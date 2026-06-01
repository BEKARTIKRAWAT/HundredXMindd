import base64
import tempfile
import os
import subprocess
from faster_whisper import WhisperModel
from langchain_community.llms import Ollama
llm = Ollama(model="llama3.2:latest")
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
def transcribe_audio(audio_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        tmp_path = f.name
    segments, _ = whisper_model.transcribe(tmp_path, beam_size=5)
    text = " ".join([seg.text for seg in segments])
    os.unlink(tmp_path)
    return text
def describe_image(image_bytes: bytes, question: str = "What is in this image?") -> str:
    # Save image temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
        f.write(image_bytes)
        img_path = f.name
    # Use subprocess to run ollama with the image
    try:
        # Ollama CLI command: ollama run llava:7b "What is in this image?" --image path
        # Note: --image flag may not be supported on all Windows versions; fallback to stdin?
        # Actually newer Ollama supports `--image` flag.
        result = subprocess.run(
            ["ollama", "run", "llava:7b", question, "--image", img_path],
            capture_output=True,
            text=True,
            timeout=120
        )
        os.unlink(img_path)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Image analysis error: {result.stderr}"
    except Exception as e:
        os.unlink(img_path)
        return f"Image analysis failed: {str(e)}"
def omni_process(text_prompt: str, image_bytes: bytes = None, audio_bytes: bytes = None) -> str:
    context = []
    if audio_bytes:
        transcribed = transcribe_audio(audio_bytes)
        context.append(f"User said (audio): {transcribed}")
    if image_bytes:
        image_desc = describe_image(image_bytes, text_prompt if text_prompt else "Describe this image")
        context.append(f"Image description: {image_desc}")
    if text_prompt:
        context.append(f"User asked: {text_prompt}")
    combined = "\n".join(context)
    final_prompt = f"You are an omni-modal assistant. Use all provided information to answer.\n{combined}\nAnswer concisely:"
    return llm.invoke(final_prompt)
