@app.post("/ask_hybrid")
@limiter.limit("5/minute")
def ask_hybrid(request: Request, query: QueryRequest, session_id: str = None, use_web: bool = False):
    sid = session_id or str(uuid.uuid4())
    history = get_conversation_history(sid)
    # Build conversation context for LLM
    history_text = ""
    for turn in history[-5:]:
        history_text += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n"
    # Full prompt with history
    if history_text:
        full_question = f"Conversation history:\n{history_text}\nCurrent user question: {query.question}\nAssistant:"
    else:
        full_question = query.question
    try:
        # Check if we need web search
        question_lower = query.question.lower()
        needs_web = use_web or any(word in question_lower for word in ["latest", "today", "current", "news", "weather", "recent", "2025", "2026"])
        if needs_web:
            web_results = web_search(query.question, max_results=3)
            if web_results:
                context = "\n".join([f"- {r['title']}: {r['body']} (Source: {r['href']})" for r in web_results])
                prompt = f"{history_text}\nUser question: {query.question}\nWeb results:\n{context}\nAssistant:"
                answer = llm.invoke(prompt)
                sources = [r['href'] for r in web_results]
                add_to_history(sid, query.question, answer)
                return {"question": query.question, "answer": answer, "route": "web", "sources": sources, "session_id": sid}
        # Default: use RAG if relevant docs exist
        docs = vectorstore.similarity_search(query.question, k=3)
        if docs:
            qa = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True
            )
            result = qa.invoke({"query": full_question})
            answer = result["result"]
            sources = [doc.metadata.get("source", "unknown") for doc in result["source_documents"]]
            add_to_history(sid, query.question, answer)
            return {"question": query.question, "answer": answer, "route": "docs", "sources": list(set(sources)), "session_id": sid}
        else:
            # Direct LLM with history
            answer = llm.invoke(full_question)
            add_to_history(sid, query.question, answer)
            return {"question": query.question, "answer": answer, "route": "llm", "sources": [], "session_id": sid}
    except Exception as e:
        logger.error(f"Hybrid error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
