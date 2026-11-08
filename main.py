# python main.py

import speech_recognition as sr
import pyttsx3 #https://pyttsx3.readthedocs.io/en/latest/engine.html (pyttsx3 documentation)
import logging
import os
import datetime
import webbrowser
import wikipedia

#This is logger for the application
LOG_DIR = "logs"
LOG_FILE_NAME = "application.log"

os.makedirs(LOG_DIR, exist_ok=True)

log_path = os.path.join(LOG_DIR, LOG_FILE_NAME)

logging.basicConfig(filename=log_path, 
                    format = "[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s", 
                    level = logging.INFO)

def text_to_sound(text):
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    # print(voices) # two list
    engine.setProperty('voice', voices[1].id) # Two types of voice: male and female. taking the male voice from the system.
    engine.say(text)
    engine.runAndWait()

def sound_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        print("Recognising...")
        querry = r.recognize_google(audio, language="en-in")
        print(f"User said: {querry}")
    except Exception as e:
        logging.info(e)
        print("Say that again please")
        return "None"
    return querry

def greetings():
    hour = datetime.datetime.now().hour
    if hour>= 0 and hour <12:
        text_to_sound("Good Morning Sir!")
    elif hour >= 12 and hour <18:
        text_to_sound("Good Afternoon Sir!")
    else:
        text_to_sound("Good Evening Sir!")
    text_to_sound("Hey how are you? Tell me how can I help you?")

greetings()
while True:
    text = sound_to_text().lower()
    text_to_sound(text)

    if "time" in text:
        time = datetime.datetime.now().strftime("%H:%M:%S")
        text_to_sound(f"The time is {time}")

    elif "exit" in text:
        text_to_sound("Okay! Good bye sir.")
        exit()

    elif "open google" in text:
        text_to_sound("Okay sir! Please search whatever you want to read.")
        webbrowser.open("google.com")

    elif "wikipedia" in text:
        text_to_sound("Searching Wikipedia")
        text = text.replace("wikipedia", "")
        results = wikipedia.summary(text, sentences=2)
        text_to_sound("According to Wikipedia.")
        print(results)
        text_to_sound(results)