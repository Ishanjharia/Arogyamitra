import json
import os
import time
from google import genai
from google.genai import types

# IMPORTANT: KEEP THIS COMMENT
# Using Google Gemini API via blueprint:python_gemini
# Models: gemini-2.5-flash (fast, cheap) and gemini-2.5-pro (complex reasoning)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
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
    "ਪੰਜਾਬੀ (Punjabi)": "pa"
}

def validate_api_key():
    if not GEMINI_API_KEY:
        return False, "Gemini API key not configured. Please set GEMINI_API_KEY environment variable."
    return True, ""

def get_gemini_client():
    is_valid, error_msg = validate_api_key()
    if not is_valid:
        raise ValueError(error_msg)
    return genai.Client(api_key=GEMINI_API_KEY)

def call_gemini_with_retry(func):
    for attempt in range(MAX_RETRIES):
        try:
            return func()
        except Exception as e:
            error_msg = str(e)
            if "503" in error_msg or "overloaded" in error_msg.lower() or "UNAVAILABLE" in error_msg:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                else:
                    return {"success": False, "error": "The AI service is currently busy. Please try again in a moment."}
            raise e

def translate_text(text, source_language, target_language):
    def _translate():
        client = get_gemini_client()
        system_instruction = f"You are a professional medical translator. Translate the following text from {source_language} to {target_language}. Maintain medical terminology accuracy and cultural sensitivity. Only provide the translation, no explanations."
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=2048
            )
        )
        return {"success": True, "translation": response.text, "error": None}
    
    try:
        result = call_gemini_with_retry(_translate)
        if isinstance(result, dict) and not result.get("success"):
            return result
        return result
    except ValueError as e:
        return {"success": False, "translation": None, "error": str(e)}
    except Exception as e:
        return {"success": False, "translation": None, "error": f"Translation failed: {str(e)}"}

def analyze_symptoms(symptoms_text, language):
    try:
        client = get_gemini_client()
        system_instruction = (
            f"You are an AI medical assistant analyzing patient symptoms. The patient is describing symptoms in {language}. "
            "Generate a structured medical report with the following sections in JSON format: "
            "1) 'symptoms_summary': Brief summary of reported symptoms "
            "2) 'possible_conditions': List of possible conditions (not a diagnosis) "
            "3) 'severity_level': Low, Medium, or High "
            "4) 'recommendations': General health recommendations "
            "5) 'urgent_care_needed': true or false "
            "6) 'follow_up_questions': Questions a doctor should ask. "
            "Include a disclaimer that this is not a medical diagnosis. "
            "Respond with valid JSON only."
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=symptoms_text,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                max_output_tokens=2048
            )
        )
        
        result = json.loads(response.text)
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
            "recommendations": "Please configure Gemini API key to use this feature",
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
        client = get_gemini_client()
        system_instruction = (
            f"You are a medical translator specializing in prescriptions. Translate the following prescription from {doctor_language} to {patient_language}. "
            "Maintain exact medication names, dosages, and timing. Format the translation clearly with: "
            "1) Medication names (keep generic/brand names) "
            "2) Dosage and frequency "
            "3) Duration "
            "4) Special instructions "
            "5) Warnings/precautions. "
            "Use simple, clear language that patients can easily understand."
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prescription_text,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=2048
            )
        )
        return {"success": True, "translation": response.text, "error": None}
    except ValueError as e:
        return {"success": False, "translation": None, "error": str(e)}
    except Exception as e:
        return {"success": False, "translation": None, "error": f"Translation failed: {str(e)}"}

def medical_chat_response(message, language, user_role):
    def _chat():
        client = get_gemini_client()
        system_instruction = ""
        if user_role == "Patient":
            system_instruction = f"You are a compassionate AI health assistant helping patients in {language}. Provide clear, simple medical information. Always recommend consulting a doctor for serious concerns. Be empathetic and supportive."
        else:
            system_instruction = f"You are an AI assistant helping doctors with medical information in {language}. Provide evidence-based medical insights, differential diagnoses support, and clinical decision support. Cite medical knowledge when appropriate."
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=2048
            )
        )
        return {"success": True, "response": response.text, "error": None}
    
    try:
        result = call_gemini_with_retry(_chat)
        if isinstance(result, dict) and not result.get("success"):
            return result
        return result
    except ValueError as e:
        return {"success": False, "response": None, "error": str(e)}
    except Exception as e:
        return {"success": False, "response": None, "error": f"Chat failed: {str(e)}"}

def transcribe_audio(audio_file_path):
    """
    Note: Gemini supports audio transcription. We'll use gemini-2.5-flash for this.
    """
    try:
        client = get_gemini_client()
        with open(audio_file_path, "rb") as f:
            audio_bytes = f.read()
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type="audio/wav",
                ),
                "Transcribe this audio accurately. Only provide the transcription text, no explanations."
            ]
        )
        return {"success": True, "transcription": response.text, "error": None}
    except ValueError as e:
        return {"success": False, "transcription": None, "error": str(e)}
    except Exception as e:
        return {"success": False, "transcription": None, "error": f"Transcription failed: {str(e)}"}

def generate_doctor_notes(conversation_text, patient_language, doctor_language):
    try:
        client = get_gemini_client()
        system_instruction = (
            f"You are an AI medical documentation assistant. The conversation was in {patient_language}. "
            f"Generate structured clinical notes in {doctor_language} with: "
            "1) Chief Complaint "
            "2) History of Present Illness "
            "3) Symptoms Summary "
            "4) Assessment "
            "5) Suggested Plan. "
            "Use standard medical terminology and format."
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=conversation_text,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=2048
            )
        )
        return {"success": True, "notes": response.text, "error": None}
    except ValueError as e:
        return {"success": False, "notes": None, "error": str(e)}
    except Exception as e:
        return {"success": False, "notes": None, "error": f"Note generation failed: {str(e)}"}

def find_nearby_hospitals(city, specialty=None, language="English"):
    def _find():
        client = get_gemini_client()
        specialty_filter = f" specializing in {specialty}" if specialty and specialty != "All Specialties" else ""
        system_instruction = (
            f"You are a healthcare location assistant helping find hospitals in India. "
            f"Find 5-8 hospitals{specialty_filter} near {city}, India. "
            f"Respond in {language} with valid JSON only. "
            "Return a JSON array with each hospital having these fields: "
            "1) 'name': Hospital name "
            "2) 'address': Full address "
            "3) 'phone': Phone number (use realistic format like +91-XXXX-XXXXXX) "
            "4) 'specialties': Array of specialties offered "
            "5) 'distance_km': Estimated distance from city center (number) "
            "6) 'type': 'Government' or 'Private' "
            "7) 'rating': Rating out of 5 (number) "
            "8) 'emergency': true or false for 24/7 emergency services. "
            "Include a mix of government and private hospitals. Use realistic Indian hospital names and addresses."
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Find hospitals near {city}{specialty_filter}",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                max_output_tokens=4096
            )
        )
        
        hospitals = json.loads(response.text)
        return {"success": True, "hospitals": hospitals, "error": None}
    
    try:
        result = call_gemini_with_retry(_find)
        if isinstance(result, dict) and not result.get("success"):
            return result
        return result
    except ValueError as e:
        return {"success": False, "hospitals": [], "error": str(e)}
    except Exception as e:
        return {"success": False, "hospitals": [], "error": f"Hospital search failed: {str(e)}"}
