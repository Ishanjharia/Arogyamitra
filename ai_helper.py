import os
import json
import time
import streamlit as st
import google.generativeai as genai

# ===============================
# Gemini API Key Loader
# ===============================

def get_gemini_api_key():
    # 1. Try environment variable FIRST (Railway, Docker, Prod)
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return api_key

    # 2. Try Streamlit secrets ONLY if available
    try:
        import streamlit as st
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

    return None

# ===============================
# Constants
# ===============================
MODEL_NAME = "models/gemini-pro"
MAX_RETRIES = 3
RETRY_DELAY = 2

GEMINI_API_KEY = get_gemini_api_key()

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")

genai.configure(api_key=GEMINI_API_KEY)

SUPPORTED_LANGUAGES = {
    "English": "en",
    "हिंदी (Hindi)": "hi",
    "मराठी (Marathi)": "mr",
    "தமிழ் (Tamil)": "ta",
    "తెలుగు (Telugu)": "te",
    "বাংলা (Bengali)": "bn",
    "ગુજરાતી (Gujarati)": "gu",
    "ಕನ್ನಡ (Kannada)": "kn",
    "മലയാളം (Malayalam)": "ml",
    "ਪੰਜਾਬੀ (Punjabi)": "pa"
}

# ===============================
# Retry Wrapper
# ===============================
def call_with_retry(func):
    for attempt in range(MAX_RETRIES):
        try:
            return func()
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                raise e

# ===============================
# Symptom Analysis
# ===============================
def analyze_symptoms(
    symptoms_text,
    language="English",
    health_context=None,
    user_role="Patient"
):

    def _run():
        model = genai.GenerativeModel(MODEL_NAME)
        
        context_block = ""
        if health_context:
            context_block = f"\nPatient Health Context:\n{health_context}\n"

            
        prompt = f"""
You are a medical AI assistant.

Language: {language}
User role: {user_role}

User symptoms:
{symptoms_text}

Rules:
- This is NOT a diagnosis
- Use simple language
- Be safe and cautious
- Encourage doctor visit if needed

Respond in JSON with:
- symptoms_summary
- possible_conditions
- severity_level
- recommendations
- urgent_care_needed
"""

        response = model.generate_content(prompt)
        return response.text

    try:
        text = call_with_retry(_run)
        return {
            "success": True,
            "response": text,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "response": None,
            "error": str(e)
        }

# ===============================
# Translation
# ===============================
def translate_text(text, source_language, target_language):
    def _run():
        model = genai.GenerativeModel(MODEL_NAME)

        prompt = f"""
Translate the following medical text
from {source_language} to {target_language}.

Text:
{text}

Only provide the translation.
"""
        response = model.generate_content(prompt)
        return response.text

    try:
        translated = call_with_retry(_run)
        return {
            "success": True,
            "translation": translated,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "translation": None,
            "error": str(e)
        }

# ===============================
# Medical Chat
# ===============================
def medical_chat_response(message, language="English"):
    def _run():
        model = genai.GenerativeModel(MODEL_NAME)

        prompt = f"""
You are a helpful medical assistant.

Language: {language}

Message:
{message}

Rules:
- Be clear and calm
- No diagnosis
- Suggest doctor when appropriate
"""
        response = model.generate_content(prompt)
        return response.text

    try:
        reply = call_with_retry(_run)
        return {
            "success": True,
            "response": reply,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "response": None,
            "error": str(e)
        }
