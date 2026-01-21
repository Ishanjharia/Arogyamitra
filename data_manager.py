import json
import os
from datetime import datetime, timedelta
import pandas as pd

DATA_DIR = "/tmp/health_data"
APPOINTMENTS_FILE = os.path.join(DATA_DIR, "appointments.json")
PRESCRIPTIONS_FILE = os.path.join(DATA_DIR, "prescriptions.json")
HEALTH_RECORDS_FILE = os.path.join(DATA_DIR, "health_records.json")
REMINDERS_FILE = os.path.join(DATA_DIR, "reminders.json")

def ensure_data_directory():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    if not os.path.exists(APPOINTMENTS_FILE):
        with open(APPOINTMENTS_FILE, 'w') as f:
            json.dump([], f)
    
    if not os.path.exists(PRESCRIPTIONS_FILE):
        with open(PRESCRIPTIONS_FILE, 'w') as f:
            json.dump([], f)
    
    if not os.path.exists(HEALTH_RECORDS_FILE):
        with open(HEALTH_RECORDS_FILE, 'w') as f:
            json.dump([], f)
    
    if not os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, 'w') as f:
            json.dump([], f)

def load_json_file(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except:
        return []

def save_json_file(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def add_appointment(patient_name, doctor_name, date, time, language, notes=""):
    ensure_data_directory()
    appointments = load_json_file(APPOINTMENTS_FILE)
    
    appointment = {
        "id": len(appointments) + 1,
        "patient_name": patient_name,
        "doctor_name": doctor_name,
        "date": date,
        "time": time,
        "language": language,
        "notes": notes,
        "status": "Scheduled",
        "created_at": datetime.now().isoformat()
    }
    
    appointments.append(appointment)
    save_json_file(APPOINTMENTS_FILE, appointments)
    return appointment

def get_appointments(filter_by=None):
    ensure_data_directory()
    appointments = load_json_file(APPOINTMENTS_FILE)
    
    if filter_by:
        appointments = [apt for apt in appointments if 
                       filter_by.lower() in apt.get('patient_name', '').lower() or
                       filter_by.lower() in apt.get('doctor_name', '').lower()]
    
    return appointments

def update_appointment(appointment_id, **kwargs):
    ensure_data_directory()
    appointments = load_json_file(APPOINTMENTS_FILE)
    
    for apt in appointments:
        if apt['id'] == appointment_id:
            for key, value in kwargs.items():
                if key in apt:
                    apt[key] = value
            save_json_file(APPOINTMENTS_FILE, appointments)
            return apt
    
    return None

def delete_appointment(appointment_id):
    ensure_data_directory()
    appointments = load_json_file(APPOINTMENTS_FILE)
    appointments = [apt for apt in appointments if apt['id'] != appointment_id]
    save_json_file(APPOINTMENTS_FILE, appointments)
    return True

def add_prescription(patient_name, doctor_name, medication, dosage, instructions, language, translated_text=""):
    ensure_data_directory()
    prescriptions = load_json_file(PRESCRIPTIONS_FILE)
    
    prescription = {
        "id": len(prescriptions) + 1,
        "patient_name": patient_name,
        "doctor_name": doctor_name,
        "medication": medication,
        "dosage": dosage,
        "instructions": instructions,
        "language": language,
        "translated_text": translated_text,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "created_at": datetime.now().isoformat()
    }
    
    prescriptions.append(prescription)
    save_json_file(PRESCRIPTIONS_FILE, prescriptions)
    return prescription

def get_prescriptions(patient_name=None):
    ensure_data_directory()
    prescriptions = load_json_file(PRESCRIPTIONS_FILE)
    
    if patient_name:
        prescriptions = [p for p in prescriptions if 
                        patient_name.lower() in p.get('patient_name', '').lower()]
    
    return prescriptions

def update_prescription(prescription_id, **kwargs):
    ensure_data_directory()
    prescriptions = load_json_file(PRESCRIPTIONS_FILE)
    
    for rx in prescriptions:
        if rx['id'] == prescription_id:
            for key, value in kwargs.items():
                if key in rx:
                    rx[key] = value
            save_json_file(PRESCRIPTIONS_FILE, prescriptions)
            return rx
    
    return None

def delete_prescription(prescription_id):
    ensure_data_directory()
    prescriptions = load_json_file(PRESCRIPTIONS_FILE)
    prescriptions = [rx for rx in prescriptions if rx['id'] != prescription_id]
    save_json_file(PRESCRIPTIONS_FILE, prescriptions)
    return True

def add_health_record(patient_name, record_type, description, language, report_data=None):
    ensure_data_directory()
    records = load_json_file(HEALTH_RECORDS_FILE)
    
    record = {
        "id": len(records) + 1,
        "patient_name": patient_name,
        "record_type": record_type,
        "description": description,
        "language": language,
        "report_data": report_data or {},
        "date": datetime.now().strftime("%Y-%m-%d"),
        "created_at": datetime.now().isoformat()
    }
    
    records.append(record)
    save_json_file(HEALTH_RECORDS_FILE, records)
    return record

def get_health_records(patient_name=None):
    ensure_data_directory()
    records = load_json_file(HEALTH_RECORDS_FILE)
    
    if patient_name:
        records = [r for r in records if 
                  patient_name.lower() in r.get('patient_name', '').lower()]
    
    return records

def update_health_record(record_id, **kwargs):
    ensure_data_directory()
    records = load_json_file(HEALTH_RECORDS_FILE)
    
    for record in records:
        if record['id'] == record_id:
            for key, value in kwargs.items():
                if key in record:
                    record[key] = value
            save_json_file(HEALTH_RECORDS_FILE, records)
            return record
    
    return None

def delete_health_record(record_id):
    ensure_data_directory()
    records = load_json_file(HEALTH_RECORDS_FILE)
    records = [r for r in records if r['id'] != record_id]
    save_json_file(HEALTH_RECORDS_FILE, records)
    return True

def add_reminder(patient_name, reminder_type, message, language, phone_number=""):
    ensure_data_directory()
    reminders = load_json_file(REMINDERS_FILE)
    
    reminder = {
        "id": len(reminders) + 1,
        "patient_name": patient_name,
        "reminder_type": reminder_type,
        "message": message,
        "language": language,
        "phone_number": phone_number,
        "status": "Pending",
        "created_at": datetime.now().isoformat(),
        "scheduled_for": (datetime.now() + timedelta(days=1)).isoformat()
    }
    
    reminders.append(reminder)
    save_json_file(REMINDERS_FILE, reminders)
    return reminder

def get_reminders(patient_name=None):
    ensure_data_directory()
    reminders = load_json_file(REMINDERS_FILE)
    
    if patient_name:
        reminders = [r for r in reminders if 
                    patient_name.lower() in r.get('patient_name', '').lower()]
    
    return reminders

def update_reminder(reminder_id, **kwargs):
    ensure_data_directory()
    reminders = load_json_file(REMINDERS_FILE)
    
    for reminder in reminders:
        if reminder['id'] == reminder_id:
            for key, value in kwargs.items():
                if key in reminder:
                    reminder[key] = value
            save_json_file(REMINDERS_FILE, reminders)
            return reminder
    
    return None

def delete_reminder(reminder_id):
    ensure_data_directory()
    reminders = load_json_file(REMINDERS_FILE)
    reminders = [r for r in reminders if r['id'] != reminder_id]
    save_json_file(REMINDERS_FILE, reminders)
    return True

def get_appointments_dataframe():
    appointments = get_appointments()
    if appointments:
        return pd.DataFrame(appointments)
    return pd.DataFrame(columns=['patient_name', 'doctor_name', 'date', 'time', 'status'])

def get_prescriptions_dataframe(patient_name=None):
    prescriptions = get_prescriptions(patient_name)
    if prescriptions:
        return pd.DataFrame(prescriptions)
    return pd.DataFrame(columns=['patient_name', 'doctor_name', 'medication', 'dosage', 'date'])

def get_health_records_dataframe(patient_name=None):
    records = get_health_records(patient_name)
    if records:
        return pd.DataFrame(records)
    return pd.DataFrame(columns=['patient_name', 'record_type', 'description', 'date'])

MEDICATIONS_FILE = os.path.join(DATA_DIR, "medications.json")

def ensure_medications_file():
    ensure_data_directory()
    if not os.path.exists(MEDICATIONS_FILE):
        with open(MEDICATIONS_FILE, 'w') as f:
            json.dump([], f)

def add_medication(patient_name, medication_name, dosage, frequency, start_date, end_date=None, notes=""):
    ensure_medications_file()
    medications = load_json_file(MEDICATIONS_FILE)
    
    medication = {
        "id": len(medications) + 1,
        "patient_name": patient_name,
        "medication_name": medication_name,
        "dosage": dosage,
        "frequency": frequency,
        "start_date": start_date,
        "end_date": end_date,
        "notes": notes,
        "status": "Active",
        "created_at": datetime.now().isoformat()
    }
    
    medications.append(medication)
    save_json_file(MEDICATIONS_FILE, medications)
    return medication

def get_medications(patient_name=None):
    ensure_medications_file()
    medications = load_json_file(MEDICATIONS_FILE)
    
    if patient_name:
        medications = [m for m in medications if 
                      patient_name.lower() in m.get('patient_name', '').lower()]
    
    return medications

def update_medication(medication_id, **kwargs):
    ensure_medications_file()
    medications = load_json_file(MEDICATIONS_FILE)
    
    for med in medications:
        if med['id'] == medication_id:
            for key, value in kwargs.items():
                if key in med:
                    med[key] = value
            save_json_file(MEDICATIONS_FILE, medications)
            return med
    
    return None

def delete_medication(medication_id):
    ensure_medications_file()
    medications = load_json_file(MEDICATIONS_FILE)
    medications = [m for m in medications if m['id'] != medication_id]
    save_json_file(MEDICATIONS_FILE, medications)
    return True

def get_medications_dataframe(patient_name=None):
    medications = get_medications(patient_name)
    if medications:
        return pd.DataFrame(medications)
    return pd.DataFrame(columns=['patient_name', 'medication_name', 'dosage', 'frequency', 'start_date', 'status'])

SAVED_HOSPITALS_FILE = os.path.join(DATA_DIR, "saved_hospitals.json")

def ensure_saved_hospitals_file():
    ensure_data_directory()
    if not os.path.exists(SAVED_HOSPITALS_FILE):
        with open(SAVED_HOSPITALS_FILE, 'w') as f:
            json.dump([], f)

def add_saved_hospital(user_id, hospital_name, address, phone, specialties, city, distance_km=None):
    ensure_saved_hospitals_file()
    hospitals = load_json_file(SAVED_HOSPITALS_FILE)
    
    existing = [h for h in hospitals if h.get('user_id') == user_id and h.get('hospital_name') == hospital_name]
    if existing:
        return {"success": False, "error": "Hospital already saved"}
    
    hospital = {
        "id": len(hospitals) + 1,
        "user_id": user_id,
        "hospital_name": hospital_name,
        "address": address,
        "phone": phone,
        "specialties": specialties,
        "city": city,
        "distance_km": distance_km,
        "saved_at": datetime.now().isoformat()
    }
    
    hospitals.append(hospital)
    save_json_file(SAVED_HOSPITALS_FILE, hospitals)
    return {"success": True, "hospital": hospital}

def get_saved_hospitals(user_id=None):
    ensure_saved_hospitals_file()
    hospitals = load_json_file(SAVED_HOSPITALS_FILE)
    
    if user_id:
        hospitals = [h for h in hospitals if h.get('user_id') == user_id]
    
    return hospitals

def delete_saved_hospital(hospital_id):
    ensure_saved_hospitals_file()
    hospitals = load_json_file(SAVED_HOSPITALS_FILE)
    hospitals = [h for h in hospitals if h['id'] != hospital_id]
    save_json_file(SAVED_HOSPITALS_FILE, hospitals)
    return True

SUPPORT_TICKETS_FILE = os.path.join(DATA_DIR, "support_tickets.json")

def ensure_support_tickets_file():
    ensure_data_directory()
    if not os.path.exists(SUPPORT_TICKETS_FILE):
        with open(SUPPORT_TICKETS_FILE, 'w') as f:
            json.dump([], f)

def add_support_ticket(user_id, user_name, user_email, category, description, language):
    ensure_support_tickets_file()
    tickets = load_json_file(SUPPORT_TICKETS_FILE)
    
    ticket = {
        "id": len(tickets) + 1,
        "user_id": user_id,
        "user_name": user_name,
        "user_email": user_email,
        "category": category,
        "description": description,
        "language": language,
        "status": "Open",
        "created_at": datetime.now().isoformat()
    }
    
    tickets.append(ticket)
    save_json_file(SUPPORT_TICKETS_FILE, tickets)
    return {"success": True, "ticket": ticket}

def get_support_tickets(user_id=None):
    ensure_support_tickets_file()
    tickets = load_json_file(SUPPORT_TICKETS_FILE)
    
    if user_id:
        tickets = [t for t in tickets if t.get('user_id') == user_id]
    
    return tickets

HEALTH_PROFILES_FILE = os.path.join(DATA_DIR, "health_profiles.json")

def ensure_health_profiles_file():
    ensure_data_directory()
    if not os.path.exists(HEALTH_PROFILES_FILE):
        with open(HEALTH_PROFILES_FILE, 'w') as f:
            json.dump([], f)

def save_health_profile(user_id, profile_data):
    ensure_health_profiles_file()
    profiles = load_json_file(HEALTH_PROFILES_FILE)
    
    existing_index = None
    for i, p in enumerate(profiles):
        if p.get('user_id') == user_id:
            existing_index = i
            break
    
    profile = {
        "id": len(profiles) + 1 if existing_index is None else profiles[existing_index]['id'],
        "user_id": user_id,
        "blood_type": profile_data.get('blood_type', ''),
        "height": profile_data.get('height', 0),
        "weight": profile_data.get('weight', 0),
        "date_of_birth": profile_data.get('date_of_birth', ''),
        "gender": profile_data.get('gender', ''),
        "allergies": profile_data.get('allergies', ''),
        "chronic_conditions": profile_data.get('chronic_conditions', ''),
        "current_medications": profile_data.get('current_medications', ''),
        "emergency_contact_name": profile_data.get('emergency_contact_name', ''),
        "emergency_contact_phone": profile_data.get('emergency_contact_phone', ''),
        "primary_doctor": profile_data.get('primary_doctor', ''),
        "smoking_status": profile_data.get('smoking_status', ''),
        "alcohol_status": profile_data.get('alcohol_status', ''),
        "exercise_frequency": profile_data.get('exercise_frequency', ''),
        "updated_at": datetime.now().isoformat()
    }
    
    if existing_index is not None:
        profiles[existing_index] = profile
    else:
        profiles.append(profile)
    
    save_json_file(HEALTH_PROFILES_FILE, profiles)
    return {"success": True, "profile": profile}

def get_health_profile(user_id):
    ensure_health_profiles_file()
    profiles = load_json_file(HEALTH_PROFILES_FILE)
    
    for profile in profiles:
        if profile.get('user_id') == user_id:
            return profile
    
    return None

def get_health_context_for_ai(user_id):
    """Get health profile formatted for AI context"""
    profile = get_health_profile(user_id)
    if not profile:
        return None
    
    context_parts = []
    
    if profile.get('blood_type'):
        context_parts.append(f"Blood Type: {profile['blood_type']}")
    if profile.get('gender'):
        context_parts.append(f"Gender: {profile['gender']}")
    if profile.get('height') and profile.get('weight'):
        context_parts.append(f"Height: {profile['height']}cm, Weight: {profile['weight']}kg")
    if profile.get('allergies'):
        context_parts.append(f"ALLERGIES: {profile['allergies']}")
    if profile.get('chronic_conditions'):
        context_parts.append(f"CHRONIC CONDITIONS: {profile['chronic_conditions']}")
    if profile.get('current_medications'):
        context_parts.append(f"CURRENT MEDICATIONS: {profile['current_medications']}")
    if profile.get('smoking_status'):
        context_parts.append(f"Smoking: {profile['smoking_status']}")
    if profile.get('alcohol_status'):
        context_parts.append(f"Alcohol: {profile['alcohol_status']}")
    
    if context_parts:
        return "PATIENT HEALTH PROFILE:\n" + "\n".join(context_parts)
    return None

ANALYTICS_FILE = os.path.join(DATA_DIR, "analytics.json")

def ensure_analytics_file():
    ensure_data_directory()
    if not os.path.exists(ANALYTICS_FILE):
        initial_data = {
            "feature_clicks": {},
            "language_usage": {},
            "symptom_keywords": {},
            "role_sessions": {"Patient": 0, "Doctor": 0},
            "daily_visits": {},
            "total_sessions": 0
        }
        with open(ANALYTICS_FILE, 'w') as f:
            json.dump(initial_data, f, indent=2)

def load_analytics():
    ensure_analytics_file()
    try:
        with open(ANALYTICS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {
            "feature_clicks": {},
            "language_usage": {},
            "symptom_keywords": {},
            "role_sessions": {"Patient": 0, "Doctor": 0},
            "daily_visits": {},
            "total_sessions": 0
        }

def save_analytics(data):
    ensure_analytics_file()
    with open(ANALYTICS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def track_feature_click(feature_name):
    """Track when a feature/page is accessed"""
    analytics = load_analytics()
    if feature_name not in analytics["feature_clicks"]:
        analytics["feature_clicks"][feature_name] = 0
    analytics["feature_clicks"][feature_name] += 1
    save_analytics(analytics)

def track_language_usage(language):
    """Track language preference usage"""
    analytics = load_analytics()
    if language not in analytics["language_usage"]:
        analytics["language_usage"][language] = 0
    analytics["language_usage"][language] += 1
    save_analytics(analytics)

def track_symptom_keyword(symptom_text):
    """Extract and track common symptom keywords (anonymized)"""
    common_symptoms = [
        "headache", "fever", "cough", "cold", "pain", "fatigue", "nausea",
        "dizziness", "chest", "breathing", "stomach", "back", "joint",
        "throat", "skin", "allergy", "infection", "weakness", "anxiety",
        "सिरदर्द", "बुखार", "खांसी", "दर्द", "थकान", "चक्कर"
    ]
    
    analytics = load_analytics()
    symptom_lower = symptom_text.lower()
    
    for keyword in common_symptoms:
        if keyword in symptom_lower:
            if keyword not in analytics["symptom_keywords"]:
                analytics["symptom_keywords"][keyword] = 0
            analytics["symptom_keywords"][keyword] += 1
    
    save_analytics(analytics)

def track_role_session(role):
    """Track session by user role"""
    analytics = load_analytics()
    if role in analytics["role_sessions"]:
        analytics["role_sessions"][role] += 1
    save_analytics(analytics)

def track_daily_visit():
    """Track daily unique visits"""
    analytics = load_analytics()
    today = datetime.now().strftime("%Y-%m-%d")
    if today not in analytics["daily_visits"]:
        analytics["daily_visits"][today] = 0
    analytics["daily_visits"][today] += 1
    analytics["total_sessions"] += 1
    save_analytics(analytics)

def get_analytics_summary():
    """Get analytics summary for dashboard"""
    analytics = load_analytics()
    
    feature_clicks = analytics.get("feature_clicks", {})
    top_features = sorted(feature_clicks.items(), key=lambda x: x[1], reverse=True)[:10]
    
    language_usage = analytics.get("language_usage", {})
    symptom_keywords = analytics.get("symptom_keywords", {})
    top_symptoms = sorted(symptom_keywords.items(), key=lambda x: x[1], reverse=True)[:10]
    
    daily_visits = analytics.get("daily_visits", {})
    last_7_days = {}
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        last_7_days[date] = daily_visits.get(date, 0)
    
    return {
        "top_features": top_features,
        "language_usage": language_usage,
        "top_symptoms": top_symptoms,
        "role_sessions": analytics.get("role_sessions", {}),
        "total_sessions": analytics.get("total_sessions", 0),
        "last_7_days": last_7_days
    }

def get_public_stats():
    """Get safe public statistics for landing page (no PII)"""
    analytics = load_analytics()
    
    language_usage = analytics.get("language_usage", {})
    total_languages = len([l for l, c in language_usage.items() if c > 0])
    
    role_sessions = analytics.get("role_sessions", {})
    total_patients = role_sessions.get("Patient", 0)
    total_doctors = role_sessions.get("Doctor", 0)
    
    daily_visits = analytics.get("daily_visits", {})
    total_visits = sum(daily_visits.values())
    
    top_symptoms = analytics.get("symptom_keywords", {})
    symptoms_analyzed = sum(top_symptoms.values())
    
    return {
        "total_users": analytics.get("total_sessions", 0),
        "languages_used": total_languages,
        "patients_helped": total_patients,
        "doctors_assisted": total_doctors,
        "symptoms_analyzed": symptoms_analyzed,
        "total_visits": total_visits
    }
