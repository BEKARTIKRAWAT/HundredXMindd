# Add at the top with other imports
from backend.feedback_db import init_feedback_db
import sqlite3
import json
DB_FEEDBACK_PATH = "D:/HUNDREDXMIND/data/feedback.db"
# Append this inside the existing /ask endpoint, after generating answer but before returning
# We'll replace the current /ask function with an enhanced version that stores feedback.
# Since modifying the existing function directly may cause duplication, we'll create a new helper and modify the endpoint.
# Simpler: add a new endpoint /ask_with_feedback that stores feedback.
# But to minimize changes, we'll update the existing /ask function.
# We'll do a targeted replacement: find the existing @app.post("/ask") function and replace it.
# I'll provide a clean version of the enhanced /ask endpoint.
