from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import time
import logging
import base64
import requests
import tempfile
import os
import uuid
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from faster_whisper import WhisperModel
from web_search import web_search
from memory import get_conversation_history, add_to_history
# ---------- Logging ----------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("hundredxmind")
# ---------- Prometheus ----------
REQUESTS = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
ERRORS = Counter('http_errors_total', 'Total HTTP errors', ['method', 'endpoint', 'error_type'])
# ---------- Rate limiter ----------
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="HundredxMind AI Assistant", version="3.3.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# ---------- Metrics middleware ----------
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    method = request.method
    endpoint = request.url.path
    REQUESTS.labels(method=method, endpoint=endpoint).inc()
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
        logger.info(f"{method} {endpoint} - {response.status_code} - {duration:.3f}s")
        return response
    except Exception as e:
        ERRORS.labels(method=method, endpoint=endpoint, error_type=type(e).__name__).inc()
        logger.error(f"{method} {endpoint} - Error: {str(e)}")
        raise
# ---------- Root ----------
@app.get("/")
def root():
    return {"message": "HundredxMind AI Assistant running. Use /ask, /ask_hybrid, /vision, /voice, /metrics"}
# ---------- Metrics ----------
@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
# ---------- RAG setup ----------
CHROMA_PATH = "D:/HUNDREDXMIND/data/chroma_db"
EMBEDDING_MODEL = "nomic-embed-text:latest"
LLM_MODEL = "llama3.2:latest"
embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
llm = Ollama(model=LLM_MODEL)
class QueryRequest(BaseModel):
    question: str
# ---------- Original /ask ----------
@app.post("/ask")
@limiter.limit("20/minute")
def ask(request: Request, query: QueryRequest):
    try:
        docs = vectorstore.similarity_search(query.question, k=3)
        if docs:
            qa = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True
            )
            result = qa.invoke({"query": query.question})
            answer = result["result"]
            sources = [doc.metadata.get("source", "unknown") for doc in result["source_documents"]]
            return {"question": query.question, "answer": answer, "route": "docs", "sources": list(set(sources))}
        else:
            answer = llm.invoke(query.question)
            return {"question": query.question, "answer": answer, "route": "llm", "sources": []}
    except Exception as e:
        logger.error(f"Error in /ask: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
# ---------- Hybrid /ask_hybrid (Web Search + Memory) ----------
@app.post("/ask_hybrid")
@limiter.limit("20/minute")
def ask_hybrid(request: Request, query: QueryRequest, session_id: str = None, use_web: bool = False):
    sid = session_id or str(uuid.uuid4())
    history = get_conversation_history(sid)
    context_str = ""
    for turn in history[-5:]:
        context_str += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n"
    full_question = query.question
    if context_str:
        full_question = f"Previous conversation:\n{context_str}\nUser: {query.question}\nAssistant:"
    try:
        docs = vectorstore.similarity_search(query.question, k=3)
        question_lower = query.question.lower()
        needs_web = use_web or any(word in question_lower for word in ["latest", "today", "current", "news", "weather", "recent", "2025", "2026"])
        if not needs_web and docs:
            qa = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True
            )
            result = qa.invoke({"query": full_question})
            answer = result["result"]
            sources = [doc.metadata.get("source", "unknown") for doc in result["source_documents"]]
            add_to_history(sid, query.question, answer)
            return {"question": query.question, "answer": answer, "route": "docs", "sources": list(set(sources)), "session_id": sid}
        else:
            web_results = web_search(query.question, max_results=3)
            if web_results:
                context = "\n".join([f"- {r['title']}: {r['body']} (Source: {r['href']})" for r in web_results])
                prompt = f"Previous conversation:\n{context_str}\nUser question: {query.question}\nWeb results:\n{context}\nAnswer:"
                answer = llm.invoke(prompt)
                sources = [r['href'] for r in web_results]
                add_to_history(sid, query.question, answer)
                return {"question": query.question, "answer": answer, "route": "web", "sources": sources, "session_id": sid}
            else:
                print("\\n[DEBUG] Prompt for LLM:", full_question, "\\n"); answer = llm.invoke(full_question)
                add_to_history(sid, query.question, answer)
                return {"question": query.question, "answer": answer, "route": "llm", "sources": [], "session_id": sid}
    except Exception as e:
        logger.error(f"Hybrid error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
# ---------- Vision ----------
@app.post("/vision")
@limiter.limit("20/minute")
async def vision(request: Request, file: UploadFile = File(...), question: str = Form("What is in this image?")):
    try:
        contents = await file.read()
        img_b64 = base64.b64encode(contents).decode()
        payload = {"model": "llava:13b", "prompt": question, "images": [img_b64], "stream": False}
        resp = requests.post("http://localhost:11434/api/generate", json=payload, timeout=300)
        if resp.status_code == 200:
            answer = resp.json().get("response", "No answer")
            return {"question": question, "answer": answer}
        else:
            raise HTTPException(status_code=500, detail="Vision model error")
    except Exception as e:
        logger.error(f"Vision error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
# ---------- Voice ----------
whisper_model = None
def get_whisper_model():
    global whisper_model
    if whisper_model is None:
        whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    return whisper_model
@app.post("/voice")
@limiter.limit("20/minute")
async def voice(request: Request, file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        model = get_whisper_model()
        segments, _ = model.transcribe(tmp_path, beam_size=5)
        transcribed_text = " ".join([segment.text for segment in segments])
        os.unlink(tmp_path)
        return {"transcribed_text": transcribed_text.strip()}
    except Exception as e:
        logger.error(f"Voice error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
@app.post("/memory_test")
def memory_test(session_id: str = None):
    sid = session_id or str(uuid.uuid4())
    history = get_conversation_history(sid)
    if not history:
        return {"session_id": sid, "history": []}
    last = history[-1]
    return {"session_id": sid, "last_user": last["user"], "last_assistant": last["assistant"]}
@app.post("/ask_memory_only")
@limiter.limit("20/minute")
def ask_memory_only(request: Request, query: QueryRequest, session_id: str = None):
    sid = session_id or str(uuid.uuid4())
    history = get_conversation_history(sid)
    prompt = ""
    if history:
        prompt += "Conversation history:\n"
        for turn in history[-5:]:
            prompt += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n"
        prompt += "\n"
    prompt += f"User: {query.question}\nAssistant:"
    answer = llm.invoke(prompt)
    add_to_history(sid, query.question, answer)
    return {"question": query.question, "answer": answer, "session_id": sid}
@app.post("/ask_memory_only")
@limiter.limit("20/minute")
def ask_memory_only(request: Request, query: QueryRequest, session_id: str = None):
    sid = session_id or str(uuid.uuid4())
    history = get_conversation_history(sid)
    prompt = ""
    if history:
        prompt += "Conversation history:\n"
        for turn in history[-5:]:
            prompt += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n"
        prompt += "\n"
    prompt += f"User: {query.question}\nAssistant:"
    answer = llm.invoke(prompt)
    add_to_history(sid, query.question, answer)
    return {"question": query.question, "answer": answer, "session_id": sid}
# ---------- Action Agent (Task Automation) ----------
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from action_agent import run_action_agent
class ActionRequest(BaseModel):
    user_id: str
    instruction: str
@app.post("/action")
@limiter.limit("10/minute")
async def action_endpoint(request: Request, action_req: ActionRequest):
    try:
        result = run_action_agent(action_req.user_id, action_req.instruction)
        return {"user_id": action_req.user_id, "instruction": action_req.instruction, "result": result}
    except Exception as e:
        logger.error(f"Action agent error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
# ---------- Streaming Endpoint (Server‑Sent Events) ----------
from fastapi.responses import StreamingResponse
import httpx
async def stream_llm(question: str):
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                "http://localhost:11434/api/generate",
                json={"model": "llama3.2:latest", "prompt": question, "stream": True}
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        # Each line is a JSON object from Ollama
                        yield f"data: {line}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
@app.post("/ask_stream")
@limiter.limit("10/minute")
async def ask_stream(request: Request, query: QueryRequest):
    return StreamingResponse(stream_llm(query.question), media_type="text/event-stream")
# ---------- Agent Swarm Endpoint (LangGraph) ----------
from agents.agent_swarm_langgraph import run_swarm
class SwarmRequest(BaseModel):
    task: str
@app.post("/swarm")
@limiter.limit("10/minute")
async def swarm_endpoint(request: Request, swarm_req: SwarmRequest):
    try:
        result = run_swarm(swarm_req.task)
        return {"task": swarm_req.task, "answer": result, "route": "swarm"}
    except Exception as e:
        logger.error(f"Swarm error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
# ---------- Hierarchical Swarm Endpoint ----------
from agents.hierarchical_swarm import run_hierarchical_swarm
class HierarchicalRequest(BaseModel):
    objective: str
@app.post("/hierarchical_swarm")
@limiter.limit("10/minute")
async def hierarchical_swarm_endpoint(request: Request, req: HierarchicalRequest):
    try:
        result = run_hierarchical_swarm(req.objective)
        return {"objective": req.objective, "answer": result, "route": "hierarchical_swarm"}
    except Exception as e:
        logger.error(f"Hierarchical swarm error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
# ---------- Omni-Modal Endpoint (Text + Image + Voice) ----------
from fastapi import File, UploadFile, Form
from omni import omni_process
class OmniRequest(BaseModel):
    text: str
@app.post("/omni")
@limiter.limit("10/minute")
async def omni_endpoint(
    request: Request,
    text: str = Form(...),
    image: UploadFile = File(None),
    audio: UploadFile = File(None)
):
    try:
        image_bytes = await image.read() if image else None
        audio_bytes = await audio.read() if audio else None
        result = omni_process(text, image_bytes, audio_bytes)
        return {"text": text, "answer": result, "route": "omni"}
    except Exception as e:
        logger.error(f"Omni error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
# ---------- ReAct Planning Endpoint ----------
from agents.planning import hierarchical_plan
class PlanRequest(BaseModel):
    task: str
    depth: int = 2
@app.post("/plan")
@limiter.limit("10/minute")
async def plan_endpoint(request: Request, req: PlanRequest):
    try:
        result = hierarchical_plan(req.task, req.depth)
        return {"task": req.task, "plan": result, "route": "react_plan"}
    except Exception as e:
        logger.error(f"Planning error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
# ---------- Feedback-Enabled Endpoint ----------
class AskFeedbackRequest(BaseModel):
    question: str
    feedback_score: int = None  # 1-5
@app.post("/ask_feedback")
@limiter.limit("10/minute")
def ask_feedback(request: Request, req: AskFeedbackRequest):
    try:
        docs = vectorstore.similarity_search(req.question, k=3)
        if docs:
            qa = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True
            )
            result = qa.invoke({"query": req.question})
            answer = result["result"]
            sources = [doc.metadata.get("source", "unknown") for doc in result["source_documents"]]
            route = "docs"
        else:
            answer = llm.invoke(req.question)
            sources = []
            route = "llm"
        # Store feedback if score provided
        if req.feedback_score is not None:
            conn = sqlite3.connect(DB_FEEDBACK_PATH)
            conn.execute(
                "INSERT INTO feedback (question, answer, route, sources, score) VALUES (?, ?, ?, ?, ?)",
                (req.question, answer, route, json.dumps(sources), req.feedback_score)
            )
            conn.commit()
            conn.close()
        return {"question": req.question, "answer": answer, "route": route, "sources": list(set(sources))}
    except Exception as e:
        logger.error(f"Ask feedback error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
from apscheduler.schedulers.background import BackgroundScheduler
from self_improve import self_improve_task
import atexit
# Start background scheduler for self‑improvement (runs every hour)
scheduler = BackgroundScheduler()
scheduler.add_job(self_improve_task, 'interval', hours=1, id='self_improve_job')
scheduler.start()
# Shutdown scheduler on exit
atexit.register(lambda: scheduler.shutdown())
# Enhanced /ask with self‑improvement prompts
def load_prompt_overrides():
    if PROMPT_OVERRIDE_FILE.exists():
        with open(PROMPT_OVERRIDE_FILE, "r") as f:
            return f.read()
    return ""
@app.post("/ask_advanced")
@limiter.limit("10/minute")
def ask_advanced(request: Request, query: QueryRequest):
    try:
        docs = vectorstore.similarity_search(query.question, k=3)
        overrides = load_prompt_overrides()
        if overrides:
            extra_instruction = f"\nAdditional guidelines from previous improvements: {overrides}\n"
        else:
            extra_instruction = ""
        if docs:
            qa = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True
            )
            # Inject extra instruction into the prompt via the QA chain's prompt template
            # This requires modifying the chain; simpler: replace the llm call with a custom prompt
            # For brevity, we add the instruction to the question itself
            modified_question = query.question + extra_instruction
            result = qa.invoke({"query": modified_question})
            answer = result["result"]
            sources = [doc.metadata.get("source", "unknown") for doc in result["source_documents"]]
            return {"question": query.question, "answer": answer, "route": "docs", "sources": list(set(sources))}
        else:
            modified_question = query.question + extra_instruction
            answer = llm.invoke(modified_question)
            return {"question": query.question, "answer": answer, "route": "llm", "sources": []}
    except Exception as e:
        logger.error(f"Advanced ask error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
# ---------- Graph-RAG Endpoint ----------
from graph_rag import query_graph, add_document_entities, G
@app.post("/graph_query")
@limiter.limit("10/minute")
async def graph_query(request: Request, query: QueryRequest):
    try:
        answer = query_graph(query.question)
        return {"question": query.question, "answer": answer, "route": "graph"}
    except Exception as e:
        logger.error(f"Graph error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
# ---------- Graph-RAG Endpoint (Neo4j) ----------
from neo4j_graph import graph
@app.post("/graph_neo4j")
@limiter.limit("10/minute")
async def graph_neo4j(request: Request, query: QueryRequest):
    try:
        answer = graph.query(query.question)
        return {"question": query.question, "answer": answer, "route": "graph_neo4j"}
    except Exception as e:
        logger.error(f"Graph error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
# ---------- Neo4j Graph-RAG Endpoint ----------
from graph_rag_neo4j import graph_neo
@app.post("/graph_neo")
@limiter.limit("10/minute")
async def graph_neo_endpoint(request: Request, query: QueryRequest):
    try:
        answer = graph_neo.query(query.question)
        return {"question": query.question, "answer": answer, "route": "neo4j_graph"}
    except Exception as e:
        logger.error(f"Neo4j error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
# ---------- Multi-modal Output Endpoints ----------
from multimodal_gen import generate_image, generate_speech
class ImageRequest(BaseModel):
    prompt: str
class SpeechRequest(BaseModel):
    text: str
@app.post("/generate_image")
@limiter.limit("5/minute")
async def generate_image_endpoint(request: Request, req: ImageRequest):
    try:
        out_path = generate_image(req.prompt)
        return {"prompt": req.prompt, "image_path": out_path}
    except Exception as e:
        logger.error(f"Image gen error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/generate_speech")
@limiter.limit("10/minute")
async def generate_speech_endpoint(request: Request, req: SpeechRequest):
    try:
        out_path = generate_speech(req.text)
        return {"text": req.text, "audio_path": out_path}
    except Exception as e:
        logger.error(f"Speech gen error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
# ---------- Code Interpreter Endpoint ----------
from code_sandbox import run_python_code
class CodeRequest(BaseModel):
    code: str
@app.post("/execute_code")
@limiter.limit("5/minute")
async def execute_code_endpoint(request: Request, req: CodeRequest):
    try:
        output = run_python_code(req.code)
        return {"code": req.code, "output": output}
    except Exception as e:
        logger.error(f"Code execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
# ---------- Real‑time Collaboration (WebSockets) ----------
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
manager = ConnectionManager()
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast message to all connected clients
            await manager.broadcast(f"User: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
