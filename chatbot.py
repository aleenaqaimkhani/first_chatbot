import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from gtts import gTTS
import base64
import tempfile
from io import BytesIO
from PyPDF2 import PdfReader

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash-8b")

# Language mapping for TTS
language_codes = {
    "English": "en",
    "Urdu": "ur",
    "Hindi": "hi",
    "Arabic": "ar",
    "French": "fr",
    "Spanish": "es",
    "Chinese": "zh-CN",
    "Russian": "ru",
    "Turkish": "tr"
}

st.set_page_config(page_title="📘 CSS MindMap", layout="centered")
st.title("📘 CSS MindMap")

st.markdown("""
This chatbot is specially designed for CSS (Central Superior Services) aspirants. You can ask any question related to CSS, and it will provide accurate answers based on authentic PDF content. Whether you need a brief explanation or a detailed one, simply choose your preference and language. It’s a smart, interactive assistant to help guide you through your CSS preparation with both text and audio support.
""")


# Sidebar selections with unique keys
selected_language = st.sidebar.selectbox("Select Answer Language", list(language_codes.keys()), key="language_selector")
answer_length = st.sidebar.radio("Answer Length", ["Short", "Detailed"], key="answer_length")

# Extract text from fixed PDF
@st.cache_data
def extract_pdf_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content
    return text

pdf_text = extract_pdf_text("converted_text.pdf")  # <-- Your static PDF file

# TTS Function
def text_to_speech(text, lang):
    try:
        tts = gTTS(text=text, lang=lang)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:            
            tts.save(fp.name)
            audio_path = fp.name
        return audio_path
    except Exception as e:
        st.error(f"TTS Error: {e}")
        return None

# Chat history container
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Ask a question
user_question = st.text_input("Ask a Question :", key="question_input")


# Generate response
if user_question:
    prompt = f"""
You are an educational assistant. Use the following textbook content to answer the question.

Textbook Content:
{pdf_text}

Now, give a {answer_length.lower()} explanation in {selected_language} for this question:
{user_question}
"""
    try:
        response = model.generate_content(prompt)
        answer = response.text

        # Show and speak answer
        st.markdown(f"**Answer:**\n{answer}")
        
        # Show download button
        st.download_button(
            label="📩 Download Answer (Text)",
            data=answer,
            file_name="css_answer.txt",
            mime="text/plain"
            
        )
        lang_code = language_codes.get(selected_language, "en")
        audio_file = text_to_speech(answer, lang_code)
        if audio_file:
            audio_bytes = open(audio_file, 'rb').read()
            st.audio(audio_bytes, format='audio/mp3')

           

        # Save to chat history
        st.session_state.chat_history.append((user_question, answer))

    except Exception as e:
        st.error(f"Error: {e}")

# Display chat history
if st.session_state.chat_history:
    with st.expander("🕘 Chat History"):
        for i, (q, a) in enumerate(reversed(st.session_state.chat_history)):
            st.markdown(f"**Q{i+1}:** {q}")
            st.markdown(f"**A{i+1}:** {a}")
