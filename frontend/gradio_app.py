import gradio as gr
import requests
import json
# API endpoint (adjust if needed)
API_URL = "http://127.0.0.1:8000/ask"
def ask_question(question, history):
    if not question:
        return ""
    try:
        response = requests.post(API_URL, json={"question": question}, timeout=60)
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "No answer")
            sources = data.get("sources", [])
            if sources:
                answer += f"\n\n📚 **Sources:** {', '.join(sources)}"
            return answer
        elif response.status_code == 429:
            return "❌ Rate limit exceeded. Please wait a moment."
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Connection error: {e}"
# Gradio interface
with gr.Blocks(title="HundredxMind AI Assistant", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🧠 HundredxMind AI Assistant
    ### Multi-Agent RAG | Self-Evaluation | Human-in-the-Loop
    Ask questions based on your documents. The system retrieves context, evaluates its own answer, and can request approval.
    """)
    chatbot = gr.Chatbot(height=500)
    msg = gr.Textbox(label="Your question", placeholder="Type your question here...")
    clear = gr.Button("Clear")
    def respond(message, chat_history):
        bot_message = ask_question(message, chat_history)
        chat_history.append((message, bot_message))
        return "", chat_history
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)
    gr.Markdown("---\n✅ **Features:** RAG citations | Multi-agent orchestration | Self-evaluation | Rate limiting | Observability metrics")
if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=8502)
