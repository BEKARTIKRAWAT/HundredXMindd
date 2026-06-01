from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import time
import logging
import base64
import requests
import shutil
import os
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("hundredxmind")
# ... (existing code for metrics, rate limiter, etc.) ...
# For brevity, I'll show only the additions; but you should merge.
# (Assume existing app and middleware are already defined above)
# Vision endpoint using LLaVA
@app.post("/vision")
@limiter.limit("5/minute")
async def vision(request: Request, file: UploadFile = File(...), question: str = Form("What is in this image?")):
    try:
        # Read image and convert to base64
        contents = await file.read()
        img_b64 = base64.b64encode(contents).decode("utf-8")
        # Call Ollama LLaVA
        ollama_url = "http://localhost:11434/api/generate"
        payload = {
            "model": "llava:13b",
            "prompt": question,
            "images": [img_b64],
            "stream": False
        }
        response = requests.post(ollama_url, json=payload, timeout=120)
        if response.status_code == 200:
            answer = response.json().get("response", "No response")
            return {"question": question, "answer": answer}
        else:
            raise HTTPException(status_code=500, detail="Vision model error")
    except Exception as e:
        logger.error(f"Vision error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
# Root endpoint (already there)
# Metrics endpoint (already there)
# /ask endpoint (already there)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
