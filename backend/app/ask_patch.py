# Modified /ask endpoint with web search fallback
@app.post("/ask")
@limiter.limit("5/minute")
def ask(request: Request, query: QueryRequest, use_web: bool = False):
    try:
        docs = vectorstore.similarity_search(query.question, k=3)
        # Check if documents are relevant (simple heuristic: if first doc has distance > some threshold, treat as irrelevant)
        relevant_docs = [doc for doc in docs if doc.metadata.get("score", 1.0) < 1.2]  # approximate
        # If explicit web search requested or no relevant docs and question suggests live data, use web
        question_lower = query.question.lower()
        needs_web = use_web or ("latest" in question_lower or "today" in question_lower or "current" in question_lower or "news" in question_lower)
        if relevant_docs and not needs_web:
            qa = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True
            )
            result = qa.invoke({"query": query.question})
            answer = result["result"]
            sources = [doc.metadata.get("source", "unknown") for doc in result["source_documents"]]
            return {"question": query.question, "answer": answer, "route": "docs", "sources": list(set(sources))}
        else:
            # Use web search
            web_results = web_search(query.question, max_results=3)
            if web_results:
                context = "\n".join([f"{r['title']}: {r['body']}" for r in web_results])
                prompt = f"Answer the question using the following web search results. Cite sources.\n\nQuestion: {query.question}\n\nWeb Results:\n{context}\n\nAnswer:"
                answer = llm.invoke(prompt)
                sources = [r['href'] for r in web_results]
                return {"question": query.question, "answer": answer, "route": "web", "sources": list(set(sources))}
            else:
                # Fallback to direct LLM
                answer = llm.invoke(query.question)
                return {"question": query.question, "answer": answer, "route": "llm", "sources": []}
    except Exception as e:
        logger.error(f"Error in /ask: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
