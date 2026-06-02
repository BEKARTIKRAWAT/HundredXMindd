import requests
from gtts import gTTS
from urllib.parse import quote
def generate_image(prompt: str, output_path: str = "generated_image.png"):
    # Pollinations.ai – free, fast, no API key required
    url = f"https://image.pollinations.ai/prompt/{quote(prompt)}"
    response = requests.get(url, timeout=30)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        return output_path
    else:
        return f"Error: {response.status_code}"
def generate_speech(text: str, output_path: str = "generated_speech.mp3"):
    tts = gTTS(text, lang="en")
    tts.save(output_path)
    return output_path
