# 🧠 HundredxMind – Ultimate Enterprise AI Assistant
**100% free, production-grade, multi-agent RAG with human-in-the-loop, self-evaluation, rate limiting, and observability.**
[![GitHub stars](https://img.shields.io/github/stars/BEKARTIKRAWAT/HundredXMindd)](https://github.com/BEKARTIKRAWAT/HundredXMindd/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
## ✨ Features
- **RAG (Retrieval Augmented Generation)** – answers grounded in your documents with citations  
- **Multi‑agent orchestration** (LangGraph) – Planner → Retriever → Analyst → Decision → Evaluation → HITL  
- **Self‑evaluation** (LLM judge) – scores each answer, auto‑retry on low score  
- **Human‑in‑the‑Loop** – approval step before final answer  
- **Adaptive routing** – automatically uses docs (if relevant) else direct LLM  
- **Rate limiting** (5/min) – prevents abuse  
- **Prometheus metrics** – /metrics endpoint for monitoring  
- **100% local & free** – runs on Ollama (Llama 3.2), no API costs  
## 🚀 Quick Start
### 1. Clone & setup
\\\ash
git clone https://github.com/BEKARTIKRAWAT/HundredXMindd.git
cd HundredXMindd
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 on Windows
pip install -r backend/requirements.txt
\\\
### 2. Pull models & ingest documents
\\\ash
ollama pull llama3.2:latest
ollama pull nomic-embed-text:latest
# Place your PDF/TXT files in data/raw/
python backend/ingest.py
\\\
### 3. Start the server
\\\ash
cd backend/app
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
\\\
### 4. Ask a question (another terminal)
\\\ash
python -c "import requests; print(requests.post('http://127.0.0.1:8000/ask', json={'question':'What is RAG?'}).json())"
\\\
### 5. Run multi-agent HITL demo
\\\ash
cd backend/agents
python test_hitl.py
\\\
Type \y\ when asked to approve the answer.
### 6. View metrics
Open \http://127.0.0.1:8000/metrics\ in your browser.
## 🏗️ Architecture
\\\mermaid
graph TD
    User --> FastAPI
    FastAPI --> Router{Adaptive Router}
    Router -->|docs| Retriever[Vector Store]
    Router -->|llm| LLM[Ollama Llama 3.2]
    Retriever --> LLM
    LLM -->|answer + sources| FastAPI
    FastAPI --> User
\\\
Multi-agent graph (LangGraph):  
\Planner → Retriever → Analyst → Decision → Evaluation → HITL → END\
## 📦 Deployment
- **Docker Compose** included – \docker compose up --build -d\  
- **Oracle Cloud Always Free** – follow [guide](./docs/oracle-deploy.md)
## 📄 License
MIT © [BEKARTIKRAWAT](https://github.com/BEKARTIKRAWAT)
## 🎥 Demo Video
[Watch demo](https://youtu.be/2ugJJ7xLSS4)


## 🚀 Advanced Capabilities

- **Action Agent** – Manage to‑do lists, reminders, and soon emails/calendar.
- **Real‑time Streaming** – Token‑by‑token responses via `/ask_stream`.
- **Web Search** – Live answers with DuckDuckGo.
- **Long‑term Memory** – Session‑based conversation recall.
- **Multi‑modal** – Vision (image Q&A) + Voice (speech‑to‑text).

## 🚀 Advanced Features

- **Advanced RAG** – Hybrid search (vector + BM25) – `/ask_advanced`
- **GraphRAG** – Entity extraction and relation mapping – `/graph_ingest`, `/graph_query`
- **Voice** – Speech‑to‑text (file upload) – `/voice` | Text‑to‑speech – `/speak`
- **Multi‑model routing** – `/ask_routed`
- **Agent swarm** – `/advanced_swarm`
- **Tool calling** – calculator, file reader, web search – `/call_tool`
- **JWT authentication** – register, login, refresh, logout
- **React frontend** – chat interface, login, settings
