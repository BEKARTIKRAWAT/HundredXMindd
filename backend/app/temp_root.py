@app.get("/")
def root():
    return {"message": "HundredxMind AI Assistant is running. Use /ask to ask questions, /metrics for Prometheus stats."}
