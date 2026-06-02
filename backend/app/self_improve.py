import sqlite3
import json
import logging
from langchain_community.llms import Ollama
from pathlib import Path
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("self_improve")
DB_PATH = Path("D:/HUNDREDXMIND/data/feedback.db")
PROMPT_OVERRIDE_FILE = Path("D:/HUNDREDXMIND/data/prompt_override.txt")
llm = Ollama(model="llama3.2:latest")
def get_low_rated_feedback(min_score=2, limit=5):
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, question, answer, route, sources FROM feedback WHERE score <= ? ORDER BY created_at DESC LIMIT ?",
        (min_score, limit)
    ).fetchall()
    conn.close()
    return rows
def analyze_and_suggest_improvement(row):
    prompt = f"""
You are an AI improvement system. A user gave a low rating for this answer.
Question: {row['question']}
Answer: {row['answer']}
Route: {row['route']}
Sources: {row['sources']}
Analyze why the answer might be poor and suggest ONE specific improvement to the system (e.g., "add more context about X", "rephrase the prompt to ask for citations", "use web search for recent data").
Output only the improvement suggestion, no extra text.
"""
    suggestion = llm.invoke(prompt).strip()
    return suggestion
def apply_improvement(suggestion):
    # For now, we append the suggestion to a prompt override file
    with open(PROMPT_OVERRIDE_FILE, "a") as f:
        f.write(f"- {suggestion}\n")
    logger.info(f"Applied improvement: {suggestion[:100]}...")
def self_improve_task():
    logger.info("Running self‑improvement scan...")
    low_feedback = get_low_rated_feedback()
    if not low_feedback:
        logger.info("No low‑rated feedback found.")
        return
    for row in low_feedback:
        suggestion = analyze_and_suggest_improvement(row)
        if suggestion:
            apply_improvement(suggestion)
    logger.info("Self‑improvement completed.")
if __name__ == "__main__":
    self_improve_task()
