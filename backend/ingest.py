import os
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
import glob
# Configuration
CHROMA_PATH = "D:/HUNDREDXMIND/data/chroma_db"
DATA_PATH = "D:/HUNDREDXMIND/data/raw"
EMBEDDING_MODEL = "nomic-embed-text:latest"
def ingest_pdf(file_path):
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    return docs
def ingest_text(file_path):
    loader = TextLoader(file_path, encoding='utf-8')
    docs = loader.load()
    return docs
def ingest_website(url):
    loader = WebBaseLoader(url)
    docs = loader.load()
    return docs
def split_documents(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    return text_splitter.split_documents(docs)
def create_vector_store(documents, persist_directory=CHROMA_PATH):
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    vectorstore.persist()
    print(f"Vector store created with {len(documents)} chunks at {persist_directory}")
    return vectorstore
def load_existing_vector_store():
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    return Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
if __name__ == "__main__":
    all_docs = []
    pdf_files = glob.glob(os.path.join(DATA_PATH, "*.pdf"))
    for pdf in pdf_files:
        print(f"Loading {pdf}...")
        docs = ingest_pdf(pdf)
        all_docs.extend(docs)
    txt_files = glob.glob(os.path.join(DATA_PATH, "*.txt"))
    for txt in txt_files:
        print(f"Loading {txt}...")
        docs = ingest_text(txt)
        all_docs.extend(docs)
    if not all_docs:
        print("No documents found. Please add PDF or TXT files to data/raw")
        exit(0)
    chunks = split_documents(all_docs)
    print(f"Split into {len(chunks)} chunks")
    create_vector_store(chunks)
