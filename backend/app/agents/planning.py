from langchain_community.llms import Ollama
import re
llm = Ollama(model="llama3.2:1b")
def plan_task(task: str) -> list:
    prompt = f"""You are a planner. Break down the task into numbered steps.
Task: {task}
Output each step as a simple sentence. Start each step with a number and a period.
Example:
1. Boil water.
2. Add tea bag.
3. Steep for 3 minutes.
"""
    response = llm.invoke(prompt)
    steps = []
    for line in response.split('\n'):
        line = line.strip()
        if re.match(r'^\d+\.', line):
            steps.append({"reason": line, "act": line})
    if not steps:
        steps = [{"reason": "Could not plan", "act": "Default action"}]
    return steps
def hierarchical_plan(task: str, depth: int = 1) -> dict:
    return {"level1": plan_task(task)}
