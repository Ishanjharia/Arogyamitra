# Arogya Mitra (आरोग्य मित्र) - Your Health Friend

## Project Overview
A comprehensive multilingual healthcare platform that enables seamless communication between patients and doctors in their preferred languages (Hindi, Marathi, Tamil, Telugu, Bengali, Gujarati, Kannada, Malayalam, Punjabi, and English).

## Current Status
**MVP Complete** - All core features implemented and tested
**AI Provider:** Switched to Google Gemini (FREE tier with generous limits)
**Authentication:** Complete user signup/login/logout system implemented
**Last Updated:** January 17, 2026

## Recent Updates (January 2026)
- Added Find Hospitals feature to locate nearby hospitals by city and specialty
- Added Medication Tracker with add/complete/delete capabilities
- Added Read Aloud functionality for prescriptions and health records (using gTTS)
- Added PDF Export for prescriptions and health records (using fpdf2)
- Added Quick Navigation from home page buttons
- Added WhatsApp Sharing for prescriptions and health records
- Added Symptom History Graph with visual timeline charts
- Added Family Accounts to manage health records for family members
- Added High Contrast Mode for accessibility (black bg, white/yellow text)
- Added Voice Commands for hands-free navigation
- Added Recent Activity Dashboard on home page
- Added Progress Indicators (loading spinners) throughout the app

## Key Features Implemented

### Patient Features
1. **Multilingual Symptom Checker**
   - Text and voice input for symptom description
   - AI-powered analysis with severity assessment
   - Structured medical reports
   - Save reports to health records

2. **AI Medical Chat Assistant**
   - Real-time health Q&A in preferred language
   - Context-aware responses
   - Medical information with disclaimers

3. **Prescription Management**
   - View prescriptions in preferred language
   - Auto-translated medication instructions
   - Digital prescription storage

4. **Appointment Booking**
   - Schedule appointments with doctors
   - Multilingual support
   - Automatic reminders

5. **Health Records**
   - Digital storage of symptom reports
   - Prescription history
   - Secure access

6. **Reminders**
   - Medication reminders
   - Appointment notifications
   - SMS integration (mock for MVP)

7. **Medication Tracker**
   - Add/track active medications
   - Mark medications as completed
   - Daily schedule view
   - Dosage and frequency tracking

8. **Accessibility Features**
   - Read Aloud for prescriptions and health records
   - PDF Export/Download for prescriptions and health records
   - Quick action buttons on home page
   - High Contrast Mode (black bg, white/yellow text)
   - Voice Commands for hands-free navigation
   - WhatsApp Sharing for easy sharing with family/doctors

9. **Symptom History**
   - Visual timeline graph showing symptom severity over time
   - Detailed history with expandable reports
   - Sorted by date for accurate visualization

10. **Family Accounts**
    - Add and manage family members
    - Switch between family members to view their records
    - Track health for children, parents, spouse

11. **Recent Activity Dashboard**
    - Shows last appointments, prescriptions, and health records
    - Quick overview of health journey on home page

12. **Find Hospitals**
    - Search hospitals by city (24+ major Indian cities)
    - Filter by medical specialty (Cardiology, Pediatrics, etc.)
    - View hospital details: address, phone, distance, type (Government/Private)
    - Save favorite hospitals for quick access
    - Direct call and Google Maps integration

### Doctor Features
1. **Patient-Doctor Translation Chat**
   - Real-time conversation translation
   - Bidirectional language support
   - Medical terminology accuracy

2. **Smart Prescription Writing**
   - Auto-translation to patient's language
   - Structured format
   - Digital storage

3. **Patient Records Access**
   - View patient history
   - Search by patient name
   - Comprehensive health data

4. **AI Chat Assistant**
   - Evidence-based medical insights
   - Differential diagnosis support
   - Clinical decision support

## Technical Architecture

### Core Modules
- **app.py** - Main Streamlit application with role-based UI and authentication
- **ai_helper.py** - Gemini API integration for translation, analysis, and chat
- **data_manager.py** - JSON-based data persistence with full CRUD operations
- **auth_manager.py** - User authentication with password hashing and session management

### Supported Languages
English, Hindi (हिंदी), Marathi (मराठी), Tamil (தமிழ்), Telugu (తెలుగు), Bengali (বাংলা), Gujarati (ગુજરાતી), Kannada (ಕನ್ನಡ), Malayalam (മലയാളം), Punjabi (ਪੰਜਾਬੀ)

### Dependencies
- **Streamlit** - Web UI framework
- **Google Gemini API** - AI-powered features (gemini-2.5-flash, gemini-2.5-pro)
- **SpeechRecognition** - Audio input processing
- **gTTS** - Text-to-speech output
- **audio-recorder-streamlit** - Voice recording component
- **Pandas** - Data management

### Environment Variables
- **GEMINI_API_KEY** - Required for all AI features (FREE tier available)
- **SESSION_SECRET** - Session management

## Data Storage
Location: `health_data/` directory
- `users.json` - User accounts (with hashed passwords)
- `appointments.json` - Appointment records
- `prescriptions.json` - Prescription data
- `health_records.json` - Patient health records
- `reminders.json` - Medication and appointment reminders

## Error Handling
All AI helper functions return structured responses:
```python
{
    "success": True/False,
    "data": ...,  # Response data
    "error": None or error message
}
```

The UI checks `success` before processing responses and displays user-friendly error messages when API calls fail or when GEMINI_API_KEY is not configured.

**Retry Logic:** Automatic retry with exponential backoff for API overload errors (503 UNAVAILABLE), with user-friendly message after max retries.

## Security Features
- **User Authentication** - Complete signup/login/logout system
- **Password Hashing** - SHA-256 with unique salt per user
- **Session Management** - Secure session state for authenticated users
- API key validation before Gemini calls
- No exposed secrets in code
- Structured error handling prevents crashes
- Environment-based configuration

## Workflow Configuration
- **Command:** `streamlit run app.py --server.port 5000`
- **Port:** 5000 (webview)
- **Auto-restart:** Enabled

## User Flows

### Patient Journey
1. Select "Patient" role
2. Choose preferred language
3. Enter name for personalization
4. Access features:
   - Describe symptoms (text/voice)
   - Chat with AI assistant
   - View prescriptions
   - Book appointments
   - Check health records
   - Manage reminders

### Doctor Journey
1. Select "Doctor" role
2. Choose working language
3. Access features:
   - Translate conversations with patients
   - Write and translate prescriptions
   - View patient records
   - Use AI clinical assistant
   - Manage appointments

## Future Enhancements (Next Phase)
- Full IVR/phone line integration for feature phones
- AI documentation assistant for auto-generating consultation notes
- Secure Arogyamitra Health Record digital locker with encryption
- Video/audio health education content library
- Telemedicine video consultation
- Advanced symptom analysis with medical knowledge base
- Multi-user authentication system
- Analytics dashboard for health trends
- Integration with diagnostic labs
- Real Twilio SMS integration

## Development Notes
- All AI calls use Google Gemini models (gemini-2.5-flash for speed, gemini-2.5-pro for complex reasoning)
- Gemini FREE tier: 60 requests/minute, no credit card required
- Automatic retry logic for API overload (503) errors with exponential backoff
- Error handling prevents crashes when API key is missing
- CRUD operations available for all data entities
- UI optimized for low digital literacy users
- Medical disclaimers included in all AI-generated content

## Testing Status
- ✅ App successfully runs on port 5000
- ✅ Role selection works
- ✅ Language switching functional
- ✅ Gemini API integration working
- ✅ Multilingual chat tested (Hindi)
- ✅ Error handling tested (API key validation and retry logic)
- ✅ End-to-end testing completed

## Known Limitations (MVP)
- SMS reminders are mocked (not actually sent)
- No user authentication system
- JSON file storage (suitable for MVP, not production scale)
- No IVR/phone support yet
- No video consultation capability
- Limited to development environment
