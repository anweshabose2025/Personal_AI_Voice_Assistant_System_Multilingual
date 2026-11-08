# streamlit run main1.py

import speech_recognition as sr
import os
import pyttsx3
#from gtts import gTTS
import logging
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("GROQ_API"),
    base_url="https://api.groq.com/openai/v1",
)

def text_to_sound(text):
    print(text)
    #ttx = gTTS(text=text, lang="en")
    #ttx.save("speech.mp3")
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    ## print(voices) # two list
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

def groq_model(user_input):
    response = client.responses.create(input=user_input,model="openai/gpt-oss-20b")
    results = response.output_text
    return results

def main():
     st.title("Multilingual AI Voice Assistant")
     st.header("Hey there! I am your AI Assistant. Tell me how can I help you today?")
     text_to_sound("Hey there! I am your AI Assistant. Tell me how can I help you today?")
     if st.button("Ask me anything"):
          with st.spinner("Listening..."):
               text = sound_to_text()
               st.write(text)
               llm_response = groq_model(text.lower())
               st.text_area(label="Response:", value=llm_response, height=350)
               text_to_sound(llm_response)
main()

#while True:
#text = sound_to_text().lower()
#text_to_sound(groq_model(text))
#if "exit" in text:
#        text_to_sound("Okay! Good bye sir.")
#        exit()

