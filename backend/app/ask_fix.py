def ask_hybrid(request: Request, query: QueryRequest, session_id: str = None, use_web: bool = False):
    sid = session_id or str(uuid.uuid4())
    history = get_conversation_history(sid)
    # Build a clear prompt including history
    prompt = ""
    if history:
        prompt += "Previous conversation:\n"
        for turn in history[-3:]:  # last 3 exchanges
            prompt += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n"
        prompt += "\nNow answer the following question, using the previous conversation if relevant.\n"
    prompt += f"User: {query.question}\nAssistant:"
    try:
        # Simple direct LLM call for testing memory
        answer = llm.invoke(prompt)
        add_to_history(sid, query.question, answer)
        return {"question": query.question, "answer": answer, "route": "memory_test", "session_id": sid}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
