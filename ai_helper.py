# ai_helper.py
# =========================================================
# AROGYAMITRA — Gemini AI Helper (FINAL, STABLE VERSION)
# =========================================================

import os
import json
import time
import streamlit as st
import google.generativeai as genai

# =========================================================
# 🔑 API KEY (Railway + Streamlit compatible)
# =========================================================

def get_gemini_api_key():
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY")

GEMINI_API_KEY = get_gemini_api_key()

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")

genai.configure(api_key=GEMINI_API_KEY)

# =========================================================
# ⚙️ GLOBAL SETTINGS
# =========================================================

MODEL_FAST = "gemini-1.5-flash"
MODEL_PRO = "gemini-1.5-pro"

MAX_RETRIES = 3
RETRY_DELAY = 2

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
    "ਪੰਜਾਬੀ (Punjabi)": "pa",
}

# =========================================================
# 🔁 RETRY WRAPPER
# =========================================================

def with_retry(func):
    for attempt in range(MAX_RETRIES):
        try:
            return func()
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                raise e

# =========================================================
# 🌐 TRANSLATION
# =========================================================

def translate_text(text, source_language, target_language):
    def _run():
        model = genai.GenerativeModel(MODEL_FAST)
        prompt = (
            f"You are a professional medical translator.\n"
            f"Translate the following text from {source_language} to {target_language}.\n"
            f"Keep medical terms accurate.\n\n{text}"
        )
        response = model.generate_content(prompt)
        return {"success": True, "translation": response.text}

    try:
        return with_retry(_run)
    except Exception as e:
        return {"success": False, "translation": None, "error": str(e)}

# =========================================================
# 🩺 SYMPTOM ANALYSIS
# =========================================================

def analyze_symptoms(symptoms_text, language, health_context=None, user_role="Patient"):
    def _run():
        model = genai.GenerativeModel(
            MODEL_PRO if user_role == "Doctor" else MODEL_FAST
        )

        context = f"\nPatient Context:\n{health_context}\n" if health_context else ""

        prompt = (
            f"You are an AI medical assistant.\n"
            f"Language: {language}\n"
            f"{context}\n"
            f"Symptoms:\n{symptoms_text}\n\n"
            f"Respond ONLY in valid JSON with:\n"
            f"- symptoms_summary\n"
            f"- possible_conditions (list)\n"
            f"- severity_level (Low/Medium/High/Critical)\n"
            f"- recommendations (list)\n"
            f"- urgent_care_needed (true/false)\n"
            f"- follow_up_questions (list)\n"
            f"- disclaimer"
        )

        response = model.generate_content(prompt)
        data = json.loads(response.text)
        data["success"] = True
        return data

    try:
        return with_retry(_run)
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "symptoms_summary": "Unable to analyze symptoms",
            "possible_conditions": [],
            "severity_level": "Unknown",
            "recommendations": [],
            "urgent_care_needed": False,
            "follow_up_questions": [],
            "disclaimer": "This is not medical advice.",
        }

# =========================================================
# 💬 MEDICAL CHAT
# =========================================================

def medical_chat_response(message, language, user_role, health_context=None, severity_level=None):
    def _run():
        model = genai.GenerativeModel(MODEL_FAST)

        context = f"\nPatient Context:\n{health_context}\n" if health_context else ""
        severity = f"\nSeverity: {severity_level}\n" if severity_level else ""

        prompt = (
            f"You are a medical AI assistant.\n"
            f"User Role: {user_role}\n"
            f"Language: {language}\n"
            f"{context}{severity}\n"
            f"User Message:\n{message}\n\n"
            f"Respond clearly, safely, and responsibly."
        )

        response = model.generate_content(prompt)
        return {"success": True, "response": response.text}

    try:
        return with_retry(_run)
    except Exception as e:
        return {"success": False, "response": None, "error": str(e)}

# =========================================================
# 🎤 AUDIO TRANSCRIPTION
# =========================================================

def transcribe_audio(audio_file_path):
    def _run():
        model = genai.GenerativeModel(MODEL_FAST)

        with open(audio_file_path, "rb") as f:
            audio_bytes = f.read()

        response = model.generate_content(
            [
                {"mime_type": "audio/wav", "data": audio_bytes},
                "Transcribe this audio accurately.",
            ]
        )
        return {"success": True, "transcription": response.text}

    try:
        return with_retry(_run)
    except Exception as e:
        return {"success": False, "transcription": None, "error": str(e)}

# =========================================================
# 📝 PRESCRIPTION TRANSLATION
# =========================================================

def generate_prescription_translation(text, doctor_language, patient_language):
    return translate_text(text, doctor_language, patient_language)

# =========================================================
# 🏥 HOSPITAL SEARCH (AI GENERATED)
# =========================================================

def find_nearby_hospitals(city, specialty=None, language="English"):
    def _run():
        model = genai.GenerativeModel(MODEL_FAST)
        spec = f" specializing in {specialty}" if specialty else ""

        prompt = (
            f"List 5 hospitals{spec} near {city}, India.\n"
            f"Return valid JSON array with name, address, phone, specialties."
        )

        response = model.generate_content(prompt)
        hospitals = json.loads(response.text)
        return {"success": True, "hospitals": hospitals}

    try:
        return with_retry(_run)
    except Exception as e:
        return {"success": False, "hospitals": [], "error": str(e)}
