from typing import TypedDict, List, Dict
from langchain_community.llms import Ollama
llm = Ollama(model="llama3.2:latest")
class MasterState(TypedDict):
    objective: str
    plan: List[str]
    results: Dict[str, str]
    final_answer: str
def master_supervisor(state: MasterState):
    prompt = f"""
    You are a master supervisor. Break down the following objective into 2-4 concrete sub‑tasks.
    Return only a numbered list of sub‑tasks, nothing else.
    Objective: {state['objective']}
    """
    response = llm.invoke(prompt)
    subtasks = [line.strip() for line in response.split('\n') if line.strip() and line[0].isdigit()]
    return {"plan": subtasks}
def research_worker(task: str) -> str:
    prompt = f"Research the following topic and provide a concise, factual answer: {task}"
    return llm.invoke(prompt)
def writing_worker(task: str) -> str:
    prompt = f"Write or summarize based on the following task: {task}"
    return llm.invoke(prompt)
def route_task(task: str) -> str:
    task_lower = task.lower()
    if "research" in task_lower or "find" in task_lower or "what is" in task_lower:
        return "research"
    else:
        return "writing"
def aggregator(objective: str, results: Dict[str, str]) -> str:
    combined = "\n".join([f"- {k}: {v}" for k, v in results.items()])
    prompt = f"Based on the following results, produce a final answer to the original objective:\nOriginal: {objective}\nResults:\n{combined}"
    return llm.invoke(prompt)
def run_hierarchical_swarm(objective: str) -> str:
    # Get plan
    state = {"objective": objective, "plan": [], "results": {}, "final_answer": ""}
    plan_result = master_supervisor(state)
    subtasks = plan_result["plan"]
    results = {}
    for idx, task in enumerate(subtasks):
        worker_type = route_task(task)
        if worker_type == "research":
            res = research_worker(task)
        else:
            res = writing_worker(task)
        results[f"task_{idx+1}"] = res
    final = aggregator(objective, results)
    return final
