import sqlite3
from pathlib import Path
DB_PATH = Path("D:/HUNDREDXMIND/data/feedback.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
def init_feedback_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            route TEXT,
            sources TEXT,
            score INTEGER,  -- 1 to 5 (1=bad, 5=excellent)
            user_feedback TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS retry_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            original_answer TEXT,
            improved_answer TEXT,
            improvement_trigger TEXT,  -- "low_score" or "user_feedback"
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
init_feedback_db()
print("Feedback database initialized.")
