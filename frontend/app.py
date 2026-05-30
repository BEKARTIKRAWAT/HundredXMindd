import streamlit as st
import requests
import json
# Page config
st.set_page_config(page_title="HundredxMind AI Assistant", page_icon="🧠", layout="wide")
st.title("🧠 HundredxMind AI Assistant")
st.caption("Multi-Agent RAG | Self-Evaluation | Human-in-the-Loop | Enterprise Ready")
# Sidebar for config
with st.sidebar:
    st.header("⚙️ Configuration")
    api_url = st.text_input("API URL", value="http://127.0.0.1:8000/ask")
    st.markdown("---")
    st.markdown("### Features Active")
    st.success("✅ RAG with Citations")
    st.success("✅ Multi-Agent Orchestration")
    st.success("✅ Self-Evaluation (LLM Judge)")
    st.success("✅ Human-in-the-Loop Approval")
    st.success("✅ Rate Limiting (5/min)")
    st.success("✅ Observability (Metrics)")
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sources" in msg:
            st.caption(f"📚 Sources: {', '.join(msg['sources'])}")
# Chat input
if prompt := st.chat_input("Ask me anything from your documents..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    # Call API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(api_url, json={"question": prompt}, timeout=60)
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No answer")
                    sources = data.get("sources", [])
                    st.markdown(answer)
                    if sources:
                        st.caption(f"📚 Sources: {', '.join(sources)}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                elif response.status_code == 429:
                    st.error("❌ Rate limit exceeded. Please wait a moment.")
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"Connection error: {e}")
# Footer
st.markdown("---")
st.caption("🚀 Powered by Ollama (Llama 3.2), LangGraph, ChromaDB, FastAPI")
