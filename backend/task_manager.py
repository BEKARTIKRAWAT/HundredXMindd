import sqlite3
import datetime
import json
from pathlib import Path
DB_PATH = Path("D:/HUNDREDXMIND/data/tasks.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                description TEXT NOT NULL,
                due_time TEXT,
                completed BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
init_db()
def add_task(user_id: str, description: str, due_time: str = None) -> str:
    with get_db() as conn:
        conn.execute(
            "INSERT INTO tasks (user_id, description, due_time) VALUES (?, ?, ?)",
            (user_id, description, due_time)
        )
        conn.commit()
    return f"✅ Task added: '{description}'" + (f" (due {due_time})" if due_time else "")
def list_tasks(user_id: str) -> str:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, description, due_time, completed FROM tasks WHERE user_id = ? AND completed = 0 ORDER BY due_time NULLS LAST",
            (user_id,)
        ).fetchall()
    if not rows:
        return "You have no pending tasks."
    tasks_str = "\n".join([f"{r['id']}. {r['description']}" + (f" (due {r['due_time']})" if r['due_time'] else "") for r in rows])
    return f"📋 Your pending tasks:\n{tasks_str}"
def complete_task(user_id: str, task_id: int) -> str:
    with get_db() as conn:
        cur = conn.execute("UPDATE tasks SET completed = 1 WHERE id = ? AND user_id = ?", (task_id, user_id))
        conn.commit()
        if cur.rowcount:
            return f"✅ Task {task_id} marked as completed."
        else:
            return f"❌ Task {task_id} not found."
