import subprocess
import base64
import json
# Path to image
image_path = "test_image.jpg"
# Read and encode image as base64
with open(image_path, "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode("utf-8")
# Create prompt for Ollama CLI
# Ollama CLI can accept base64 image via stdin or temp file; simpler: use curl directly to API
import requests
url = "http://localhost:11434/api/generate"
payload = {
    "model": "llava:13b",
    "prompt": "What is in this image?",
    "images": [image_b64],
    "stream": False
}
response = requests.post(url, json=payload)
if response.status_code == 200:
    print(response.json()["response"])
else:
    print("Error:", response.status_code, response.text)
