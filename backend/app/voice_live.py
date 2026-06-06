import speech_recognition as sr
import pyttsx3
import threading
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()
def listen_once() -> str:
    with sr.Microphone() as source:
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return ""
def speak(text: str):
    tts_engine.say(text)
    tts_engine.runAndWait()
