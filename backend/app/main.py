from fastapi import FastAPI, HTTPException, Request
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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("hundredxmind")
REQUESTS = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
ERRORS = Counter('http_errors_total', 'Total HTTP errors', ['method', 'endpoint', 'error_type'])
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="HundredxMind AI Assistant", version="2.6.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
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
@app.get("/")
def root():
    return {"message": "HundredxMind AI Assistant is running. Use POST /ask to ask questions, GET /metrics for Prometheus stats."}
@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
CHROMA_PATH = "D:/HUNDREDXMIND/data/chroma_db"
EMBEDDING_MODEL = "nomic-embed-text:latest"
LLM_MODEL = "llama3.2:latest"
embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
llm = Ollama(model=LLM_MODEL)
class QueryRequest(BaseModel):
    question: str
@app.post("/ask")
@limiter.limit("5/minute")
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
            return {
                "question": query.question,
                "answer": answer,
                "route": "docs",
                "sources": list(set(sources))
            }
        else:
            answer = llm.invoke(query.question)
            return {
                "question": query.question,
                "answer": answer,
                "route": "llm",
                "sources": []
            }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
