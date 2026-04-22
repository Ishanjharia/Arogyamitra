import json
import os
import time

import requests

# IMPORTANT: KEEP THIS COMMENT
# Using Groq's free developer API via the OpenAI-compatible chat API.

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
MAX_RETRIES = 3
RETRY_DELAY = 2
FAST_MODEL = os.environ.get("GROQ_FAST_MODEL", "llama-3.1-8b-instant")
COMPLEX_MODEL = os.environ.get("GROQ_COMPLEX_MODEL", "llama-3.1-8b-instant")

SUPPORTED_LANGUAGES = {
    "English": "en",
    "à¤¹à¤¿à¤‚à¤¦à¥€ (Hindi)": "hi",
    "à¤®à¤°à¤¾à¤ à¥€ (Marathi)": "mr",
    "à®¤à®®à®¿à®´à¯ (Tamil)": "ta",
    "à°¤à±†à°²à±à°—à± (Telugu)": "te",
    "à¦¬à¦¾à¦‚à¦²à¦¾ (Bengali)": "bn",
    "àª—à«àªœàª°àª¾àª¤à«€ (Gujarati)": "gu",
    "à²•à²¨à³à²¨à²¡ (Kannada)": "kn",
    "à´®à´²à´¯à´¾à´³à´‚ (Malayalam)": "ml",
    "à¨ªà©°à¨œà¨¾à¨¬à©€ (Punjabi)": "pa",
}


def validate_api_key():
    if not os.environ.get("GROQ_API_KEY"):
        return False, "Groq API key not configured. Please set GROQ_API_KEY."
    return True, ""


def call_groq_with_retry(func):
    for attempt in range(MAX_RETRIES):
        try:
            return func()
        except Exception as e:
            error_msg = str(e).lower()
            retryable = any(
                marker in error_msg
                for marker in ["429", "503", "overloaded", "unavailable", "rate limit", "timeout"]
            )
            if retryable and attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            if retryable:
                return {
                    "success": False,
                    "error": "The AI service is busy right now. Please try again in a moment.",
                }
            raise e


def _extract_text(message):
    if isinstance(message, dict):
        content = message.get("content", "")
    else:
        content = getattr(message, "content", "")

    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_value = item.get("text", "")
                if isinstance(text_value, dict):
                    text_value = text_value.get("value", "")
                parts.append(text_value)
            elif isinstance(item, dict) and "text" in item:
                text_value = item.get("text", "")
                if isinstance(text_value, dict):
                    text_value = text_value.get("value", "")
                parts.append(text_value)
            else:
                text_value = getattr(item, "text", None)
                if text_value:
                    parts.append(text_value)
        return "\n".join(part for part in parts if part).strip()
    return str(content).strip()


def _clean_json_payload(raw_text):
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def _chat_completion(user_content, system_instruction, model, max_output_tokens, response_format=None):
    is_valid, error_msg = validate_api_key()
    if not is_valid:
        raise ValueError(error_msg)

    request_payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_content},
        ],
        "max_tokens": max_output_tokens,
    }
    if response_format:
        request_payload["response_format"] = response_format

    response = requests.post(
        f"{GROQ_BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
            "Content-Type": "application/json",
        },
        json=request_payload,
        timeout=120,
    )
    response.raise_for_status()
    payload = response.json()
    return _extract_text(payload["choices"][0]["message"])


def _json_completion(user_content, system_instruction, model, max_output_tokens):
    raw_text = _chat_completion(
        user_content=user_content,
        system_instruction=system_instruction,
        model=model,
        max_output_tokens=max_output_tokens,
        response_format={"type": "json_object"},
    )
    return json.loads(_clean_json_payload(raw_text))


def translate_text(text, source_language, target_language):
    def _translate():
        system_instruction = (
            f"You are a professional medical translator. Translate the following text from "
            f"{source_language} to {target_language}. Maintain medical terminology accuracy and "
            "cultural sensitivity. Only provide the translation, no explanations."
        )
        translation = _chat_completion(
            user_content=text,
            system_instruction=system_instruction,
            model=FAST_MODEL,
            max_output_tokens=2048,
        )
        return {"success": True, "translation": translation, "error": None}

    try:
        result = call_groq_with_retry(_translate)
        if isinstance(result, dict) and not result.get("success"):
            return result
        return result
    except ValueError as e:
        return {"success": False, "translation": None, "error": str(e)}
    except Exception as e:
        return {"success": False, "translation": None, "error": f"Translation failed: {str(e)}"}


def analyze_symptoms(symptoms_text, language, health_context=None, user_role="Patient"):
    try:
        health_info = ""
        if health_context:
            health_info = (
                "\n\nIMPORTANT PATIENT INFORMATION:\n"
                f"{health_context}\n\n"
                "Consider this health profile when analyzing symptoms. Pay special attention to:\n"
                "- Any allergies when suggesting treatments\n"
                "- Existing chronic conditions that might be related\n"
                "- Current medications that might interact or cause side effects\n"
                "- Lifestyle factors that could be relevant\n\n"
            )

        if user_role == "Patient":
            system_instruction = (
                f"You are an AI medical assistant analyzing patient symptoms. The patient is "
                f"describing symptoms in {language}. {health_info}"
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
                f"You are an AI clinical decision support system. Analyzing symptoms described in "
                f"{language}. {health_info}"
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
                "Use proper medical terminology. Be thorough and precise. Respond with valid JSON only."
            )

        result = _json_completion(
            user_content=symptoms_text,
            system_instruction=system_instruction,
            model=COMPLEX_MODEL,
            max_output_tokens=2048,
        )
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
            "recommendations": "Please configure GROQ_API_KEY to use this feature",
            "urgent_care_needed": False,
            "follow_up_questions": [],
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
            "follow_up_questions": [],
        }


def generate_prescription_translation(prescription_text, doctor_language, patient_language):
    try:
        system_instruction = (
            f"You are a medical translator specializing in prescriptions. Translate the following "
            f"prescription from {doctor_language} to {patient_language}. "
            "Maintain exact medication names, dosages, and timing. Format the translation clearly with: "
            "1) Medication names (keep generic/brand names) "
            "2) Dosage and frequency "
            "3) Duration "
            "4) Special instructions "
            "5) Warnings/precautions. "
            "Use simple, clear language that patients can easily understand."
        )
        translation = _chat_completion(
            user_content=prescription_text,
            system_instruction=system_instruction,
            model=FAST_MODEL,
            max_output_tokens=2048,
        )
        return {"success": True, "translation": translation, "error": None}
    except ValueError as e:
        return {"success": False, "translation": None, "error": str(e)}
    except Exception as e:
        return {"success": False, "translation": None, "error": f"Translation failed: {str(e)}"}


def medical_chat_response(message, language, user_role, health_context=None, severity_level=None):
    def _chat():
        health_info = ""
        if health_context and user_role == "Patient":
            health_info = (
                "\n\nPatient Health Profile:\n"
                f"{health_context}\n\n"
                "Use this information to provide personalized responses. Consider their allergies, "
                "existing conditions, and current medications when giving advice.\n\n"
            )

        severity_guidance = ""
        if severity_level:
            if severity_level in ["High", "Critical"]:
                severity_guidance = (
                    "IMPORTANT: This appears to be a high-severity situation. Strongly emphasize "
                    "seeking immediate medical attention. Be direct about urgency while remaining calm. "
                )
            elif severity_level == "Medium":
                severity_guidance = (
                    "This is a moderate concern. Recommend scheduling a doctor visit soon. "
                    "Provide helpful interim guidance. "
                )

        if user_role == "Patient":
            system_instruction = (
                f"You are a compassionate AI health assistant helping patients in {language}. "
                f"{health_info}{severity_guidance}"
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
            max_output_tokens = 1024
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
            max_output_tokens = 2048

        response_text = _chat_completion(
            user_content=message,
            system_instruction=system_instruction,
            model=FAST_MODEL,
            max_output_tokens=max_output_tokens,
        )
        return {"success": True, "response": response_text, "error": None}

    try:
        result = call_groq_with_retry(_chat)
        if isinstance(result, dict) and not result.get("success"):
            return result
        return result
    except ValueError as e:
        return {"success": False, "response": None, "error": str(e)}
    except Exception as e:
        return {"success": False, "response": None, "error": f"Chat failed: {str(e)}"}


def transcribe_audio(audio_file_path):
    _ = audio_file_path
    return {
        "success": False,
        "transcription": None,
        "error": (
            "Audio transcription is disabled in the free demo setup. "
            "Use text input for the demo, or add a separate speech-to-text service later."
        ),
    }


def generate_doctor_notes(conversation_text, patient_language, doctor_language):
    try:
        system_instruction = (
            f"You are an AI medical documentation assistant. The conversation was in "
            f"{patient_language}. Generate structured clinical notes in {doctor_language} with: "
            "1) Chief Complaint "
            "2) History of Present Illness "
            "3) Symptoms Summary "
            "4) Assessment "
            "5) Suggested Plan. "
            "Use standard medical terminology and format."
        )
        notes = _chat_completion(
            user_content=conversation_text,
            system_instruction=system_instruction,
            model=COMPLEX_MODEL,
            max_output_tokens=2048,
        )
        return {"success": True, "notes": notes, "error": None}
    except ValueError as e:
        return {"success": False, "notes": None, "error": str(e)}
    except Exception as e:
        return {"success": False, "notes": None, "error": f"Note generation failed: {str(e)}"}


def find_nearby_hospitals(city, specialty=None, language="English"):
    def _find():
        specialty_filter = (
            f" specializing in {specialty}"
            if specialty and specialty != "All Specialties"
            else ""
        )
        system_instruction = (
            "You are a healthcare location assistant helping find hospitals in India. "
            f"Find 5-8 hospitals{specialty_filter} near {city}, India. "
            f"Respond in {language} with valid JSON only. "
            "Return a JSON object with a 'hospitals' array. "
            "Each hospital must have these fields: "
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
        payload = _json_completion(
            user_content=f"Find hospitals near {city}{specialty_filter}",
            system_instruction=system_instruction,
            model=FAST_MODEL,
            max_output_tokens=4096,
        )
        hospitals = payload.get("hospitals", payload if isinstance(payload, list) else [])
        return {"success": True, "hospitals": hospitals, "error": None}

    try:
        result = call_groq_with_retry(_find)
        if isinstance(result, dict) and not result.get("success"):
            return result
        return result
    except ValueError as e:
        return {"success": False, "hospitals": [], "error": str(e)}
    except Exception as e:
        return {"success": False, "hospitals": [], "error": f"Hospital search failed: {str(e)}"}
