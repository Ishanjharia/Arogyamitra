import json
import os
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

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

def validate_api_key():
    if not OPENAI_API_KEY:
        return False, "OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
    return True, ""

def get_openai_client():
    is_valid, error_msg = validate_api_key()
    if not is_valid:
        raise ValueError(error_msg)
    # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
    # do not change this unless explicitly requested by the user
    return OpenAI(api_key=OPENAI_API_KEY)

def translate_text(text, source_language, target_language):
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a professional medical translator. Translate the following text from {source_language} to {target_language}. Maintain medical terminology accuracy and cultural sensitivity. Only provide the translation, no explanations."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            max_completion_tokens=2048
        )
        return {"success": True, "translation": response.choices[0].message.content, "error": None}
    except ValueError as e:
        return {"success": False, "translation": None, "error": str(e)}
    except Exception as e:
        return {"success": False, "translation": None, "error": f"Translation failed: {str(e)}"}

def analyze_symptoms(symptoms_text, language):
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an AI medical assistant analyzing patient symptoms. The patient is describing symptoms in {language}. Generate a structured medical report with the following sections in JSON format: "
                    + "1) 'symptoms_summary': Brief summary of reported symptoms "
                    + "2) 'possible_conditions': List of possible conditions (not a diagnosis) "
                    + "3) 'severity_level': Low, Medium, or High "
                    + "4) 'recommendations': General health recommendations "
                    + "5) 'urgent_care_needed': true or false "
                    + "6) 'follow_up_questions': Questions a doctor should ask. "
                    + "Include a disclaimer that this is not a medical diagnosis. "
                    + "Respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": symptoms_text
                }
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=2048
        )
        result = json.loads(response.choices[0].message.content)
        result["success"] = True
        result["error"] = None
        return result
    except ValueError as e:
        return {
            "success": False,
            "error": str(e),
            "symptoms_summary": "AI service not configured",
            "possible_conditions": [],
            "severity_level": "Unknown",
            "recommendations": "Please configure OpenAI API key to use this feature",
            "urgent_care_needed": False,
            "follow_up_questions": []
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "symptoms_summary": "Error analyzing symptoms",
            "possible_conditions": [],
            "severity_level": "Unknown",
            "recommendations": "Please consult a doctor",
            "urgent_care_needed": False,
            "follow_up_questions": []
        }

def generate_prescription_translation(prescription_text, doctor_language, patient_language):
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a medical translator specializing in prescriptions. Translate the following prescription from {doctor_language} to {patient_language}. "
                    + "Maintain exact medication names, dosages, and timing. Format the translation clearly with: "
                    + "1) Medication names (keep generic/brand names) "
                    + "2) Dosage and frequency "
                    + "3) Duration "
                    + "4) Special instructions "
                    + "5) Warnings/precautions. "
                    + "Use simple, clear language that patients can easily understand."
                },
                {
                    "role": "user",
                    "content": prescription_text
                }
            ],
            max_completion_tokens=2048
        )
        return {"success": True, "translation": response.choices[0].message.content, "error": None}
    except ValueError as e:
        return {"success": False, "translation": None, "error": str(e)}
    except Exception as e:
        return {"success": False, "translation": None, "error": f"Translation failed: {str(e)}"}

def medical_chat_response(message, language, user_role):
    try:
        client = get_openai_client()
        system_prompt = ""
        if user_role == "Patient":
            system_prompt = f"You are a compassionate AI health assistant helping patients in {language}. Provide clear, simple medical information. Always recommend consulting a doctor for serious concerns. Be empathetic and supportive."
        else:
            system_prompt = f"You are an AI assistant helping doctors with medical information in {language}. Provide evidence-based medical insights, differential diagnoses support, and clinical decision support. Cite medical knowledge when appropriate."
        
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            max_completion_tokens=2048
        )
        return {"success": True, "response": response.choices[0].message.content, "error": None}
    except ValueError as e:
        return {"success": False, "response": None, "error": str(e)}
    except Exception as e:
        return {"success": False, "response": None, "error": f"Chat failed: {str(e)}"}

def transcribe_audio(audio_file_path):
    try:
        client = get_openai_client()
        with open(audio_file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return {"success": True, "transcription": response.text, "error": None}
    except ValueError as e:
        return {"success": False, "transcription": None, "error": str(e)}
    except Exception as e:
        return {"success": False, "transcription": None, "error": f"Transcription failed: {str(e)}"}

def generate_doctor_notes(conversation_text, patient_language, doctor_language):
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an AI medical documentation assistant. The conversation was in {patient_language}. Generate structured clinical notes in {doctor_language} with: "
                    + "1) Chief Complaint "
                    + "2) History of Present Illness "
                    + "3) Symptoms Summary "
                    + "4) Assessment "
                    + "5) Suggested Plan. "
                    + "Use standard medical terminology and format."
                },
                {
                    "role": "user",
                    "content": conversation_text
                }
            ],
            max_completion_tokens=2048
        )
        return {"success": True, "notes": response.choices[0].message.content, "error": None}
    except ValueError as e:
        return {"success": False, "notes": None, "error": str(e)}
    except Exception as e:
        return {"success": False, "notes": None, "error": f"Note generation failed: {str(e)}"}
