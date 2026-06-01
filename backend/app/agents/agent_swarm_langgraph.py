from langgraph.graph import StateGraph, END
from langchain_community.llms import Ollama
from typing import TypedDict, List, Annotated
import operator
llm = Ollama(model="llama3.2:latest")
class SwarmState(TypedDict):
    task: str
    subtasks: Annotated[List[str], operator.add]
    results: Annotated[List[str], operator.add]
    final_answer: str
def decomposer(state: SwarmState):
    """Break the main task into 2-3 simpler subtasks."""
    prompt = f"Break down the following task into 2-3 simple, independent subtasks. Return as numbered list:\n{state['task']}"
    response = llm.invoke(prompt)
    subtasks = [line.strip() for line in response.split('\n') if line.strip() and line[0].isdigit()]
    return {"subtasks": subtasks}
def worker_1(state: SwarmState):
    """First worker agent."""
    if len(state["subtasks"]) > 0:
        subtask = state["subtasks"][0]
        result = llm.invoke(f"Perform this subtask: {subtask}")
        return {"results": [result]}
    return {"results": []}
def worker_2(state: SwarmState):
    """Second worker agent."""
    if len(state["subtasks"]) > 1:
        subtask = state["subtasks"][1]
        result = llm.invoke(f"Perform this subtask: {subtask}")
        return {"results": [result]}
    return {"results": []}
def worker_3(state: SwarmState):
    """Third worker agent (if needed)."""
    if len(state["subtasks"]) > 2:
        subtask = state["subtasks"][2]
        result = llm.invoke(f"Perform this subtask: {subtask}")
        return {"results": [result]}
    return {"results": []}
def aggregator(state: SwarmState):
    """Combine all results into a final answer."""
    combined = "\n".join(state["results"])
    prompt = f"Combine the following results into a single, coherent final answer:\n{combined}"
    final = llm.invoke(prompt)
    return {"final_answer": final}
# Build graph
builder = StateGraph(SwarmState)
builder.add_node("decomposer", decomposer)
builder.add_node("worker_1", worker_1)
builder.add_node("worker_2", worker_2)
builder.add_node("worker_3", worker_3)
builder.add_node("aggregator", aggregator)
builder.set_entry_point("decomposer")
builder.add_edge("decomposer", "worker_1")
builder.add_edge("worker_1", "worker_2")
builder.add_edge("worker_2", "worker_3")
builder.add_edge("worker_3", "aggregator")
builder.add_edge("aggregator", END)
graph = builder.compile()
def run_swarm(task: str) -> str:
    initial = SwarmState(task=task, subtasks=[], results=[], final_answer="")
    result = graph.invoke(initial)
    return result["final_answer"]
