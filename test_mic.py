import speech_recognition as sr
recognizer = sr.Recognizer()
with sr.Microphone() as source:
    print("Adjusting for ambient noise...")
    recognizer.adjust_for_ambient_noise(source, duration=1)
    print("Say something...")
    try:
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)
        print("Audio captured, recognizing...")
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
    except sr.WaitTimeoutError:
        print("No speech detected within timeout.")
    except sr.UnknownValueError:
        print("Could not understand the audio.")
    except Exception as e:
        print(f"Error: {e}")
