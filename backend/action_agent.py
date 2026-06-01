from langchain_community.llms import Ollama
from task_manager import add_task, list_tasks, complete_task
import re
llm = Ollama(model="llama3.2:latest")
def parse_and_execute(user_id: str, instruction: str) -> str:
    # Step 1: Use a simple keyword + regex match (faster and more reliable than LLM parsing for this demo)
    instruction_lower = instruction.lower()
    # Add task: "remind me to X at Y" or "add task X"
    if "remind" in instruction_lower or "add task" in instruction_lower:
        # Extract description
        patterns = [
            r"remind me to (.+?)(?: at |$)",
            r"add task (.+)"
        ]
        desc = None
        for pat in patterns:
            match = re.search(pat, instruction, re.IGNORECASE)
            if match:
                desc = match.group(1).strip()
                break
        if not desc:
            desc = instruction
        # Extract due time if any
        due_match = re.search(r"at (\d{1,2}(?::\d{2})?\s?(?:am|pm)?)", instruction, re.IGNORECASE)
        due = due_match.group(1) if due_match else None
        return add_task(user_id, desc, due)
    # List tasks
    elif "list my tasks" in instruction_lower or "what are my tasks" in instruction_lower:
        return list_tasks(user_id)
    # Complete task: "complete task 3"
    elif "complete task" in instruction_lower:
        match = re.search(r"complete task (\d+)", instruction_lower)
        if match:
            task_id = int(match.group(1))
            return complete_task(user_id, task_id)
        return "? Please specify the task number. Example: 'complete task 3'"
    else:
        return "I can only manage tasks (add, list, complete). Please rephrase."
def run_action_agent(user_id: str, instruction: str) -> str:
    return parse_and_execute(user_id, instruction)
