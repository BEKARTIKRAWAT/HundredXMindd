import ollama
import base64
image_path = "test_image.jpg"
with open(image_path, "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")
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
