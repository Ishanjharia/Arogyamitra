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

def analyze_symptoms(symptoms_text, language, health_context=None, user_role="Patient"):
    try:
        client = get_gemini_client()
        
        health_info = ""
        if health_context:
            health_info = f"\n\nIMPORTANT PATIENT INFORMATION:\n{health_context}\n\nConsider this health profile when analyzing symptoms. Pay special attention to:\n- Any allergies when suggesting treatments\n- Existing chronic conditions that might be related\n- Current medications that might interact or cause side effects\n- Lifestyle factors that could be relevant\n\n"
        
        if user_role == "Patient":
            system_instruction = (
                f"You are an AI medical assistant analyzing patient symptoms. The patient is describing symptoms in {language}. "
                f"{health_info}"
                "Generate a structured medical report with the following sections in JSON format: "
                "1) 'symptoms_summary': Brief, easy-to-understand summary (2-3 sentences max) "
                "2) 'possible_conditions': List of 2-4 possible conditions using simple terms (not a diagnosis) "
                "3) 'severity_level': Low, Medium, or High "
                "4) 'recommendations': 3-5 simple, actionable health tips the patient can follow at home "
                "5) 'urgent_care_needed': true or false "
                "6) 'when_to_see_doctor': Clear guidance on when to seek medical help "
                "7) 'allergy_warnings': Any warnings based on patient allergies (empty list if none) "
                "8) 'condition_considerations': How existing conditions might affect this (empty string if none) "
                "9) 'disclaimer': 'This is not a medical diagnosis. Please consult a doctor for proper evaluation.' "
                "Use simple, everyday language. Avoid medical jargon. Be reassuring but honest about severity. "
                "Respond with valid JSON only."
            )
        else:
            system_instruction = (
                f"You are an AI clinical decision support system. Analyzing symptoms described in {language}. "
                f"{health_info}"
                "Generate a comprehensive clinical assessment in JSON format: "
                "1) 'symptoms_summary': Detailed symptom characterization with onset, duration, quality, severity "
                "2) 'possible_conditions': Comprehensive differential diagnosis list with ICD-10 codes where applicable "
                "3) 'severity_level': Low, Medium, High, or Critical with clinical reasoning "
                "4) 'recommendations': Evidence-based treatment protocols and clinical pathways "
                "5) 'urgent_care_needed': true or false with clinical justification "
                "6) 'follow_up_questions': Targeted clinical history questions for differential narrowing "
                "7) 'suggested_diagnostics': Recommended laboratory tests, imaging, or procedures "
                "8) 'red_flags': Critical symptoms requiring immediate attention "
                "9) 'allergy_warnings': Drug allergy considerations for treatment planning "
                "10) 'condition_considerations': Comorbidity interactions and management considerations "
                "11) 'references': Relevant clinical guidelines or literature "
                "Use proper medical terminology. Be thorough and precise. "
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

def medical_chat_response(message, language, user_role, health_context=None, severity_level=None):
    def _chat():
        client = get_gemini_client()
        
        health_info = ""
        if health_context and user_role == "Patient":
            health_info = f"\n\nPatient Health Profile:\n{health_context}\n\nUse this information to provide personalized responses. Consider their allergies, existing conditions, and current medications when giving advice.\n\n"
        
        severity_guidance = ""
        if severity_level:
            if severity_level in ["High", "Critical"]:
                severity_guidance = "IMPORTANT: This appears to be a high-severity situation. Strongly emphasize seeking immediate medical attention. Be direct about urgency while remaining calm. "
            elif severity_level == "Medium":
                severity_guidance = "This is a moderate concern. Recommend scheduling a doctor visit soon. Provide helpful interim guidance. "
        
        system_instruction = ""
        if user_role == "Patient":
            system_instruction = (
                f"You are a compassionate AI health assistant helping patients in {language}. "
                f"{health_info}"
                f"{severity_guidance}"
                "RESPONSE GUIDELINES FOR PATIENTS:\n"
                "- Keep responses SHORT and SIMPLE (2-4 paragraphs max)\n"
                "- Use everyday language, avoid medical jargon\n"
                "- Focus on practical, actionable advice\n"
                "- Include safety warnings prominently\n"
                "- ALWAYS recommend consulting a doctor for serious concerns\n"
                "- Be empathetic, warm, and reassuring\n"
                "- If allergies/conditions are on file, warn about relevant precautions\n"
                "- End with a clear next step the patient can take\n"
                "- Include disclaimer: 'This is not medical advice. Please consult a doctor.'"
            )
        else:
            system_instruction = (
                f"You are an AI clinical assistant helping doctors in {language}. "
                "RESPONSE GUIDELINES FOR DOCTORS:\n"
                "- Provide DETAILED, comprehensive medical information\n"
                "- Use proper medical terminology and classifications (ICD codes if relevant)\n"
                "- Include differential diagnoses with reasoning\n"
                "- Cite evidence-based guidelines and research when applicable\n"
                "- Discuss mechanism of action, pharmacokinetics where relevant\n"
                "- Include contraindications, drug interactions, dosing considerations\n"
                "- Provide clinical decision support with risk stratification\n"
                "- Suggest relevant diagnostic tests and their interpretation\n"
                "- Reference treatment protocols and clinical pathways\n"
                "- Be thorough and precise - doctors need complete information"
            )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=2048 if user_role == "Doctor" else 1024
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
