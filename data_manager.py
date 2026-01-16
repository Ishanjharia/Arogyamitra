import json
import os
from datetime import datetime, timedelta
import pandas as pd

DATA_DIR = "health_data"
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
