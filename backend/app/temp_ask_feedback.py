# ---------- Simplified /ask_feedback (with error logging) ----------
class AskFeedbackRequest(BaseModel):
    question: str
    feedback_score: int = None
@app.post("/ask_feedback")
@limiter.limit("10/minute")
def ask_feedback(request: Request, req: AskFeedbackRequest):
    try:
        # Get answer using RAG (reuse existing /ask logic)
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
            # Convert sources to JSON string
            sources_json = json.dumps(sources)
            conn.execute(
                "INSERT INTO feedback (question, answer, route, sources, score) VALUES (?, ?, ?, ?, ?)",
                (req.question, answer, route, sources_json, req.feedback_score)
            )
            conn.commit()
            conn.close()
            logger.info(f"Stored feedback for question: {req.question[:50]}, score={req.feedback_score}")
        return {"question": req.question, "answer": answer, "route": route, "sources": list(set(sources))}
    except Exception as e:
        logger.error(f"Ask feedback error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
