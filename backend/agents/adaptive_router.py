from langchain_ollama import OllamaLLM
router_llm = OllamaLLM(model="llama3.2:latest")
def route_query(question: str) -> str:
    prompt = f"""Classify the following user question into one of three categories:
- "docs" if it asks about internal company information (policies, products, employees, projects, internal data)
- "web" if it asks about current events, external news, real-time info, or something not in your documents
- "llm" if it's a general knowledge question, reasoning, or creative task
Return ONLY one word: docs, web, or llm.
Question: {question}
Category:"""
    result = router_llm.invoke(prompt).strip().lower()
    if result in ["docs", "web", "llm"]:
        return result
    return "llm"  # fallback
