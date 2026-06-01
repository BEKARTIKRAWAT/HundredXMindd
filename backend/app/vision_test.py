import ollama
import base64
from pathlib import Path
# Load and encode image
image_path = "test_image.jpg"
with open(image_path, "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")
# Send request to Ollama (LLaVA) through Python client
response = ollama.chat(
    model="llava:13b",
    messages=[
        {
            "role": "user",
            "content": "What is in this image?",
            "images": [image_data]
        }
    ]
)
print(response['message']['content'])
