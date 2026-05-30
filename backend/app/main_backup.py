from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_ollama import OllamaLLM
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
import os
app = FastAPI(title="HundredxMind AI Assistant - RAG Enabled", version="2.0.0")
# Paths
CHROMA_PATH = "D:/HUNDREDXMIND/data/chroma_db"
EMBEDDING_MODEL = "nomic-embed-text:latest"
LLM_MODEL = "llama3.2:latest"
# Load vector store
embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
# Load LLM
llm = OllamaLLM(model=LLM_MODEL)
# Create RAG chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    verbose=True
)
class QueryRequest(BaseModel):
    question: str
@app.get("/")
def root():
    return {"message": "HundredxMind AI Assistant with RAG is running!"}
@app.post("/ask")
def ask(request: QueryRequest):
    try:
        result = qa_chain.invoke({"query": request.question})
        answer = result["result"]
        sources = [doc.metadata.get("source", "unknown") for doc in result["source_documents"]]
        return {
            "question": request.question,
            "answer": answer,
            "sources": list(set(sources))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
