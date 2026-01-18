import streamlit as st
import os
from datetime import datetime, timedelta
from audio_recorder_streamlit import audio_recorder
from gtts import gTTS
import tempfile
import base64
import random
from fpdf import FPDF
from streamlit_theme import st_theme

import ai_helper
import data_manager
import auth_manager
from translations import get_text, get_greeting, get_nav_items, TRANSLATIONS

def sync_theme_with_streamlit():
    """Sync our custom theme with Streamlit's active theme"""
    try:
        streamlit_theme = st_theme()
        if streamlit_theme:
            base = streamlit_theme.get('base', 'light')
            current_theme = st.session_state.get('theme_mode', 'Light')
            
            if base == 'dark' and current_theme == 'Light':
                st.session_state.theme_mode = 'Dark'
            elif base == 'light' and current_theme == 'Dark':
                st.session_state.theme_mode = 'Light'
    except Exception:
        pass

HEALTH_TIPS = {
    "English": [
        "💧 Drink at least 8 glasses of water daily to stay hydrated.",
        "🚶 Walk for 30 minutes daily to improve heart health.",
        "🥗 Include more fruits and vegetables in your diet.",
        "😴 Get 7-8 hours of quality sleep every night.",
        "🧘 Practice deep breathing for 5 minutes to reduce stress.",
        "🍎 Eat a healthy breakfast to kickstart your metabolism.",
        "🚭 Avoid smoking and limit alcohol consumption.",
        "🧴 Wash hands frequently to prevent infections.",
        "📱 Take regular breaks from screens to protect your eyes.",
        "❤️ Regular health check-ups can catch problems early."
    ],
    "हिंदी (Hindi)": [
        "💧 हाइड्रेटेड रहने के लिए रोज़ाना कम से कम 8 गिलास पानी पिएं।",
        "🚶 दिल की सेहत के लिए रोज़ 30 मिनट टहलें।",
        "🥗 अपने आहार में अधिक फल और सब्ज़ियाँ शामिल करें।",
        "😴 हर रात 7-8 घंटे की अच्छी नींद लें।",
        "🧘 तनाव कम करने के लिए 5 मिनट गहरी सांस लें।",
        "🍎 मेटाबॉलिज्म बढ़ाने के लिए स्वस्थ नाश्ता करें।",
        "🚭 धूम्रपान से बचें और शराब सीमित करें।",
        "🧴 संक्रमण से बचने के लिए बार-बार हाथ धोएं।",
        "📱 आंखों की सुरक्षा के लिए स्क्रीन से नियमित ब्रेक लें।",
        "❤️ नियमित स्वास्थ्य जांच समस्याओं को जल्दी पकड़ सकती है।"
    ],
    "मराठी (Marathi)": [
        "💧 हायड्रेटेड राहण्यासाठी दररोज किमान 8 ग्लास पाणी प्या।",
        "🚶 हृदयाच्या आरोग्यासाठी दररोज 30 मिनिटे चाला।",
        "🥗 आहारात अधिक फळे आणि भाज्या समाविष्ट करा।",
        "😴 दररात्री 7-8 तासांची चांगली झोप घ्या।",
        "🧘 तणाव कमी करण्यासाठी 5 मिनिटे दीर्घ श्वास घ्या।"
    ]
}

EMERGENCY_CONTACTS = {
    "ambulance": "102",
    "police": "100",
    "fire": "101",
    "women_helpline": "1091",
    "child_helpline": "1098",
    "emergency": "112"
}

st.set_page_config(
    page_title="Arogya Mitra - आरोग्य मित्र",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

def generate_whatsapp_share_url(text):
    import urllib.parse
    encoded_text = urllib.parse.quote(text)
    return f"https://wa.me/?text={encoded_text}"

def inject_custom_css():
    theme_mode = st.session_state.get('theme_mode', 'Light')
    text_size = st.session_state.get('text_size', 'Medium')
    
    size_multipliers = {
        'Small': '0.9',
        'Medium': '1.0',
        'Large': '1.2'
    }
    size_mult = size_multipliers.get(text_size, '1.0')
    
    COLOR_PRIMARY = '#4F7CF3'
    COLOR_SUCCESS = '#2CB9A8'
    COLOR_WARNING = '#F4B740'
    COLOR_DANGER = '#E5533D'
    COLOR_INFO = '#6366F1'
    
    theme_palettes = {
        'Light': {
            'bg_primary': '#F7F9FC',
            'bg_secondary': '#EEF2FF',
            'bg_card': '#FFFFFF',
            'text_primary': '#1F2937',
            'text_secondary': '#6B7280',
            'border_color': '#E5E7EB',
            'sidebar_bg': '#EEF2FF',
            'sidebar_text': '#1F2937'
        },
        'Dark': {
            'bg_primary': '#0F172A',
            'bg_secondary': '#1E293B',
            'bg_card': '#1E293B',
            'text_primary': '#E5E7EB',
            'text_secondary': '#9CA3AF',
            'border_color': '#334155',
            'sidebar_bg': '#020617',
            'sidebar_text': '#E5E7EB'
        },
        'High Contrast': {
            'bg_primary': '#000000',
            'bg_secondary': '#000000',
            'bg_card': '#0A0A0A',
            'text_primary': '#FFFFFF',
            'text_secondary': '#FFD400',
            'border_color': '#FFFFFF',
            'sidebar_bg': '#000000',
            'sidebar_text': '#FFFFFF'
        }
    }
    
    palette = theme_palettes.get(theme_mode, theme_palettes['Light'])
    bg_primary = palette['bg_primary']
    bg_secondary = palette['bg_secondary']
    bg_card = palette['bg_card']
    text_primary = palette['text_primary']
    text_secondary = palette['text_secondary']
    border_color = palette['border_color']
    sidebar_bg = palette['sidebar_bg']
    sidebar_text = palette['sidebar_text']
    
    is_dark_theme = theme_mode in ['Dark', 'High Contrast']
    is_high_contrast = theme_mode == 'High Contrast'
    
    st.markdown(f"""
    <style>
    /* Base font size adjustment */
    html, body, .stApp {{
        font-size: calc(16px * {size_mult}) !important;
    }}
    
    /* Theme body styles */
    .stApp {{
        background-color: {bg_primary} !important;
        color: {text_primary} !important;
    }}
    
    /* Sidebar styling - solid color, no gradient */
    .stApp [data-testid="stSidebar"],
    .stApp section[data-testid="stSidebar"] > div,
    section[data-testid="stSidebar"] {{
        background: {sidebar_bg} !important;
    }}
    
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] .stRadio label span,
    section[data-testid="stSidebar"] .stSelectbox label {{
        color: {sidebar_text} !important;
    }}
    
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {{
        color: {sidebar_text} !important;
        background: {'rgba(255, 255, 255, 0.1)' if is_dark_theme else 'rgba(79, 124, 243, 0.1)'};
        border-radius: 8px;
        padding: 0.5rem 1rem;
        margin: 0.25rem 0;
        transition: background 0.2s ease;
    }}
    
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {{
        background: {'rgba(255, 255, 255, 0.2)' if is_dark_theme else 'rgba(79, 124, 243, 0.2)'};
    }}
    
    /* High contrast specific overrides */
    {f'''
    .stApp p, .stApp span, .stApp label, .stApp div {{
        color: #FFFFFF !important;
    }}
    .stApp h1, .stApp h2, .stApp h3, .stApp h4 {{
        color: #FFD400 !important;
    }}
    .stApp a {{
        color: #00FFFF !important;
    }}
    .stApp button {{
        border: 2px solid #FFFFFF !important;
    }}
    .info-box, .stat-card, .feature-card {{
        background: #0A0A0A !important;
        border: 2px solid #FFFFFF !important;
    }}
    .info-box *, .stat-card *, .feature-card * {{
        color: #FFFFFF !important;
    }}
    ''' if is_high_contrast else ''}
    
    /* Main gradient header - keep gradient */
    .main-header {{
        background: linear-gradient(135deg, {COLOR_PRIMARY} 0%, {COLOR_INFO} 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(79, 124, 243, 0.3);
    }}
    
    .main-header h1 {{
        margin: 0;
        font-size: 2.5rem;
        color: white !important;
    }}
    
    .main-header p {{
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.2rem;
        color: white !important;
    }}
    
    /* Feature cards - solid colors with semantic borders */
    .feature-card {{
        background: {bg_card};
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        border-left: 5px solid;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    
    .feature-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
    }}
    
    .feature-card.green {{ border-left-color: {COLOR_SUCCESS}; }}
    .feature-card.blue {{ border-left-color: {COLOR_PRIMARY}; }}
    .feature-card.purple {{ border-left-color: {COLOR_INFO}; }}
    .feature-card.orange {{ border-left-color: {COLOR_WARNING}; }}
    .feature-card.pink {{ border-left-color: {COLOR_DANGER}; }}
    .feature-card.teal {{ border-left-color: {COLOR_SUCCESS}; }}
    
    .feature-card h3 {{
        margin: 0 0 0.5rem 0;
        color: {text_primary};
    }}
    
    .feature-card p {{
        margin: 0;
        color: {text_secondary};
    }}
    
    /* Info boxes - solid colors, no gradients */
    .info-box {{
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }}
    
    .info-box.success {{
        background: {'#0A0A0A' if is_high_contrast else ('#1E293B' if is_dark_theme else '#ECFDF5')};
        border: 2px solid {COLOR_SUCCESS};
        color: {text_primary};
    }}
    
    .info-box.warning {{
        background: {'#0A0A0A' if is_high_contrast else ('#1E293B' if is_dark_theme else '#FFFBEB')};
        border: 2px solid {COLOR_WARNING};
        color: {text_primary};
    }}
    
    .info-box.info {{
        background: {'#0A0A0A' if is_high_contrast else ('#1E293B' if is_dark_theme else '#EEF2FF')};
        border: 2px solid {COLOR_INFO};
        color: {text_primary};
    }}
    
    /* Welcome banner - keep gradient */
    .welcome-banner {{
        background: linear-gradient(135deg, {COLOR_PRIMARY}15 0%, {COLOR_INFO}15 100%);
        border: 2px solid {COLOR_PRIMARY};
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        margin-bottom: 1.5rem;
    }}
    
    .welcome-banner h2 {{
        color: {COLOR_PRIMARY if not is_high_contrast else '#FFD400'};
        margin: 0;
    }}
    
    /* Stats cards - solid colors */
    .stat-card {{
        background: {bg_card};
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border: 1px solid {border_color};
    }}
    
    .stat-card.green {{ border-left: 4px solid {COLOR_SUCCESS}; }}
    .stat-card.blue {{ border-left: 4px solid {COLOR_PRIMARY}; }}
    .stat-card.purple {{ border-left: 4px solid {COLOR_INFO}; }}
    .stat-card.orange {{ border-left: 4px solid {COLOR_WARNING}; }}
    
    /* Auth form styling */
    .auth-container {{
        background: {bg_card};
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        border: 1px solid {border_color};
    }}
    
    /* Button styling */
    .stButton > button[kind="primary"] {{
        background: {COLOR_PRIMARY};
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        color: white;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    
    .stButton > button[kind="primary"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(79, 124, 243, 0.4);
    }}
    
    .stButton > button[kind="secondary"] {{
        background: {bg_secondary};
        border: 2px solid {border_color};
        border-radius: 10px;
        color: {text_primary};
    }}
    
    /* Input styling */
    .stTextInput > div > div > input {{
        border-radius: 10px;
        border: 2px solid {border_color};
        padding: 0.75rem;
        background: {bg_card};
        color: {text_primary};
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: {COLOR_PRIMARY};
        box-shadow: 0 0 0 3px rgba(79, 124, 243, 0.2);
    }}
    
    /* Chat messages - solid colors */
    .chat-user {{
        background: {'#1E293B' if is_dark_theme else '#EEF2FF'};
        border-radius: 15px 15px 5px 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid {COLOR_PRIMARY};
        color: {text_primary};
    }}
    
    .chat-assistant {{
        background: {'#1E293B' if is_dark_theme else '#F5F3FF'};
        border-radius: 15px 15px 15px 5px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid {COLOR_INFO};
        color: {text_primary};
    }}
    
    /* Severity indicators - solid colors with semantic colors */
    .severity-high {{
        background: {'#0A0A0A' if is_high_contrast else ('#1E293B' if is_dark_theme else '#FEF2F2')};
        border: 2px solid {COLOR_DANGER};
        border-radius: 10px;
        padding: 1rem;
        color: {text_primary};
    }}
    
    .severity-medium {{
        background: {'#0A0A0A' if is_high_contrast else ('#1E293B' if is_dark_theme else '#FFFBEB')};
        border: 2px solid {COLOR_WARNING};
        border-radius: 10px;
        padding: 1rem;
        color: {text_primary};
    }}
    
    .severity-low {{
        background: {'#0A0A0A' if is_high_contrast else ('#1E293B' if is_dark_theme else '#ECFDF5')};
        border: 2px solid {COLOR_SUCCESS};
        border-radius: 10px;
        padding: 1rem;
        color: {text_primary};
    }}
    
    /* Language badge - solid color */
    .language-badge {{
        display: inline-block;
        background: {COLOR_INFO};
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
    }}
    
    /* Divider */
    .gradient-divider {{
        height: 3px;
        background: {COLOR_PRIMARY};
        border-radius: 2px;
        margin: 1.5rem 0;
    }}
    </style>
    """, unsafe_allow_html=True)

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
    if 'theme_mode' not in st.session_state:
        st.session_state.theme_mode = "Light"
    if 'text_size' not in st.session_state:
        st.session_state.text_size = "Medium"
    if 'family_members' not in st.session_state:
        st.session_state.family_members = []

def get_health_tip(language):
    tips = HEALTH_TIPS.get(language, HEALTH_TIPS.get("English", []))
    if tips:
        return random.choice(tips)
    return "💡 Stay healthy and take care of yourself!"

def get_recent_activity(patient_name, limit=5):
    activities = []
    
    appointments = data_manager.get_appointments(patient_name)
    for apt in appointments[-3:]:
        activities.append({
            "type": "appointment",
            "icon": "📅",
            "title": f"Appointment with Dr. {apt.get('doctor_name', 'Unknown')}",
            "date": apt.get('date', ''),
            "status": apt.get('status', 'Scheduled')
        })
    
    prescriptions = data_manager.get_prescriptions(patient_name)
    for presc in prescriptions[-3:]:
        activities.append({
            "type": "prescription",
            "icon": "💊",
            "title": f"Prescription from Dr. {presc.get('doctor_name', 'Unknown')}",
            "date": presc.get('date', ''),
            "status": "Active"
        })
    
    records = data_manager.get_health_records(patient_name)
    for rec in records[-3:]:
        activities.append({
            "type": "record",
            "icon": "📋",
            "title": rec.get('record_type', 'Health Record'),
            "date": rec.get('date', ''),
            "status": "Saved"
        })
    
    activities.sort(key=lambda x: x.get('date', ''), reverse=True)
    return activities[:limit]

def generate_prescription_pdf(prescription):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Arogya Mitra - Prescription", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Patient: {prescription.get('patient_name', 'N/A')}", ln=True)
    pdf.cell(0, 8, f"Doctor: {prescription.get('doctor_name', 'N/A')}", ln=True)
    pdf.cell(0, 8, f"Date: {prescription.get('date', 'N/A')}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Medication:", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 6, prescription.get('medication', 'N/A'))
    pdf.ln(3)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Dosage:", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 6, prescription.get('dosage', 'N/A'))
    pdf.ln(3)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Instructions:", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 6, prescription.get('instructions', 'N/A'))
    
    pdf.ln(10)
    pdf.set_font("Arial", "I", 9)
    pdf.cell(0, 6, "Generated by Arogya Mitra - Your Health Friend", ln=True, align="C")
    
    return pdf.output(dest='S').encode('latin-1')

def generate_health_record_pdf(record):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Arogya Mitra - Health Record", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Patient: {record.get('patient_name', 'N/A')}", ln=True)
    pdf.cell(0, 8, f"Record Type: {record.get('record_type', 'N/A')}", ln=True)
    pdf.cell(0, 8, f"Date: {record.get('date', 'N/A')}", ln=True)
    pdf.cell(0, 8, f"Language: {record.get('language', 'N/A')}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Description:", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 6, record.get('description', 'N/A'))
    
    pdf.ln(10)
    pdf.set_font("Arial", "I", 9)
    pdf.cell(0, 6, "Generated by Arogya Mitra - Your Health Friend", ln=True, align="C")
    
    return pdf.output(dest='S').encode('latin-1')

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
    inject_custom_css()
    
    st.markdown("""
    <div class="main-header">
        <h1>🏥 Arogya Mitra</h1>
        <p>आरोग्य मित्र - Your Multilingual Health Companion</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="auth-container">
            <h2 style="text-align: center; color: #667eea; margin-bottom: 1.5rem;">🔐 Welcome Back!</h2>
        </div>
        """, unsafe_allow_html=True)
        
        email = st.text_input("📧 Email", placeholder="Enter your email")
        password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Sign In", type="primary", use_container_width=True):
            if email and password:
                result = auth_manager.authenticate_user(email, password)
                if result["success"]:
                    st.session_state.authenticated = True
                    st.session_state.current_user = result["user"]
                    st.session_state.user_role = result["user"]["role"]
                    st.session_state.patient_name = result["user"]["name"]
                    st.session_state.user_language = result["user"].get("language", "English")
                    st.balloons()
                    st.success(f"🎉 Welcome back, {result['user']['name']}!")
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")
            else:
                st.warning("⚠️ Please enter both email and password")
        
        st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)
        
        st.markdown("<p style='text-align: center; color: #6b7280;'>New to Arogya Mitra?</p>", unsafe_allow_html=True)
        if st.button("✨ Create New Account", use_container_width=True):
            st.session_state.auth_page = "signup"
            st.rerun()
    
    st.markdown("""
    <div class="info-box info" style="text-align: center; margin-top: 2rem;">
        💡 <strong>Supported Languages:</strong> Hindi, Marathi, Tamil, Telugu, Bengali, Gujarati, Kannada, Malayalam, Punjabi & English
    </div>
    """, unsafe_allow_html=True)

def signup_page():
    inject_custom_css()
    
    st.markdown("""
    <div class="main-header">
        <h1>🏥 Arogya Mitra</h1>
        <p>आरोग्य मित्र - Join Our Health Community</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <h2 style="color: #667eea;">✨ Create Your Account</h2>
            <p style="color: #6b7280;">Start your journey to better health</p>
        </div>
        """, unsafe_allow_html=True)
        
        name = st.text_input("👤 Full Name", placeholder="Enter your full name")
        email = st.text_input("📧 Email", placeholder="Enter your email")
        phone = st.text_input("📱 Phone Number (optional)", placeholder="+91...")
        
        col_pass1, col_pass2 = st.columns(2)
        with col_pass1:
            password = st.text_input("🔑 Password", type="password", placeholder="Min 6 characters")
        with col_pass2:
            confirm_password = st.text_input("🔑 Confirm", type="password", placeholder="Confirm password")
        
        st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)
        
        st.markdown("#### 👤 I am a:")
        col_role1, col_role2 = st.columns(2)
        with col_role1:
            patient_selected = st.button("🏃 Patient", use_container_width=True, type="primary" if st.session_state.get('signup_role', 'Patient') == 'Patient' else "secondary")
            if patient_selected:
                st.session_state.signup_role = "Patient"
        with col_role2:
            doctor_selected = st.button("👨‍⚕️ Doctor", use_container_width=True, type="primary" if st.session_state.get('signup_role', 'Patient') == 'Doctor' else "secondary")
            if doctor_selected:
                st.session_state.signup_role = "Doctor"
        
        role = st.session_state.get('signup_role', 'Patient')
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        language = st.selectbox(
            "🌐 Preferred Language",
            options=list(ai_helper.SUPPORTED_LANGUAGES.keys()),
            index=0
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 Create My Account", type="primary", use_container_width=True):
            if not name or not email or not password:
                st.warning("⚠️ Please fill in all required fields")
            elif len(password) < 6:
                st.warning("⚠️ Password must be at least 6 characters")
            elif password != confirm_password:
                st.error("❌ Passwords do not match")
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
                    st.balloons()
                    st.success("🎉 Account created successfully! Please sign in.")
                    st.session_state.auth_page = "login"
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")
        
        st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)
        
        st.markdown("<p style='text-align: center; color: #6b7280;'>Already have an account?</p>", unsafe_allow_html=True)
        if st.button("⬅️ Back to Sign In", use_container_width=True):
            st.session_state.auth_page = "login"
            st.rerun()

def role_selection_page():
    if st.session_state.auth_page == "signup":
        signup_page()
    else:
        login_page()

def sidebar_navigation():
    inject_custom_css()
    
    theme_mode = st.session_state.get('theme_mode', 'Light')
    is_light_theme = theme_mode == 'Light'
    
    title_color = "#1e293b" if is_light_theme else "white"
    subtitle_color = "#64748b" if is_light_theme else "rgba(255,255,255,0.85)"
    user_bg = "rgba(79,124,243,0.1)" if is_light_theme else "rgba(255,255,255,0.1)"
    user_text_color = "#1e293b" if is_light_theme else "white"
    
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem 0;">
            <h1 style="color: {title_color}; margin: 0;">🏥 Arogya Mitra</h1>
            <p style="color: {subtitle_color}; margin: 0.25rem 0 0 0; font-size: 0.9rem;">आरोग्य मित्र - Your Health Friend</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.current_user:
            role_color = "#10b981" if st.session_state.user_role == "Patient" else "#3b82f6"
            st.markdown(f"""
            <div style="background: {user_bg}; border-radius: 10px; padding: 0.75rem; margin: 0.5rem 0; text-align: center;">
                <p style="color: {user_text_color}; margin: 0; font-weight: bold;">👤 {st.session_state.current_user['name']}</p>
                <span style="background: {role_color}; color: white; padding: 0.2rem 0.6rem; border-radius: 15px; font-size: 0.8rem;">{st.session_state.user_role}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        lang = st.session_state.user_language
        st.markdown(f"### 🌐 {get_text('language_preference', lang)}")
        selected_language = st.selectbox(
            get_text("select_language", lang),
            options=list(ai_helper.SUPPORTED_LANGUAGES.keys()),
            index=list(ai_helper.SUPPORTED_LANGUAGES.keys()).index(st.session_state.user_language)
        )
        if selected_language != st.session_state.user_language:
            st.session_state.user_language = selected_language
            if st.session_state.current_user:
                auth_manager.update_user(st.session_state.current_user['id'], language=selected_language)
                st.session_state.current_user['language'] = selected_language
                st.toast(f"Language saved: {selected_language}")
            st.rerun()
        st.session_state.user_language = selected_language
        
        st.markdown("---")
        
        menu_options = get_nav_items(st.session_state.user_role, lang)
        
        st.markdown("---")
        
        selected_menu = st.radio("Navigation", menu_options, label_visibility="collapsed", key="nav_radio")
        
        st.markdown("---")
        if st.button(f"🚪 {get_text('logout', lang)}", use_container_width=True):
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
    inject_custom_css()
    
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
        <h1>🔍 AI Symptom Checker</h1>
        <p>Describe your symptoms and get instant AI-powered analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="text-align: center; margin: 1rem 0;">
        <span class="language-badge">🌐 {st.session_state.user_language}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box warning">
        ⚠️ <strong>Important:</strong> This is not a medical diagnosis. Please consult a qualified doctor for proper medical advice.
    </div>
    """, unsafe_allow_html=True)
    
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
                        st.markdown("""
                        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 1rem; border-radius: 10px; text-align: center; margin: 1rem 0;">
                            <h2 style="margin: 0; color: white;">📊 Symptom Analysis Report</h2>
                            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">AI-powered health assessment</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        severity = analysis.get('severity_level', 'Unknown')
                        severity_colors = {
                            'Low': ('#10b981', '#d1fae5', '🟢'),
                            'Medium': ('#f59e0b', '#fef3c7', '🟡'),
                            'High': ('#ef4444', '#fee2e2', '🔴'),
                            'Critical': ('#dc2626', '#fecaca', '🚨')
                        }
                        sev_color, sev_bg, sev_icon = severity_colors.get(severity, ('#6b7280', '#f3f4f6', '⚪'))
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"""
                            <div style="background: {sev_bg}; border-left: 4px solid {sev_color}; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                                <p style="margin: 0; font-size: 0.85rem; color: #6b7280; font-weight: 600;">SEVERITY LEVEL</p>
                                <p style="margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: bold; color: {sev_color};">{sev_icon} {severity}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            urgent = analysis.get('urgent_care_needed', False)
                            if urgent:
                                st.markdown("""
                                <div style="background: #fee2e2; border-left: 4px solid #ef4444; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                                    <p style="margin: 0; font-size: 0.85rem; color: #6b7280; font-weight: 600;">URGENT CARE</p>
                                    <p style="margin: 0.5rem 0 0 0; font-size: 1.25rem; font-weight: bold; color: #ef4444;">⚠️ Seek Immediate Care</p>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown("""
                                <div style="background: #d1fae5; border-left: 4px solid #10b981; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                                    <p style="margin: 0; font-size: 0.85rem; color: #6b7280; font-weight: 600;">URGENT CARE</p>
                                    <p style="margin: 0.5rem 0 0 0; font-size: 1.25rem; font-weight: bold; color: #10b981;">✓ No Immediate Urgency</p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        summary = analysis.get('symptoms_summary', 'N/A')
                        st.markdown(f"""
                        <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 1.25rem; border-radius: 10px; margin-bottom: 1rem;">
                            <h4 style="margin: 0 0 0.75rem 0; color: #1e293b; display: flex; align-items: center; gap: 0.5rem;">
                                🧾 Summary
                            </h4>
                            <p style="margin: 0; color: #475569; line-height: 1.6;">{summary}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        conditions = analysis.get('possible_conditions', [])
                        if conditions:
                            conditions_html = "".join([f"<li style='margin: 0.5rem 0; color: #475569;'>{cond}</li>" for cond in conditions])
                            st.markdown(f"""
                            <div style="background: #fef3c7; border: 1px solid #fcd34d; padding: 1.25rem; border-radius: 10px; margin-bottom: 1rem;">
                                <h4 style="margin: 0 0 0.75rem 0; color: #92400e; display: flex; align-items: center; gap: 0.5rem;">
                                    🩺 Possible Conditions to Discuss
                                </h4>
                                <ul style="margin: 0; padding-left: 1.5rem;">{conditions_html}</ul>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        recommendations = analysis.get('recommendations', 'Please consult a doctor')
                        if isinstance(recommendations, list):
                            recs_html = "".join([f"<li style='margin: 0.5rem 0; color: #475569;'>{rec}</li>" for rec in recommendations])
                            recs_content = f"<ul style='margin: 0; padding-left: 1.5rem;'>{recs_html}</ul>"
                        else:
                            recs_content = f"<p style='margin: 0; color: #475569; line-height: 1.6;'>{recommendations}</p>"
                        
                        st.markdown(f"""
                        <div style="background: #dbeafe; border: 1px solid #93c5fd; padding: 1.25rem; border-radius: 10px; margin-bottom: 1rem;">
                            <h4 style="margin: 0 0 0.75rem 0; color: #1e40af; display: flex; align-items: center; gap: 0.5rem;">
                                ✅ Recommendations
                            </h4>
                            {recs_content}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        questions = analysis.get('follow_up_questions', [])
                        if questions:
                            questions_html = "".join([f"<li style='margin: 0.5rem 0; color: #475569;'>{q}</li>" for q in questions])
                            st.markdown(f"""
                            <div style="background: #f3e8ff; border: 1px solid #c4b5fd; padding: 1.25rem; border-radius: 10px; margin-bottom: 1rem;">
                                <h4 style="margin: 0 0 0.75rem 0; color: #7c3aed; display: flex; align-items: center; gap: 0.5rem;">
                                    ❓ Questions for Your Doctor
                                </h4>
                                <ul style="margin: 0; padding-left: 1.5rem;">{questions_html}</ul>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        if st.session_state.patient_name:
                            if st.button("💾 Save to Health Records", type="primary"):
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
                                st.markdown("""
                                <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 1rem; border-radius: 10px; text-align: center; margin: 1rem 0;">
                                    <h2 style="margin: 0; color: white;">📊 Voice Analysis Report</h2>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                severity = analysis.get('severity_level', 'Unknown')
                                severity_colors = {
                                    'Low': ('#10b981', '#d1fae5', '🟢'),
                                    'Medium': ('#f59e0b', '#fef3c7', '🟡'),
                                    'High': ('#ef4444', '#fee2e2', '🔴'),
                                    'Critical': ('#dc2626', '#fecaca', '🚨')
                                }
                                sev_color, sev_bg, sev_icon = severity_colors.get(severity, ('#6b7280', '#f3f4f6', '⚪'))
                                
                                st.markdown(f"""
                                <div style="background: {sev_bg}; border-left: 4px solid {sev_color}; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                                    <p style="margin: 0; font-size: 0.85rem; color: #6b7280; font-weight: 600;">SEVERITY: <span style="color: {sev_color}; font-size: 1.25rem;">{sev_icon} {severity}</span></p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                summary = analysis.get('symptoms_summary', 'N/A')
                                st.markdown(f"""
                                <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                                    <h4 style="margin: 0 0 0.5rem 0; color: #1e293b;">🧾 Summary</h4>
                                    <p style="margin: 0; color: #475569;">{summary}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                conditions = analysis.get('possible_conditions', [])
                                if conditions:
                                    conditions_html = "".join([f"<li style='margin: 0.25rem 0;'>{c}</li>" for c in conditions])
                                    st.markdown(f"""
                                    <div style="background: #fef3c7; border: 1px solid #fcd34d; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                                        <h4 style="margin: 0 0 0.5rem 0; color: #92400e;">🩺 Possible Conditions</h4>
                                        <ul style="margin: 0; padding-left: 1.5rem;">{conditions_html}</ul>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                if st.session_state.patient_name:
                                    if st.button("💾 Save Analysis", type="primary"):
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
    inject_custom_css()
    
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);">
        <h1>💬 AI Medical Chat Assistant</h1>
        <p>Ask health questions and get instant responses in your language</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="text-align: center; margin: 1rem 0;">
        <span class="language-badge">🌐 {st.session_state.user_language}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box info">
        💡 Ask me health-related questions in your preferred language! I'm here to help.
    </div>
    """, unsafe_allow_html=True)
    
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
    inject_custom_css()
    
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);">
        <h1>🌐 Patient-Doctor Translation</h1>
        <p>Real-time communication across languages</p>
    </div>
    """, unsafe_allow_html=True)
    
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
    inject_custom_css()
    
    if st.session_state.user_role == "Doctor":
        st.markdown("""
        <div class="main-header" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
            <h1>📝 Write Prescription</h1>
            <p>Create prescriptions with automatic translation</p>
        </div>
        """, unsafe_allow_html=True)
        
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
                        
                        action_col1, action_col2, action_col3 = st.columns(3)
                        with action_col1:
                            if st.button(f"🔊 Read Aloud", key=f"read_rx_{i}"):
                                text_to_read = rx.get('translated_text', rx.get('instructions', ''))
                                lang_code = ai_helper.SUPPORTED_LANGUAGES.get(rx.get('language', 'English'), 'en')
                                play_audio_text(text_to_read, lang_code)
                                st.success("Playing audio...")
                        
                        with action_col2:
                            pdf_data = generate_prescription_pdf(rx)
                            st.download_button(
                                label="📥 PDF",
                                data=pdf_data,
                                file_name=f"prescription_{rx['date']}_{i}.pdf",
                                mime="application/pdf",
                                key=f"pdf_rx_{i}"
                            )
                        
                        with action_col3:
                            share_text = f"Prescription from Dr. {rx['doctor_name']}\nMedication: {rx['medication']}\nDosage: {rx['dosage']}\nInstructions: {rx.get('instructions', '')}"
                            whatsapp_url = generate_whatsapp_share_url(share_text)
                            st.markdown(f"<a href='{whatsapp_url}' target='_blank' style='display:inline-block;background:#25D366;color:white;padding:0.5rem 1rem;border-radius:5px;text-decoration:none;'>📱 WhatsApp</a>", unsafe_allow_html=True)
            else:
                st.info("No prescriptions found. Visit a doctor to get prescriptions.")
        else:
            st.warning("Please enter your name in the sidebar to view prescriptions")

def health_records_page():
    inject_custom_css()
    
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #ec4899 0%, #db2777 100%);">
        <h1>📁 Health Records</h1>
        <p>Your digital health history in one place</p>
    </div>
    """, unsafe_allow_html=True)
    
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
                    
                    action_col1, action_col2, action_col3 = st.columns(3)
                    with action_col1:
                        if st.button(f"🔊 Read Aloud", key=f"read_rec_{i}"):
                            text_to_read = record.get('description', '')
                            lang_code = ai_helper.SUPPORTED_LANGUAGES.get(record.get('language', 'English'), 'en')
                            play_audio_text(text_to_read, lang_code)
                            st.success("Playing audio...")
                    
                    with action_col2:
                        pdf_data = generate_health_record_pdf(record)
                        st.download_button(
                            label="📥 PDF",
                            data=pdf_data,
                            file_name=f"health_record_{record['date']}_{i}.pdf",
                            mime="application/pdf",
                            key=f"pdf_rec_{i}"
                        )
                    
                    with action_col3:
                        share_text = f"Health Record: {record.get('record_type', 'Report')}\nDate: {record['date']}\nDescription: {record.get('description', '')[:200]}"
                        whatsapp_url = generate_whatsapp_share_url(share_text)
                        st.markdown(f"<a href='{whatsapp_url}' target='_blank' style='display:inline-block;background:#25D366;color:white;padding:0.5rem 1rem;border-radius:5px;text-decoration:none;'>📱 WhatsApp</a>", unsafe_allow_html=True)
        else:
            st.info("No health records yet. Use the Symptom Checker to create your first record.")
    else:
        st.warning("Please enter your name in the sidebar to view records")

def appointment_booking_page():
    inject_custom_css()
    
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);">
        <h1>📅 Book Appointment</h1>
        <p>Schedule your consultation with a doctor</p>
    </div>
    """, unsafe_allow_html=True)
    
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
    inject_custom_css()
    
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);">
        <h1>📅 Appointments Overview</h1>
        <p>Manage all your patient appointments</p>
    </div>
    """, unsafe_allow_html=True)
    
    appointments = data_manager.get_appointments()
    
    if appointments:
        st.success(f"Total appointments: {len(appointments)}")
        df = data_manager.get_appointments_dataframe()
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No appointments scheduled yet")

def reminders_page():
    inject_custom_css()
    
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%);">
        <h1>🔔 My Reminders</h1>
        <p>Never miss your medications or appointments</p>
    </div>
    """, unsafe_allow_html=True)
    
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

def medication_tracker_page():
    inject_custom_css()
    
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);">
        <h1>💊 Medication Tracker</h1>
        <p>Track and manage your medications</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.patient_name:
        tab1, tab2 = st.tabs(["📋 My Medications", "➕ Add Medication"])
        
        with tab1:
            medications = data_manager.get_medications(st.session_state.patient_name)
            
            if medications:
                st.success(f"You have {len(medications)} medication(s)")
                
                for med in medications:
                    status_color = "green" if med['status'] == "Active" else "orange"
                    st.markdown(f"""
                    <div class="feature-card {status_color}">
                        <h3>💊 {med['medication_name']}</h3>
                        <p><strong>Dosage:</strong> {med['dosage']} | <strong>Frequency:</strong> {med['frequency']}</p>
                        <p><strong>Started:</strong> {med['start_date']} | <strong>Status:</strong> {med['status']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if med['status'] == "Active":
                            if st.button(f"⏹️ Mark Complete", key=f"complete_{med['id']}"):
                                data_manager.update_medication(med['id'], status="Completed")
                                st.success("Medication marked as completed!")
                                st.rerun()
                    with col2:
                        if st.button(f"🗑️ Remove", key=f"delete_{med['id']}"):
                            data_manager.delete_medication(med['id'])
                            st.success("Medication removed!")
                            st.rerun()
            else:
                st.info("No medications being tracked. Add a medication to start tracking!")
        
        with tab2:
            st.markdown("### ➕ Add New Medication")
            
            col1, col2 = st.columns(2)
            with col1:
                med_name = st.text_input("Medication Name")
                dosage = st.text_input("Dosage (e.g., 500mg)")
                start_date = st.date_input("Start Date")
            
            with col2:
                frequency = st.selectbox("Frequency", [
                    "Once daily",
                    "Twice daily", 
                    "Three times daily",
                    "Every 8 hours",
                    "Every 12 hours",
                    "As needed",
                    "Weekly"
                ])
                end_date = st.date_input("End Date (optional)", value=None)
                notes = st.text_area("Notes (optional)")
            
            if st.button("➕ Add Medication", type="primary"):
                if med_name and dosage:
                    data_manager.add_medication(
                        patient_name=st.session_state.patient_name,
                        medication_name=med_name,
                        dosage=dosage,
                        frequency=frequency,
                        start_date=str(start_date),
                        end_date=str(end_date) if end_date else None,
                        notes=notes
                    )
                    st.success("✅ Medication added successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.warning("Please fill in medication name and dosage")
        
        st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)
        
        st.markdown("### 📅 Today's Schedule")
        active_meds = [m for m in data_manager.get_medications(st.session_state.patient_name) if m['status'] == 'Active']
        if active_meds:
            for med in active_meds:
                st.markdown(f"- 💊 **{med['medication_name']}** - {med['dosage']} ({med['frequency']})")
        else:
            st.info("No active medications scheduled for today")
    else:
        st.warning("Please enter your name in the sidebar")

def symptom_history_page():
    inject_custom_css()
    
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);">
        <h1>📊 Symptom History</h1>
        <p>Visualize your health journey over time</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.patient_name:
        records = data_manager.get_health_records(st.session_state.patient_name)
        symptom_records = [r for r in records if r.get('record_type') == 'Symptom Analysis']
        
        if symptom_records:
            st.success(f"Found {len(symptom_records)} symptom report(s)")
            
            st.markdown("### 📈 Symptom Timeline")
            
            dates = []
            severities = []
            severity_map = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}
            
            sorted_records = sorted(symptom_records, key=lambda x: x.get('date', ''))
            for record in sorted_records:
                dates.append(record.get('date', 'Unknown'))
                report_data = record.get('report_data', {})
                severity = report_data.get('severity', 'Medium') if isinstance(report_data, dict) else 'Medium'
                severities.append(severity_map.get(severity, 2))
            
            if dates and severities:
                import pandas as pd
                chart_data = pd.DataFrame({
                    'Date': dates,
                    'Severity Level': severities
                })
                st.bar_chart(chart_data.set_index('Date'))
                
                st.markdown("""
                <div class="info-box info">
                    <strong>📊 Severity Scale:</strong><br>
                    1 = Low | 2 = Medium | 3 = High | 4 = Critical
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)
            
            st.markdown("### 📋 Detailed History")
            for i, record in enumerate(symptom_records, 1):
                with st.expander(f"📄 Report #{i} - {record.get('date', 'Unknown')}"):
                    st.markdown(f"**Description:** {record.get('description', 'N/A')}")
                    if record.get('report_data'):
                        if isinstance(record['report_data'], dict):
                            st.markdown(f"**Severity:** {record['report_data'].get('severity', 'N/A')}")
                            if record['report_data'].get('possible_conditions'):
                                st.markdown("**Possible Conditions:**")
                                for cond in record['report_data'].get('possible_conditions', []):
                                    st.markdown(f"- {cond}")
        else:
            st.info("No symptom history yet. Use the Symptom Checker from the sidebar menu to record your first symptoms!")
    else:
        st.warning("Please enter your name in the sidebar")

def family_accounts_page():
    inject_custom_css()
    
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
        <h1>👨‍👩‍👧 Family Accounts</h1>
        <p>Manage health records for your family members</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.patient_name:
        tab1, tab2 = st.tabs(["👥 Family Members", "➕ Add Member"])
        
        with tab1:
            family_members = st.session_state.get('family_members', [])
            
            if family_members:
                st.success(f"You have {len(family_members)} family member(s)")
                
                for i, member in enumerate(family_members):
                    st.markdown(f"""
                    <div class="feature-card {'green' if member.get('relationship') == 'Child' else 'blue'}">
                        <h3>👤 {member['name']}</h3>
                        <p><strong>Relationship:</strong> {member.get('relationship', 'N/A')} | <strong>Age:</strong> {member.get('age', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"📋 View Records", key=f"view_family_{i}"):
                            st.session_state.patient_name = member['name']
                            st.rerun()
                    with col2:
                        if st.button(f"🗑️ Remove", key=f"remove_family_{i}"):
                            st.session_state.family_members.pop(i)
                            st.success(f"Removed {member['name']}")
                            st.rerun()
            else:
                st.info("No family members added yet. Add a family member to manage their health records!")
        
        with tab2:
            st.markdown("### ➕ Add Family Member")
            
            col1, col2 = st.columns(2)
            with col1:
                member_name = st.text_input("Family Member Name")
                relationship = st.selectbox("Relationship", [
                    "Spouse", "Child", "Parent", "Sibling", "Grandparent", "Other"
                ])
            
            with col2:
                age = st.number_input("Age", min_value=0, max_value=120, value=30)
                phone = st.text_input("Phone (optional)", placeholder="+91...")
            
            if st.button("➕ Add Family Member", type="primary"):
                if member_name:
                    new_member = {
                        "name": member_name,
                        "relationship": relationship,
                        "age": age,
                        "phone": phone,
                        "added_by": st.session_state.patient_name
                    }
                    if 'family_members' not in st.session_state:
                        st.session_state.family_members = []
                    st.session_state.family_members.append(new_member)
                    st.success(f"✅ Added {member_name} to your family!")
                    st.balloons()
                    st.rerun()
                else:
                    st.warning("Please enter the family member's name")
        
        st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box info">
            <strong>💡 Tip:</strong> You can switch between family members to view their health records, 
            prescriptions, and appointments. All data is kept separate for each family member.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Please enter your name in the sidebar")

def find_hospitals_page():
    inject_custom_css()
    
    theme_mode = st.session_state.get('theme_mode', 'Light')
    is_light_theme = theme_mode == 'Light'
    
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);">
        <h1>🏥 Find Nearby Hospitals</h1>
        <p>Locate hospitals and healthcare facilities near you</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.patient_name:
        user_id = st.session_state.current_user.get('id') if st.session_state.current_user else None
        
        tab1, tab2 = st.tabs(["🔍 Search Hospitals", "⭐ Saved Hospitals"])
        
        with tab1:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                indian_cities = [
                    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
                    "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
                    "Chandigarh", "Bhopal", "Indore", "Nagpur", "Patna",
                    "Thiruvananthapuram", "Kochi", "Coimbatore", "Visakhapatnam",
                    "Guwahati", "Bhubaneswar", "Ranchi", "Dehradun", "Shimla"
                ]
                city = st.selectbox("📍 Select City", options=indian_cities, index=0)
                
                custom_city = st.text_input("Or enter a different city/area", placeholder="e.g., Varanasi, Noida, Gurugram")
                if custom_city:
                    city = custom_city
            
            with col2:
                specialties = [
                    "All Specialties",
                    "General Medicine",
                    "Cardiology",
                    "Orthopedics",
                    "Pediatrics",
                    "Gynecology",
                    "Neurology",
                    "Oncology",
                    "Dermatology",
                    "ENT",
                    "Ophthalmology",
                    "Psychiatry",
                    "Emergency Care"
                ]
                specialty = st.selectbox("🏷️ Specialty Filter", options=specialties)
            
            if st.button("🔍 Search Hospitals", type="primary", use_container_width=True):
                with st.spinner("Finding hospitals near you..."):
                    result = ai_helper.find_nearby_hospitals(
                        city=city,
                        specialty=specialty if specialty != "All Specialties" else None,
                        language=st.session_state.user_language
                    )
                    
                    if result["success"]:
                        st.session_state.hospital_results = result["hospitals"]
                        st.session_state.hospital_search_city = city
                    else:
                        st.error(f"❌ {result['error']}")
            
            if 'hospital_results' in st.session_state and st.session_state.hospital_results:
                st.markdown(f"### 🏥 Hospitals near {st.session_state.get('hospital_search_city', city)}")
                st.markdown(f"Found **{len(st.session_state.hospital_results)}** hospitals")
                
                for i, hospital in enumerate(st.session_state.hospital_results):
                    hospital_type = hospital.get('type', 'Unknown')
                    type_color = "#10b981" if hospital_type == "Government" else "#6366f1"
                    emergency_badge = "🚨 24/7 Emergency" if hospital.get('emergency') else ""
                    rating = hospital.get('rating', 0)
                    stars = "⭐" * int(rating) + "☆" * (5 - int(rating))
                    
                    card_bg = "#ffffff" if is_light_theme else "#1e293b"
                    card_text = "#1e293b" if is_light_theme else "#ffffff"
                    card_subtext = "#64748b" if is_light_theme else "#94a3b8"
                    
                    st.markdown(f"""
                    <div style="background: {card_bg}; border-radius: 12px; padding: 1.25rem; margin: 1rem 0; 
                                border-left: 4px solid {type_color}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div>
                                <h3 style="color: {card_text}; margin: 0 0 0.5rem 0;">{hospital.get('name', 'Unknown Hospital')}</h3>
                                <p style="color: {card_subtext}; margin: 0.25rem 0; font-size: 0.9rem;">
                                    📍 {hospital.get('address', 'Address not available')}
                                </p>
                                <p style="color: {card_subtext}; margin: 0.25rem 0; font-size: 0.9rem;">
                                    📞 {hospital.get('phone', 'N/A')} | 📏 {hospital.get('distance_km', 'N/A')} km away
                                </p>
                            </div>
                            <div style="text-align: right;">
                                <span style="background: {type_color}; color: white; padding: 0.25rem 0.75rem; 
                                            border-radius: 20px; font-size: 0.8rem; font-weight: 600;">
                                    {hospital_type}
                                </span>
                                <p style="color: #f59e0b; margin: 0.5rem 0 0 0; font-size: 0.9rem;">{stars}</p>
                            </div>
                        </div>
                        <div style="margin-top: 0.75rem;">
                            <p style="color: {card_text}; margin: 0; font-size: 0.85rem;">
                                <strong>Specialties:</strong> {', '.join(hospital.get('specialties', ['General'])[:4])}
                            </p>
                            {f'<span style="background: #ef4444; color: white; padding: 0.2rem 0.5rem; border-radius: 10px; font-size: 0.75rem; margin-top: 0.5rem; display: inline-block;">{emergency_badge}</span>' if emergency_badge else ''}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("⭐ Save", key=f"save_hospital_{i}", use_container_width=True):
                            if user_id:
                                result = data_manager.add_saved_hospital(
                                    user_id=user_id,
                                    hospital_name=hospital.get('name', 'Unknown'),
                                    address=hospital.get('address', ''),
                                    phone=hospital.get('phone', ''),
                                    specialties=hospital.get('specialties', []),
                                    city=st.session_state.get('hospital_search_city', city),
                                    distance_km=hospital.get('distance_km')
                                )
                                if result.get("success"):
                                    st.success("✅ Hospital saved!")
                                else:
                                    st.info(result.get("error", "Already saved"))
                            else:
                                st.warning("Please log in to save hospitals")
                    
                    with col2:
                        phone = hospital.get('phone', '').replace('-', '').replace(' ', '').replace('+', '')
                        if phone:
                            st.markdown(f"""
                            <a href="tel:{phone}" target="_blank" style="text-decoration: none;">
                                <button style="width: 100%; background: #10b981; color: white; border: none; 
                                              padding: 0.5rem; border-radius: 8px; cursor: pointer;">
                                    📞 Call
                                </button>
                            </a>
                            """, unsafe_allow_html=True)
                    
                    with col3:
                        address_encoded = hospital.get('address', '').replace(' ', '+')
                        st.markdown(f"""
                        <a href="https://www.google.com/maps/search/?api=1&query={address_encoded}" target="_blank" style="text-decoration: none;">
                            <button style="width: 100%; background: #3b82f6; color: white; border: none; 
                                          padding: 0.5rem; border-radius: 8px; cursor: pointer;">
                                🗺️ Map
                            </button>
                        </a>
                        """, unsafe_allow_html=True)
        
        with tab2:
            st.markdown("### ⭐ Your Saved Hospitals")
            
            if user_id:
                saved_hospitals = data_manager.get_saved_hospitals(user_id)
                
                if saved_hospitals:
                    for hospital in saved_hospitals:
                        card_bg = "#ffffff" if is_light_theme else "#1e293b"
                        card_text = "#1e293b" if is_light_theme else "#ffffff"
                        card_subtext = "#64748b" if is_light_theme else "#94a3b8"
                        
                        st.markdown(f"""
                        <div style="background: {card_bg}; border-radius: 12px; padding: 1rem; margin: 0.75rem 0;
                                    border: 1px solid {'#e2e8f0' if is_light_theme else '#334155'};">
                            <h4 style="color: {card_text}; margin: 0 0 0.5rem 0;">🏥 {hospital.get('hospital_name', 'Unknown')}</h4>
                            <p style="color: {card_subtext}; margin: 0.25rem 0; font-size: 0.9rem;">
                                📍 {hospital.get('address', 'N/A')} | 📞 {hospital.get('phone', 'N/A')}
                            </p>
                            <p style="color: {card_subtext}; margin: 0.25rem 0; font-size: 0.85rem;">
                                🏷️ {', '.join(hospital.get('specialties', ['General'])[:3])}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            phone = hospital.get('phone', '').replace('-', '').replace(' ', '').replace('+', '')
                            if phone:
                                st.markdown(f"""
                                <a href="tel:{phone}" style="text-decoration: none;">
                                    <button style="width: 100%; background: #10b981; color: white; border: none; 
                                                  padding: 0.4rem; border-radius: 6px; cursor: pointer; font-size: 0.9rem;">
                                        📞 Call
                                    </button>
                                </a>
                                """, unsafe_allow_html=True)
                        with col2:
                            if st.button("🗑️ Remove", key=f"remove_saved_{hospital['id']}", use_container_width=True):
                                data_manager.delete_saved_hospital(hospital['id'])
                                st.success("Hospital removed")
                                st.rerun()
                else:
                    st.info("No saved hospitals yet. Search for hospitals and save your favorites!")
            else:
                st.warning("Please log in to view saved hospitals")
        
        st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box info">
            <strong>💡 Tip:</strong> Save your frequently visited hospitals for quick access. 
            You can directly call or view the location on maps.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Please enter your name in the sidebar")

def patient_records_doctor():
    inject_custom_css()
    
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
        <h1>📊 Patient Records</h1>
        <p>Access and manage patient health data</p>
    </div>
    """, unsafe_allow_html=True)
    
    search_patient = st.text_input("🔍 Search Patient by Name")
    
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
    inject_custom_css()
    lang = st.session_state.user_language
    
    user_name = st.session_state.current_user['name'] if st.session_state.current_user else st.session_state.user_role
    greeting = get_greeting(lang)
    
    st.markdown(f"""
    <div class="welcome-banner">
        <h2>🙏 {greeting}, {user_name}!</h2>
        <p style="color: #9d174d; margin-top: 0.5rem;">{get_text('welcome_message', lang)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    lang_display = st.session_state.user_language
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <span class="language-badge">🌐 {lang_display}</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.user_role == "Patient":
        health_tip = get_health_tip(st.session_state.user_language)
        st.markdown(f"""
        <div class="info-box info">
            <strong>💡 {get_text('health_tip', lang)}:</strong><br>
            {health_tip}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)
        
        st.markdown(f"### 📊 {get_text('recent_activity', lang)}")
        activities = get_recent_activity(st.session_state.patient_name)
        
        if activities:
            for activity in activities:
                st.markdown(f"""
                <div class="feature-card {'green' if activity['type'] == 'appointment' else 'orange' if activity['type'] == 'prescription' else 'blue'}">
                    <p style="margin: 0;"><strong>{activity['icon']} {activity['title']}</strong></p>
                    <p style="margin: 0.25rem 0 0 0; font-size: 0.9rem;">📅 {activity['date']} • Status: {activity['status']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(get_text('no_recent_activity', lang))
        
        st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)
        
        st.markdown(f"### 🎯 {get_text('features', lang)}")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="feature-card green">
                <h3>🔍 {get_text('symptom_checker_title', lang)}</h3>
                <p>{get_text('symptom_checker_desc', lang)}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="feature-card blue">
                <h3>💬 {get_text('chat_title', lang)}</h3>
                <p>{get_text('chat_desc', lang)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="feature-card purple">
                <h3>📅 {get_text('appointments_title', lang)}</h3>
                <p>{get_text('appointments_desc', lang)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        col4, col5, col6 = st.columns(3)
        
        with col4:
            st.markdown(f"""
            <div class="feature-card orange">
                <h3>📋 {get_text('prescriptions_title', lang)}</h3>
                <p>{get_text('prescriptions_desc', lang)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="feature-card pink">
                <h3>📁 {get_text('health_records_title', lang)}</h3>
                <p>{get_text('health_records_desc', lang)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col6:
            st.markdown(f"""
            <div class="feature-card teal">
                <h3>🔔 {get_text('reminders_title', lang)}</h3>
                <p>{get_text('reminders_desc', lang)}</p>
            </div>
            """, unsafe_allow_html=True)
        
    else:
        st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-card blue">
                <h3>🌐 Translation Chat</h3>
                <p>Communicate with patients in their native language in real-time</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("""
            <div class="feature-card green">
                <h3>📝 Smart Prescriptions</h3>
                <p>Write prescriptions that auto-translate to patient's language</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-card purple">
                <h3>💬 AI Assistant</h3>
                <p>Get AI-powered clinical insights and decision support</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col4, col5 = st.columns(2)
        
        with col4:
            st.markdown("""
            <div class="feature-card orange">
                <h3>📊 Patient Records</h3>
                <p>Access and manage comprehensive patient health data</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown("""
            <div class="feature-card pink">
                <h3>📅 Appointments</h3>
                <p>View and manage your appointment schedule</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box info">
            <strong>🌟 Doctor Features:</strong><br>
            ✅ Real-time translation chat &nbsp;|&nbsp; 
            ✅ Auto-translated prescriptions &nbsp;|&nbsp; 
            ✅ Patient record management &nbsp;|&nbsp; 
            ✅ AI clinical assistant
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box warning" style="text-align: center; margin-top: 1rem;">
        👆 <strong>Select an option from the sidebar menu to get started!</strong>
    </div>
    """, unsafe_allow_html=True)

def main():
    data_manager.ensure_data_directory()
    initialize_session_state()
    sync_theme_with_streamlit()
    
    if not st.session_state.authenticated:
        role_selection_page()
    else:
        menu = sidebar_navigation()
        lang = st.session_state.user_language
        menu_options = get_nav_items(st.session_state.user_role, lang)
        
        try:
            menu_index = menu_options.index(menu)
        except ValueError:
            menu_index = 0
        
        if st.session_state.user_role == "Patient":
            patient_pages = [
                home_page,
                symptom_checker_page,
                symptom_history_page,
                ai_chat_page,
                prescription_page,
                health_records_page,
                appointment_booking_page,
                reminders_page,
                medication_tracker_page,
                find_hospitals_page,
                family_accounts_page
            ]
            if menu_index < len(patient_pages):
                patient_pages[menu_index]()
            else:
                home_page()
        else:
            doctor_pages = [
                home_page,
                ai_chat_page,
                translation_chat_page,
                prescription_page,
                view_appointments_doctor,
                patient_records_doctor
            ]
            if menu_index < len(doctor_pages):
                doctor_pages[menu_index]()
            else:
                home_page()

if __name__ == "__main__":
    main()
