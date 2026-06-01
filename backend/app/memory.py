import diskcache
import json
cache = diskcache.Cache("D:/HUNDREDXMIND/data/memory_cache")
def get_conversation_history(session_id):
    key = f"history:{session_id}"
    if key in cache:
        return cache[key]
    return []
def add_to_history(session_id, user_msg, assistant_msg):
    key = f"history:{session_id}"
    history = get_conversation_history(session_id)
    history.append({"user": user_msg, "assistant": assistant_msg})
    if len(history) > 10:
        history = history[-10:]
    cache[key] = history
def clear_history(session_id):
    if f"history:{session_id}" in cache:
        del cache[f"history:{session_id}"]
