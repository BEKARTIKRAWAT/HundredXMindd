# ---------- Feedback-Enabled Endpoint (Corrected) ----------
class AskFeedbackRequest(BaseModel):
    question: str
    feedback_score: int = None
@app.post("/ask_feedback")
@limiter.limit("10/minute")
def ask_feedback(request: Request, req: AskFeedbackRequest):
    try:
        # Use the same RAG logic as /ask
        docs = vectorstore.similarity_search(req.question, k=3)
        if docs:
            qa = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True
            )
            result = qa.invoke({"query": req.question})
            answer = result["result"]
            sources = [doc.metadata.get("source", "unknown") for doc in result["source_documents"]]
            route = "docs"
        else:
            answer = llm.invoke(req.question)
            sources = []
            route = "llm"
        # Store feedback if score provided
        if req.feedback_score is not None:
            import sqlite3, json
            conn = sqlite3.connect("D:/HUNDREDXMIND/data/feedback.db")
            conn.execute(
                "INSERT INTO feedback (question, answer, route, sources, score) VALUES (?, ?, ?, ?, ?)",
                (req.question, answer, route, json.dumps(sources), req.feedback_score)
            )
            conn.commit()
            conn.close()
        return {"question": req.question, "answer": answer, "route": route, "sources": list(set(sources))}
    except Exception as e:
        logger.error(f"Ask feedback error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
