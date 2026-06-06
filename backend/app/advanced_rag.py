from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from rank_bm25 import BM25Okapi
import numpy as np
CHROMA_PATH = "D:/HUNDREDXMIND/data/chroma_db"
EMBEDDING_MODEL = "nomic-embed-text:latest"
embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
def hybrid_retrieve(query, k=5, alpha=0.5):
    vector_results = vectorstore.similarity_search_with_score(query, k=k*2)
    if not vector_results:
        return []
    docs = [doc for doc, _ in vector_results]
    scores = [score for _, score in vector_results]
    tokenized_corpus = [doc.page_content.lower().split() for doc in docs]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = query.lower().split()
    bm25_scores = bm25.get_scores(tokenized_query)
    if np.max(bm25_scores) > 0:
        bm25_scores = bm25_scores / np.max(bm25_scores)
    max_dist = max(scores) if scores else 1
    vector_sim = [1 - (s / max_dist) for s in scores]
    combined = [alpha * v + (1 - alpha) * b for v, b in zip(vector_sim, bm25_scores)]
    sorted_idx = np.argsort(combined)[::-1][:k]
    return [docs[i] for i in sorted_idx]
