from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import OllamaLLM
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
CHROMA_PATH = "D:/HUNDREDXMIND/data/chroma_db"
EMBEDDING_MODEL = "nomic-embed-text:latest"
LLM_MODEL = "llama3.2:latest"
class AgentState(TypedDict):
    question: str
    plan: str
    retrieved_docs: List[str]
    analysis: str
    draft_answer: str
    approved: bool
    final_answer: str
llm = OllamaLLM(model=LLM_MODEL)
embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
def planner_node(state: AgentState):
    prompt = f"Create a simple plan to answer: {state['question']}"
    return {"plan": llm.invoke(prompt)}
def retriever_node(state: AgentState):
    docs = retriever.invoke(state["question"])
    return {"retrieved_docs": [d.page_content for d in docs]}
def analyst_node(state: AgentState):
    context = "\n".join(state["retrieved_docs"])
    prompt = f"Context: {context}\nQuestion: {state['question']}\nAnswer based on context:"
    return {"analysis": llm.invoke(prompt)}
def decision_node(state: AgentState):
    draft = state["analysis"] if state["retrieved_docs"] else "No relevant info found."
    return {"draft_answer": draft}
def hitl_node(state: AgentState):
    # This node will be interrupted before execution
    # When resumed, we set approved=True and finalize answer
    return {"approved": True, "final_answer": state["draft_answer"]}
builder = StateGraph(AgentState)
builder.add_node("planner", planner_node)
builder.add_node("retriever", retriever_node)
builder.add_node("analyst", analyst_node)
builder.add_node("decision", decision_node)
builder.add_node("hitl", hitl_node)
builder.set_entry_point("planner")
builder.add_edge("planner", "retriever")
builder.add_edge("retriever", "analyst")
builder.add_edge("analyst", "decision")
builder.add_edge("decision", "hitl")
builder.add_edge("hitl", END)
# Add checkpointer to allow interruptions
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer, interrupt_before=["hitl"])
