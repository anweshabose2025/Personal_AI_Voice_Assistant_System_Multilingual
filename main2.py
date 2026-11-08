# streamlit run main2.py

import streamlit as st
import speech_recognition as sr
import os
import io
import logging

from openai import OpenAI
from dotenv import load_dotenv
from gtts import gTTS


# ==========================================
# 1. APPLICATION CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="My AI Voice Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()

logging.basicConfig(level=logging.INFO)

API_KEY = os.getenv("GROQ_API")

if not API_KEY:
    st.error("Groq API key not found. Please configure your .env file.")
    st.stop()


client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.groq.com/openai/v1"
)


# ==========================================
# 2. LANGUAGE CONFIGURATION
# ==========================================

LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Bengali": "bn",
    "Tamil": "ta",
    "Telugu": "te",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Spanish": "es",
    "French": "fr",
    "German": "de"
}


# ==========================================
# 3. SESSION STATE
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "assistant_name" not in st.session_state:
    st.session_state.assistant_name = "Nova"


# ==========================================
# 4. CUSTOM CSS
# ==========================================

st.markdown("""
<style>

.main {
    background-color: #0e1117;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.assistant-heading {
    font-size: 36px;
    font-weight: 700;
    text-align: center;
}

.assistant-subheading {
    text-align: center;
    color: #9ca3af;
    font-size: 16px;
}

.stButton button {
    border-radius: 12px;
    height: 45px;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 5. TEXT TO SPEECH
# ==========================================

def text_to_sound(text, language="en"):

    try:

        audio_file = io.BytesIO()

        tts = gTTS(
            text=text,
            lang=language
        )

        tts.write_to_fp(audio_file)

        audio_file.seek(0)

        return audio_file.getvalue()

    except Exception as e:

        logging.exception("Text to speech error")

        return None


# ==========================================
# 6. SPEECH TO TEXT
# ==========================================

def sound_to_text(audio_bytes, language=None):

    try:

        recognizer = sr.Recognizer()

        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:

            audio = recognizer.record(source)

        # Groq Whisper transcription

        audio_file = (
            "recording.wav",
            audio_bytes,
            "audio/wav"
        )

        kwargs = {
            "file": audio_file,
            "model": "whisper-large-v3-turbo",
            "response_format": "json"
        }

        if language:
            kwargs["language"] = language

        transcription = client.audio.transcriptions.create(
            **kwargs
        )

        return transcription.text.strip()

    except Exception as e:

        logging.exception("Speech recognition error")

        st.error(f"Could not recognize speech: {e}")

        return None


# ==========================================
# 7. GROQ AI MODEL
# ==========================================

def groq_model(user_input, language):

    try:

        system_prompt = f"""
        You are Nova, an intelligent and friendly
        multilingual AI voice assistant.

        Your responsibilities:

        1. Answer questions clearly and accurately.
        2. Be friendly and conversational.
        3. Keep simple answers concise.
        4. Explain technical topics step by step.
        5. Understand follow-up questions.
        6. Reply in {language}, unless the user
           explicitly requests another language.
        7. Do not repeat unnecessary information.
        """

        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

        # Keep recent conversation history

        messages.extend(
            [
                {
                    "role": msg["role"],
                    "content": msg["content"]
                }
                for msg in st.session_state.messages[-12:]
            ]
        )

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages
        )

        return response.choices[0].message.content

    except Exception as e:

        logging.exception("Groq API error")

        return f"Sorry, something went wrong: {e}"


# ==========================================
# 8. PROCESS USER MESSAGE
# ==========================================

def process_message(question, language, voice_reply):

    if not question or not question.strip():
        return

    # Save user message

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    # Generate AI response

    response = groq_model(
        question,
        language
    )

    # Generate voice response

    audio_bytes = None

    if voice_reply:

        audio_bytes = text_to_sound(
            response,
            LANGUAGES[language]
        )

    # Save assistant response

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
            "audio": audio_bytes
        }
    )

    st.rerun()


# ==========================================
# 9. SIDEBAR
# ==========================================

with st.sidebar:

    st.title("🎙️ Nova Assistant")

    st.caption("Your personal AI voice assistant")

    st.divider()

    st.subheader("Settings")

    selected_language = st.selectbox(
        "Response language",
        list(LANGUAGES.keys()),
        index=0
    )

    input_language = st.selectbox(
        "Voice input language",
        ["Auto Detect"] + list(LANGUAGES.keys()),
        index=0
    )

    voice_reply = st.toggle(
        "Enable voice responses",
        value=True
    )

    st.divider()

    st.subheader("Conversation")

    if st.button("🗑️ Clear conversation", use_container_width=True):

        st.session_state.messages = []

        st.rerun()

    st.divider()

    st.caption("Powered by Groq AI")


# ==========================================
# 10. MAIN INTERFACE
# ==========================================

st.markdown(
    '<div class="assistant-heading">🤖 Hello, I am Nova</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="assistant-subheading">'
    'Your intelligent multilingual AI voice assistant'
    '</div>',
    unsafe_allow_html=True
)

st.write("")


# ==========================================
# 11. DISPLAY CHAT HISTORY
# ==========================================

if not st.session_state.messages:

    st.info(
        "👋 Welcome! Ask me anything using text "
        "or your microphone."
    )

    st.write("### Try asking me:")

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button("Explain Python", use_container_width=True):

            process_message(
                "Explain Python programming.",
                selected_language,
                voice_reply
            )

    with col2:

        if st.button("What is AI?", use_container_width=True):

            process_message(
                "Explain Artificial Intelligence.",
                selected_language,
                voice_reply
            )

    with col3:

        if st.button("Tell me a joke", use_container_width=True):

            process_message(
                "Tell me a funny joke.",
                selected_language,
                voice_reply
            )


for index, message in enumerate(st.session_state.messages):

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant":

            if message.get("audio"):

                st.audio(
                    message["audio"],
                    format="audio/mp3"
                )


# ==========================================
# 12. TEXT INPUT
# ==========================================

user_prompt = st.chat_input(
    "Message Nova... Ask anything!"
)

if user_prompt:

    process_message(
        user_prompt,
        selected_language,
        voice_reply
    )


# ==========================================
# 13. VOICE INPUT
# ==========================================

st.divider()

st.subheader("🎤 Talk to Nova")

audio_value = st.audio_input(
    "Record your voice message"
)

if st.button(
    "🚀 Send voice message",
    use_container_width=True
):

    if audio_value is not None:

        with st.spinner("Listening and understanding your voice..."):

            language_code = None

            if input_language != "Auto Detect":

                language_code = LANGUAGES[input_language]

            spoken_text = sound_to_text(
                audio_value.getvalue(),
                language_code
            )

        if spoken_text:

            st.success(f"You said: {spoken_text}")

            process_message(
                spoken_text,
                selected_language,
                voice_reply
            )

    else:

        st.warning("Please record a voice message first.")
