import streamlit as st
import os
from datetime import datetime, timedelta
from audio_recorder_streamlit import audio_recorder
from gtts import gTTS
import tempfile
import base64

import ai_helper
import data_manager
import auth_manager

st.set_page_config(
    page_title="Arogya Mitra - आरोग्य मित्र",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_language' not in st.session_state:
        st.session_state.user_language = "English"
    if 'patient_name' not in st.session_state:
        st.session_state.patient_name = ""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'translation_chat' not in st.session_state:
        st.session_state.translation_chat = []
    if 'auth_page' not in st.session_state:
        st.session_state.auth_page = "login"

def play_audio_text(text, language_code):
    try:
        tts = gTTS(text=text, lang=language_code, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            audio_file = open(fp.name, 'rb')
            audio_bytes = audio_file.read()
            audio_base64 = base64.b64encode(audio_bytes).decode()
            audio_html = f'<audio autoplay><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
            st.markdown(audio_html, unsafe_allow_html=True)
            audio_file.close()
            os.unlink(fp.name)
    except Exception as e:
        st.warning(f"Could not play audio: {str(e)}")

def login_page():
    st.title("🏥 Arogya Mitra - आरोग्य मित्र")
    st.subheader("Your Multilingual Health Companion")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Sign In")
        
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        if st.button("Sign In", type="primary", use_container_width=True):
            if email and password:
                result = auth_manager.authenticate_user(email, password)
                if result["success"]:
                    st.session_state.authenticated = True
                    st.session_state.current_user = result["user"]
                    st.session_state.user_role = result["user"]["role"]
                    st.session_state.patient_name = result["user"]["name"]
                    st.session_state.user_language = result["user"].get("language", "English")
                    st.success(f"Welcome back, {result['user']['name']}!")
                    st.rerun()
                else:
                    st.error(result["error"])
            else:
                st.warning("Please enter both email and password")
        
        st.markdown("---")
        st.markdown("Don't have an account?")
        if st.button("Create New Account", use_container_width=True):
            st.session_state.auth_page = "signup"
            st.rerun()
    
    st.markdown("---")
    st.info("💡 Arogya Mitra supports Hindi, Marathi, Tamil, Telugu, Bengali, Gujarati, Kannada, Malayalam, Punjabi, and English")

def signup_page():
    st.title("🏥 Arogya Mitra - आरोग्य मित्र")
    st.subheader("Create Your Account")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 📝 Sign Up")
        
        name = st.text_input("Full Name", placeholder="Enter your full name")
        email = st.text_input("Email", placeholder="Enter your email")
        phone = st.text_input("Phone Number (optional)", placeholder="+91...")
        password = st.text_input("Password", type="password", placeholder="Create a password (min 6 characters)")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        st.markdown("### 👤 I am a:")
        role = st.radio("Select your role", ["Patient", "Doctor"], horizontal=True)
        
        language = st.selectbox(
            "Preferred Language",
            options=list(ai_helper.SUPPORTED_LANGUAGES.keys()),
            index=0
        )
        
        if st.button("Create Account", type="primary", use_container_width=True):
            if not name or not email or not password:
                st.warning("Please fill in all required fields")
            elif len(password) < 6:
                st.warning("Password must be at least 6 characters")
            elif password != confirm_password:
                st.error("Passwords do not match")
            else:
                result = auth_manager.create_user(
                    name=name,
                    email=email,
                    password=password,
                    role=role,
                    language=language,
                    phone=phone
                )
                if result["success"]:
                    st.success("Account created successfully! Please sign in.")
                    st.session_state.auth_page = "login"
                    st.rerun()
                else:
                    st.error(result["error"])
        
        st.markdown("---")
        st.markdown("Already have an account?")
        if st.button("Back to Sign In", use_container_width=True):
            st.session_state.auth_page = "login"
            st.rerun()

def role_selection_page():
    if st.session_state.auth_page == "signup":
        signup_page()
    else:
        login_page()

def sidebar_navigation():
    with st.sidebar:
        st.title("🏥 Arogya Mitra")
        st.caption("आरोग्य मित्र - Your Health Friend")
        
        if st.session_state.current_user:
            st.markdown(f"**👤 {st.session_state.current_user['name']}**")
            st.markdown(f"*{st.session_state.user_role}*")
        
        st.markdown("---")
        
        st.markdown("### 🌐 Language Preference")
        selected_language = st.selectbox(
            "Select your language",
            options=list(ai_helper.SUPPORTED_LANGUAGES.keys()),
            index=list(ai_helper.SUPPORTED_LANGUAGES.keys()).index(st.session_state.user_language)
        )
        if selected_language != st.session_state.user_language:
            st.session_state.user_language = selected_language
            if st.session_state.current_user:
                auth_manager.update_user(st.session_state.current_user['id'], language=selected_language)
                st.session_state.current_user['language'] = selected_language
                st.toast(f"Language saved: {selected_language}")
        st.session_state.user_language = selected_language
        
        st.markdown("---")
        
        if st.session_state.user_role == "Patient":
            menu_options = [
                "🏠 Home",
                "🔍 Symptom Checker",
                "💬 Chat with AI",
                "📋 My Prescriptions",
                "📁 Health Records",
                "📅 Book Appointment",
                "🔔 My Reminders"
            ]
        else:
            menu_options = [
                "🏠 Home",
                "💬 AI Chat Assistant",
                "🌐 Patient-Doctor Translation",
                "📝 Write Prescription",
                "📅 View Appointments",
                "📊 Patient Records"
            ]
        
        st.markdown("---")
        selected_menu = st.radio("Navigation", menu_options, label_visibility="collapsed")
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.user_role = None
            st.session_state.patient_name = ""
            st.session_state.chat_history = []
            st.session_state.translation_chat = []
            st.session_state.auth_page = "login"
            st.rerun()
        
        return selected_menu

def symptom_checker_page():
    st.title("🔍 AI Symptom Checker")
    st.markdown(f"**Language:** {st.session_state.user_language}")
    
    st.info("⚠️ This is not a medical diagnosis. Please consult a qualified doctor for proper medical advice.")
    
    tab1, tab2 = st.tabs(["💬 Text Input", "🎤 Voice Input"])
    
    with tab1:
        st.markdown("### Describe Your Symptoms")
        symptoms_text = st.text_area(
            "Tell us what you're experiencing",
            placeholder=f"Example: I have a fever, headache, and body pain for the last 3 days...",
            height=150
        )
        
        if st.button("🔍 Analyze Symptoms", type="primary"):
            if symptoms_text:
                with st.spinner("Analyzing your symptoms..."):
                    analysis = ai_helper.analyze_symptoms(symptoms_text, st.session_state.user_language)
                    
                    if analysis.get("success"):
                        st.success("✅ Analysis Complete!")
                        
                        st.markdown("### 📊 Symptom Analysis Report")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Severity Level:**")
                            if analysis.get('severity_level') == 'High':
                                st.error(f"🔴 {analysis.get('severity_level', 'Unknown')}")
                            elif analysis.get('severity_level') == 'Medium':
                                st.warning(f"🟡 {analysis.get('severity_level', 'Unknown')}")
                            else:
                                st.info(f"🟢 {analysis.get('severity_level', 'Unknown')}")
                        
                        with col2:
                            st.markdown("**Urgent Care Needed:**")
                            if analysis.get('urgent_care_needed'):
                                st.error("⚠️ Yes - Please seek immediate medical attention")
                            else:
                                st.success("✓ No immediate urgency detected")
                        
                        st.markdown("**Summary:**")
                        st.write(analysis.get('symptoms_summary', 'N/A'))
                        
                        st.markdown("**Possible Conditions to Discuss with Doctor:**")
                        for condition in analysis.get('possible_conditions', []):
                            st.write(f"• {condition}")
                        
                        st.markdown("**Recommendations:**")
                        st.write(analysis.get('recommendations', 'Please consult a doctor'))
                        
                        st.markdown("**Questions for Your Doctor:**")
                        for question in analysis.get('follow_up_questions', []):
                            st.write(f"• {question}")
                        
                        if st.session_state.patient_name:
                            if st.button("💾 Save to Health Records"):
                                data_manager.add_health_record(
                                    patient_name=st.session_state.patient_name,
                                    record_type="Symptom Analysis",
                                    description=symptoms_text,
                                    language=st.session_state.user_language,
                                    report_data=analysis
                                )
                                st.success("✅ Saved to your health records!")
                    else:
                        st.error(f"Error: {analysis.get('error', 'Unknown error')}")
            else:
                st.warning("Please describe your symptoms")
    
    with tab2:
        st.markdown("### 🎤 Record Your Symptoms")
        st.write("Click the microphone to record your symptoms in your language")
        
        audio_bytes = audio_recorder(
            text="Click to record",
            recording_color="#e74c3c",
            neutral_color="#3498db",
            icon_size="2x"
        )
        
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            
            if st.button("🔄 Transcribe & Analyze", type="primary"):
                with st.spinner("Processing audio..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as fp:
                        fp.write(audio_bytes)
                        fp.flush()
                        
                        result = ai_helper.transcribe_audio(fp.name)
                        os.unlink(fp.name)
                    
                    if result.get("success"):
                        transcription = result.get("transcription")
                        st.success("✅ Transcription Complete!")
                        st.markdown("**You said:**")
                        st.info(transcription)
                        
                        with st.spinner("Analyzing symptoms..."):
                            analysis = ai_helper.analyze_symptoms(transcription, st.session_state.user_language)
                            
                            if analysis.get("success"):
                                st.markdown("### 📊 Analysis Report")
                                st.json(analysis)
                                
                                if st.session_state.patient_name:
                                    if st.button("💾 Save Analysis"):
                                        data_manager.add_health_record(
                                            patient_name=st.session_state.patient_name,
                                            record_type="Voice Symptom Analysis",
                                            description=transcription,
                                            language=st.session_state.user_language,
                                            report_data=analysis
                                        )
                                        st.success("✅ Saved!")
                            else:
                                st.error(f"Analysis error: {analysis.get('error')}")
                    else:
                        st.error(f"Transcription error: {result.get('error')}")

def ai_chat_page():
    st.title("💬 AI Medical Chat Assistant")
    st.markdown(f"**Language:** {st.session_state.user_language}")
    
    st.info("Ask me health-related questions in your preferred language!")
    
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    user_input = st.chat_input("Type your question here...")
    
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.write(user_input)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = ai_helper.medical_chat_response(
                    user_input,
                    st.session_state.user_language,
                    st.session_state.user_role
                )
                if result.get("success"):
                    response = result.get("response")
                    st.write(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                else:
                    error_msg = f"Error: {result.get('error')}"
                    st.error(error_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})

def translation_chat_page():
    st.title("🌐 Patient-Doctor Real-Time Translation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👤 Patient Language")
        patient_lang = st.selectbox(
            "Patient speaks",
            options=list(ai_helper.SUPPORTED_LANGUAGES.keys()),
            key="patient_lang"
        )
    
    with col2:
        st.markdown("### 👨‍⚕️ Doctor Language")
        doctor_lang = st.selectbox(
            "Doctor speaks",
            options=list(ai_helper.SUPPORTED_LANGUAGES.keys()),
            index=0,
            key="doctor_lang"
        )
    
    st.markdown("---")
    
    for msg in st.session_state.translation_chat:
        if msg["speaker"] == "Patient":
            st.markdown(f"**👤 Patient ({patient_lang}):**")
            st.info(msg["original"])
            if msg.get("translation"):
                st.markdown(f"*Translation to {doctor_lang}:* {msg['translation']}")
        else:
            st.markdown(f"**👨‍⚕️ Doctor ({doctor_lang}):**")
            st.success(msg["original"])
            if msg.get("translation"):
                st.markdown(f"*Translation to {patient_lang}:* {msg['translation']}")
        st.markdown("---")
    
    tab1, tab2 = st.tabs(["👤 Patient Message", "👨‍⚕️ Doctor Message"])
    
    with tab1:
        patient_message = st.text_area(f"Patient speaks in {patient_lang}", key="patient_msg")
        if st.button("Send & Translate", key="patient_send"):
            if patient_message:
                with st.spinner("Translating..."):
                    result = ai_helper.translate_text(patient_message, patient_lang, doctor_lang)
                    if result.get("success"):
                        translation = result.get("translation")
                        st.session_state.translation_chat.append({
                            "speaker": "Patient",
                            "original": patient_message,
                            "translation": translation
                        })
                        st.rerun()
                    else:
                        st.error(f"Translation error: {result.get('error')}")
    
    with tab2:
        doctor_message = st.text_area(f"Doctor speaks in {doctor_lang}", key="doctor_msg")
        if st.button("Send & Translate", key="doctor_send"):
            if doctor_message:
                with st.spinner("Translating..."):
                    result = ai_helper.translate_text(doctor_message, doctor_lang, patient_lang)
                    if result.get("success"):
                        translation = result.get("translation")
                        st.session_state.translation_chat.append({
                            "speaker": "Doctor",
                            "original": doctor_message,
                            "translation": translation
                        })
                        st.rerun()
                    else:
                        st.error(f"Translation error: {result.get('error')}")
    
    if st.session_state.translation_chat:
        if st.button("🔄 Clear Conversation"):
            st.session_state.translation_chat = []
            st.rerun()

def prescription_page():
    if st.session_state.user_role == "Doctor":
        st.title("📝 Write Prescription")
        
        col1, col2 = st.columns(2)
        
        with col1:
            patient_name = st.text_input("Patient Name")
            doctor_name = st.text_input("Doctor Name")
            medication = st.text_area("Medication Details", height=100)
        
        with col2:
            dosage = st.text_input("Dosage & Frequency")
            instructions = st.text_area("Instructions", height=100)
            patient_language = st.selectbox(
                "Translate to Patient's Language",
                options=list(ai_helper.SUPPORTED_LANGUAGES.keys())
            )
        
        prescription_text = f"""
Medication: {medication}
Dosage: {dosage}
Instructions: {instructions}
"""
        
        if st.button("💾 Generate & Save Prescription", type="primary"):
            if patient_name and medication:
                with st.spinner("Translating prescription..."):
                    result = ai_helper.generate_prescription_translation(
                        prescription_text,
                        st.session_state.user_language,
                        patient_language
                    )
                    
                    if result.get("success"):
                        translated = result.get("translation")
                        
                        data_manager.add_prescription(
                            patient_name=patient_name,
                            doctor_name=doctor_name,
                            medication=medication,
                            dosage=dosage,
                            instructions=instructions,
                            language=patient_language,
                            translated_text=translated
                        )
                        
                        st.success("✅ Prescription saved successfully!")
                        
                        st.markdown("### 📄 Prescription Preview")
                        st.markdown(f"**Original ({st.session_state.user_language}):**")
                        st.code(prescription_text)
                        
                        st.markdown(f"**Translated ({patient_language}):**")
                        st.info(translated)
                    else:
                        st.error(f"Translation error: {result.get('error')}")
            else:
                st.warning("Please fill in patient name and medication details")
    
    else:
        st.title("📋 My Prescriptions")
        
        if st.session_state.patient_name:
            prescriptions = data_manager.get_prescriptions(st.session_state.patient_name)
            
            if prescriptions:
                st.success(f"Found {len(prescriptions)} prescription(s)")
                
                for i, rx in enumerate(prescriptions, 1):
                    with st.expander(f"📋 Prescription #{i} - {rx['date']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**Doctor:** {rx['doctor_name']}")
                            st.markdown(f"**Date:** {rx['date']}")
                            st.markdown(f"**Medication:** {rx['medication']}")
                        
                        with col2:
                            st.markdown(f"**Dosage:** {rx['dosage']}")
                            st.markdown(f"**Language:** {rx['language']}")
                        
                        st.markdown("**Instructions:**")
                        st.write(rx['instructions'])
                        
                        if rx.get('translated_text'):
                            st.markdown(f"**Translation ({rx['language']}):**")
                            st.info(rx['translated_text'])
            else:
                st.info("No prescriptions found. Visit a doctor to get prescriptions.")
        else:
            st.warning("Please enter your name in the sidebar to view prescriptions")

def health_records_page():
    st.title("📁 Health Records")
    
    if st.session_state.patient_name:
        records = data_manager.get_health_records(st.session_state.patient_name)
        
        if records:
            st.success(f"Found {len(records)} record(s)")
            
            for i, record in enumerate(records, 1):
                with st.expander(f"📄 {record['record_type']} - {record['date']}"):
                    st.markdown(f"**Type:** {record['record_type']}")
                    st.markdown(f"**Date:** {record['date']}")
                    st.markdown(f"**Language:** {record['language']}")
                    st.markdown(f"**Description:** {record['description']}")
                    
                    if record.get('report_data'):
                        st.markdown("**Analysis Report:**")
                        st.json(record['report_data'])
        else:
            st.info("No health records yet. Use the Symptom Checker to create your first record.")
    else:
        st.warning("Please enter your name in the sidebar to view records")

def appointment_booking_page():
    st.title("📅 Book Appointment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        patient_name = st.text_input("Patient Name", value=st.session_state.patient_name)
        doctor_name = st.text_input("Doctor Name")
        appointment_date = st.date_input("Appointment Date", min_value=datetime.now().date())
    
    with col2:
        appointment_time = st.time_input("Appointment Time")
        language = st.selectbox(
            "Preferred Language for Consultation",
            options=list(ai_helper.SUPPORTED_LANGUAGES.keys()),
            index=list(ai_helper.SUPPORTED_LANGUAGES.keys()).index(st.session_state.user_language)
        )
        notes = st.text_area("Notes / Reason for Visit")
    
    if st.button("📅 Book Appointment", type="primary"):
        if patient_name and doctor_name:
            appointment = data_manager.add_appointment(
                patient_name=patient_name,
                doctor_name=doctor_name,
                date=str(appointment_date),
                time=str(appointment_time),
                language=language,
                notes=notes
            )
            
            st.success("✅ Appointment booked successfully!")
            st.balloons()
            
            st.markdown("### 📋 Appointment Details")
            st.info(f"""
**Patient:** {appointment['patient_name']}
**Doctor:** {appointment['doctor_name']}
**Date:** {appointment['date']}
**Time:** {appointment['time']}
**Language:** {appointment['language']}
**Status:** {appointment['status']}
            """)
            
            reminder_msg = f"Reminder: You have an appointment with Dr. {doctor_name} on {appointment_date} at {appointment_time}"
            data_manager.add_reminder(
                patient_name=patient_name,
                reminder_type="Appointment",
                message=reminder_msg,
                language=language
            )
            
            st.success("🔔 Reminder set for this appointment!")
        else:
            st.warning("Please fill in patient and doctor names")
    
    st.markdown("---")
    st.markdown("### 📋 Your Upcoming Appointments")
    
    if st.session_state.patient_name:
        appointments = data_manager.get_appointments(st.session_state.patient_name)
        if appointments:
            df = data_manager.get_appointments_dataframe()
            st.dataframe(df[['patient_name', 'doctor_name', 'date', 'time', 'status', 'language']], use_container_width=True)
        else:
            st.info("No appointments yet")

def view_appointments_doctor():
    st.title("📅 Appointments Overview")
    
    appointments = data_manager.get_appointments()
    
    if appointments:
        st.success(f"Total appointments: {len(appointments)}")
        df = data_manager.get_appointments_dataframe()
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No appointments scheduled yet")

def reminders_page():
    st.title("🔔 My Reminders")
    
    if st.session_state.patient_name:
        reminders = data_manager.get_reminders(st.session_state.patient_name)
        
        if reminders:
            st.success(f"You have {len(reminders)} reminder(s)")
            
            for reminder in reminders:
                with st.expander(f"🔔 {reminder['reminder_type']} - {reminder['status']}"):
                    st.markdown(f"**Type:** {reminder['reminder_type']}")
                    st.markdown(f"**Message:** {reminder['message']}")
                    st.markdown(f"**Language:** {reminder['language']}")
                    st.markdown(f"**Status:** {reminder['status']}")
                    st.markdown(f"**Scheduled:** {reminder.get('scheduled_for', 'N/A')}")
        else:
            st.info("No reminders set")
        
        st.markdown("---")
        st.markdown("### ➕ Create New Reminder")
        
        col1, col2 = st.columns(2)
        with col1:
            reminder_type = st.selectbox("Reminder Type", ["Medication", "Appointment", "Follow-up", "Other"])
            message = st.text_area("Reminder Message")
        
        with col2:
            phone = st.text_input("Phone Number (for SMS)", placeholder="+91...")
            
        if st.button("➕ Add Reminder"):
            if message:
                data_manager.add_reminder(
                    patient_name=st.session_state.patient_name,
                    reminder_type=reminder_type,
                    message=message,
                    language=st.session_state.user_language,
                    phone_number=phone
                )
                st.success("✅ Reminder created! (SMS will be sent via Twilio in production)")
                st.rerun()
    else:
        st.warning("Please enter your name in the sidebar")

def patient_records_doctor():
    st.title("📊 Patient Records")
    
    search_patient = st.text_input("Search Patient by Name")
    
    if search_patient:
        st.markdown(f"### Records for: {search_patient}")
        
        tab1, tab2, tab3 = st.tabs(["📋 Prescriptions", "📁 Health Records", "📅 Appointments"])
        
        with tab1:
            prescriptions = data_manager.get_prescriptions(search_patient)
            if prescriptions:
                df = data_manager.get_prescriptions_dataframe(search_patient)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No prescriptions found")
        
        with tab2:
            records = data_manager.get_health_records(search_patient)
            if records:
                df = data_manager.get_health_records_dataframe(search_patient)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No health records found")
        
        with tab3:
            appointments = data_manager.get_appointments(search_patient)
            if appointments:
                for apt in appointments:
                    st.write(f"- {apt['date']} at {apt['time']} - Status: {apt['status']}")
            else:
                st.info("No appointments found")

def home_page():
    st.title("🏥 Arogya Mitra - आरोग्य मित्र")
    
    if st.session_state.current_user:
        st.markdown(f"### Welcome, {st.session_state.current_user['name']}! 🙏")
    else:
        st.markdown(f"### Welcome, {st.session_state.user_role}!")
    
    if st.session_state.user_role == "Patient":
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🔍 Symptom Checker")
            st.write("Describe your symptoms in your language and get AI-powered analysis")
            
        with col2:
            st.markdown("### 💬 AI Chat")
            st.write("Ask health questions and get instant responses in your language")
        
        with col3:
            st.markdown("### 📅 Appointments")
            st.write("Book and manage your appointments with doctors")
        
        st.markdown("---")
        
        st.markdown("### 🌟 Key Features")
        st.write("✅ Voice-enabled symptom description")
        st.write("✅ Multilingual support (10+ Indian languages)")
        st.write("✅ Prescription translation")
        st.write("✅ Digital health records")
        st.write("✅ SMS reminders for medications")
        
    else:
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🌐 Real-Time Translation")
            st.write("Communicate with patients in their native language")
            
        with col2:
            st.markdown("### 📝 Smart Prescriptions")
            st.write("Write prescriptions that auto-translate to patient's language")
        
        st.markdown("---")
        
        st.markdown("### 🌟 Doctor Features")
        st.write("✅ Patient-doctor translation chat")
        st.write("✅ Automated prescription translation")
        st.write("✅ Patient record management")
        st.write("✅ AI medical chat assistant")
        st.write("✅ Appointment overview")
    
    st.markdown("---")
    st.info("💡 Select an option from the sidebar to get started!")

def main():
    data_manager.ensure_data_directory()
    initialize_session_state()
    
    if not st.session_state.authenticated:
        role_selection_page()
    else:
        menu = sidebar_navigation()
        
        if menu == "🏠 Home":
            home_page()
        elif menu == "🔍 Symptom Checker":
            symptom_checker_page()
        elif menu == "💬 Chat with AI" or menu == "💬 AI Chat Assistant":
            ai_chat_page()
        elif menu == "🌐 Patient-Doctor Translation":
            translation_chat_page()
        elif menu == "📝 Write Prescription" or menu == "📋 My Prescriptions":
            prescription_page()
        elif menu == "📁 Health Records":
            health_records_page()
        elif menu == "📅 Book Appointment":
            appointment_booking_page()
        elif menu == "📅 View Appointments":
            view_appointments_doctor()
        elif menu == "🔔 My Reminders":
            reminders_page()
        elif menu == "📊 Patient Records":
            patient_records_doctor()

if __name__ == "__main__":
    main()
