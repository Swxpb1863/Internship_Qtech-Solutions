import os
import openai
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# List of supported languages for translation
languages = [
    "English", "Hindi", "Tamil", "Telugu", "Malayalam", 
    "French", "Russian", "German", "Spanish", "Italian", 
    "Chinese", "Japanese", "Korean"
]

# Function to handle translation
def translate_text(text, source_lang, target_lang):
    prompt = f"Translate the following text from {source_lang} to {target_lang}: {text}"
    
    # Make an API request to OpenAI GPT-3.5-turbo for translation
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use the new gpt-3.5-turbo model
        messages=[
            {"role": "system", "content": "You are a helpful language translator."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=100,
    )
    
    # Extract and return the translated text
    return response['choices'][0]['message']['content'].strip()

# Streamlit UI
st.title("Language Translation with GPT-3.5")
st.write("Select the source and target languages and enter the text to translate.")

# Select source and target languages
source_language = st.selectbox("Select Source Language", languages)
target_language = st.selectbox("Select Target Language", languages)

# Input text to be translated
text = st.text_area("Enter text to translate")

# Button to trigger translation
if st.button("Translate"):
    if text:
        translated_text = translate_text(text, source_language, target_language)
        st.subheader("Translated Text")
        st.write(translated_text)
    else:
        st.error("Please enter text to translate.")
