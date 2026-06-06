from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
raw_path = "data/raw/sample.txt"
persist_dir = "data/chroma_db"
loader = TextLoader(raw_path, encoding='utf-8')
docs = loader.load()
print(f"1. Loaded {len(docs)} documents")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(docs)
print(f"2. Split into {len(chunks)} chunks")
print(f"   Preview: {chunks[0].page_content[:100]}")
embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
vec = embeddings.embed_query(chunks[0].page_content)
print(f"3. Embedding works, vector length = {len(vec)}")
vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory=persist_dir)
print(f"4. Vector store created (overwrote)")
docs_retrieved = vectorstore.similarity_search("What is RAG?", k=3)
print(f"5. Retrieved {len(docs_retrieved)} documents")
if docs_retrieved:
    print(f"   Content: {docs_retrieved[0].page_content[:200]}")
else:
    print("   No documents retrieved")
