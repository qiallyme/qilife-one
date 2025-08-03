import pyttsx3

engine = pyttsx3.init()

def speak_response(text):
    engine.say(text)
    engine.runAndWait()
