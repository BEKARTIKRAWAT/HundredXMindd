import sqlite3
import json
import subprocess
import tempfile
import os
import re
import time
from langchain_community.llms import Ollama
llm = Ollama(model="llama3.2:1b")
DB_PATH = "D:/HUNDREDXMIND/data/feedback.db"
TOOLS_DIR = "D:/HUNDREDXMIND/HundredXMindd/backend/dynamic_tools"
os.makedirs(TOOLS_DIR, exist_ok=True)
def get_recent_failures(limit=5):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT question, answer, route, sources FROM feedback WHERE score <= 2 ORDER BY created_at DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return rows
def generate_new_tool(failure):
    prompt = f"""
A user gave a low rating to this answer:
Question: {failure['question']}
Answer: {failure['answer']}
Route: {failure['route']}
Suggest a new Python function (tool) that could prevent this failure.
The function should have a clear name, docstring, and return a string.
Output ONLY the Python code, no explanation.
"""
    code = llm.invoke(prompt)
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0]
    elif "```" in code:
        code = code.split("```")[1].split("```")[0]
    return code.strip()
def validate_and_save_tool(code, name=None):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        tmp_path = f.name
    result = subprocess.run(['python', '-m', 'py_compile', tmp_path], capture_output=True)
    os.unlink(tmp_path)
    if result.returncode != 0:
        return False, result.stderr.decode()
    if not name:
        match = re.search(r"def\s+(\w+)\s*\(", code)
        name = match.group(1) if match else f"tool_{int(time.time())}"
    save_path = os.path.join(TOOLS_DIR, f"{name}.py")
    with open(save_path, 'w') as f:
        f.write(code)
    return True, save_path
def run_evolution():
    failures = get_recent_failures()
    if not failures:
        print("No failures to evolve from.")
        return
    for f in failures:
        code = generate_new_tool(f)
        ok, msg = validate_and_save_tool(code)
        if ok:
            print(f"✅ New tool saved: {msg}")
        else:
            print(f"❌ Tool generation failed: {msg}")
if __name__ == "__main__":
    run_evolution()
