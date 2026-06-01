# ---------- Voice endpoint (using faster-whisper) ----------
from faster_whisper import WhisperModel
whisper_model = None
def get_whisper_model():
    global whisper_model
    if whisper_model is None:
        whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    return whisper_model
@app.post("/voice")
@limiter.limit("5/minute")
async def voice(request: Request, file: UploadFile = File(...)):
    try:
        # Save uploaded audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        # Transcribe using faster-whisper
        model = get_whisper_model()
        segments, info = model.transcribe(tmp_path, beam_size=5)
        transcribed_text = " ".join([segment.text for segment in segments])
        os.unlink(tmp_path)  # delete temp file
        return {"transcribed_text": transcribed_text.strip()}
    except Exception as e:
        logger.error(f"Voice error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
