import operator
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
# ---------- Configuration ----------
CHROMA_PATH = "D:/HUNDREDXMIND/data/chroma_db"
EMBEDDING_MODEL = "nomic-embed-text:latest"
LLM_MODEL = "llama3.2:1b"
llm = Ollama(model=LLM_MODEL)
embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
# ---------- State ----------
class AgentState(TypedDict):
    task: str
    plan: List[str]
    research_data: Annotated[List[str], operator.add]
    critique: str
    code: str
    final_answer: str
    iteration: int
# ---------- Nodes ----------
def planner(state: AgentState):
    prompt = f"Break this task into 2-4 concrete subtasks. Return each on a new line.\nTask: {state['task']}"
    response = llm.invoke(prompt)
    subtasks = [line.strip() for line in response.split('\n') if line.strip() and line[0].isdigit()]
    if not subtasks:
        subtasks = [state['task']]
    return {"plan": subtasks}
def research(state: AgentState):
    # Use RAG for each subtask (simplified: combine all)
    all_docs = []
    for subtask in state.get("plan", [state["task"]]):
        docs = retriever.invoke(subtask)
        all_docs.extend(docs)
    # Fallback to web search if no docs
    if not all_docs:
        try:
            from backend.web_search import web_search
            results = web_search(state["task"], max_results=2)
            web_text = "\n".join([f"{r['title']}: {r['body']}" for r in results])
            all_docs = [web_text]
        except:
            all_docs = ["No information found."]
    texts = [doc.page_content if hasattr(doc, 'page_content') else str(doc) for doc in all_docs]
    return {"research_data": texts}
def critic(state: AgentState):
    research_text = "\n".join(state["research_data"])
    prompt = f"""Critique the following research for accuracy, completeness, and relevance to the task: "{state['task']}".
Research:\n{research_text}\n
Provide a short critique and suggest what is missing."""
    return {"critique": llm.invoke(prompt)}
def coder(state: AgentState):
    # Only trigger if the task asks for code
    if any(word in state["task"].lower() for word in ["code", "function", "program", "script"]):
        prompt = f"Write code to accomplish: {state['task']}\nUse Python. Return only the code block."
        return {"code": llm.invoke(prompt)}
    return {"code": ""}
def summarizer(state: AgentState):
    research_summary = "\n".join(state["research_data"])
    prompt = f"""Task: {state['task']}
Research findings:
{research_summary}
Critique: {state['critique']}
Code (if any): {state['code']}
Produce a final, polished answer that addresses the task."""
    final = llm.invoke(prompt)
    return {"final_answer": final}
def router(state: AgentState):
    # After research, go to critic, then summarizer (skip coder if not needed)
    # We'll hardcode the flow for simplicity
    return "critic"
# ---------- Build Graph ----------
builder = StateGraph(AgentState)
builder.add_node("planner", planner)
builder.add_node("research", research)
builder.add_node("critic", critic)
builder.add_node("coder", coder)
builder.add_node("summarizer", summarizer)
builder.set_entry_point("planner")
builder.add_edge("planner", "research")
builder.add_edge("research", "critic")
builder.add_edge("critic", "coder")
builder.add_edge("coder", "summarizer")
builder.add_edge("summarizer", END)
graph = builder.compile()
def run_advanced_swarm(task: str) -> str:
    initial = AgentState(task=task, plan=[], research_data=[], critique="", code="", final_answer="", iteration=0)
    result = graph.invoke(initial)
    return result["final_answer"]
