import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import ai_helper


class TranslateRequest(BaseModel):
    text: str
    source_language: str
    target_language: str


class SymptomAnalysisRequest(BaseModel):
    symptoms_text: str
    language: str
    health_context: str | None = None
    user_role: str = "Patient"


class ChatRequest(BaseModel):
    message: str
    language: str
    user_role: str
    health_context: str | None = None
    severity_level: str | None = None


class PrescriptionTranslationRequest(BaseModel):
    prescription_text: str
    doctor_language: str
    patient_language: str


class DoctorNotesRequest(BaseModel):
    conversation_text: str
    patient_language: str
    doctor_language: str


class HospitalSearchRequest(BaseModel):
    city: str
    specialty: str | None = None
    language: str = "English"


app = FastAPI(
    title="ArogyaMitra API",
    version="1.0.0",
    description="Backend for demo healthcare assistant features powered by Groq.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "ArogyaMitra API",
        "status": "ok",
        "provider": "Groq",
        "ui_note": "The original Streamlit UI remains in app.py for local/dev use. Vercel serves this FastAPI backend.",
        "routes": [
            "/translate",
            "/analyze-symptoms",
            "/chat",
            "/prescription-translation",
            "/doctor-notes",
            "/find-hospitals",
        ],
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "provider": "Groq",
        "api_key_configured": bool(os.environ.get("GROQ_API_KEY")),
        "fast_model": os.environ.get("GROQ_FAST_MODEL", "llama-3.1-8b-instant"),
        "complex_model": os.environ.get("GROQ_COMPLEX_MODEL", "llama-3.1-8b-instant"),
    }


@app.post("/translate")
def translate(payload: TranslateRequest):
    return ai_helper.translate_text(
        payload.text,
        payload.source_language,
        payload.target_language,
    )


@app.post("/analyze-symptoms")
def analyze_symptoms(payload: SymptomAnalysisRequest):
    return ai_helper.analyze_symptoms(
        payload.symptoms_text,
        payload.language,
        payload.health_context,
        payload.user_role,
    )


@app.post("/chat")
def chat(payload: ChatRequest):
    return ai_helper.medical_chat_response(
        payload.message,
        payload.language,
        payload.user_role,
        payload.health_context,
        payload.severity_level,
    )


@app.post("/prescription-translation")
def prescription_translation(payload: PrescriptionTranslationRequest):
    return ai_helper.generate_prescription_translation(
        payload.prescription_text,
        payload.doctor_language,
        payload.patient_language,
    )


@app.post("/doctor-notes")
def doctor_notes(payload: DoctorNotesRequest):
    return ai_helper.generate_doctor_notes(
        payload.conversation_text,
        payload.patient_language,
        payload.doctor_language,
    )


@app.post("/find-hospitals")
def find_hospitals(payload: HospitalSearchRequest):
    return ai_helper.find_nearby_hospitals(
        payload.city,
        payload.specialty,
        payload.language,
    )
