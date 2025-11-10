# AI Health Assistant - Local Setup Guide

This guide will help you run the AI Health Assistant on your local computer after downloading from Replit.

## Prerequisites

Before you begin, ensure you have:
- **Python 3.11** installed on your computer
- **pip** (Python package manager) - comes with Python
- **OpenAI API Key** - Get one from https://platform.openai.com/api-keys

## Installation Steps

### Step 1: Extract the Downloaded Files
1. Locate the downloaded `.zip` file from Replit
2. Right-click and select "Extract All" (Windows) or double-click (Mac)
3. Choose a location to extract the files

### Step 2: Open Terminal/Command Prompt
- **Windows**: Press `Win + R`, type `cmd`, press Enter
- **Mac**: Press `Cmd + Space`, type `terminal`, press Enter
- **Linux**: Press `Ctrl + Alt + T`

### Step 3: Navigate to Project Folder
```bash
cd path/to/extracted/folder
```
Replace `path/to/extracted/folder` with the actual path where you extracted the files.

### Step 4: Install Required Python Packages
Run this command to install all dependencies:

```bash
pip install streamlit openai pandas gtts pydub SpeechRecognition audio-recorder-streamlit python-dateutil
```

**Note:** If you have both Python 2 and 3 installed, you may need to use `pip3` instead of `pip`.

### Step 5: Set Up OpenAI API Key

You need to set your OpenAI API key as an environment variable.

#### Windows (Command Prompt):
```bash
set OPENAI_API_KEY=your-api-key-here
```

#### Windows (PowerShell):
```powershell
$env:OPENAI_API_KEY="your-api-key-here"
```

#### Mac/Linux:
```bash
export OPENAI_API_KEY=your-api-key-here
```

**Important:** Replace `your-api-key-here` with your actual OpenAI API key.

**For Permanent Setup (Recommended):**

Create a `.env` file in the project directory:
```bash
OPENAI_API_KEY=your-api-key-here
SESSION_SECRET=any-random-secret-string
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

### Step 6: Run the Application

Run this command:
```bash
streamlit run app.py --server.port 5000
```

The application will start and open automatically in your default web browser at:
```
http://localhost:5000
```

## Troubleshooting

### Problem: "Python is not recognized"
**Solution:** Python is not in your system PATH. Reinstall Python and check "Add Python to PATH" during installation.

### Problem: "pip is not recognized"
**Solution:** Try using `python -m pip` instead of `pip`:
```bash
python -m pip install streamlit openai pandas gtts pydub SpeechRecognition audio-recorder-streamlit python-dateutil
```

### Problem: "Port 5000 is already in use"
**Solution:** Either:
1. Stop the application using port 5000, or
2. Use a different port:
```bash
streamlit run app.py --server.port 8501
```

### Problem: Audio recording doesn't work
**Solution:** 
- Make sure your browser has microphone permissions enabled
- Use Chrome or Firefox for best compatibility
- Check that your microphone is properly connected

### Problem: OpenAI API errors
**Solution:**
- Verify your API key is correct
- Check that you have credits in your OpenAI account
- Ensure the environment variable is set correctly

## Project Structure

```
AI-Health-Assistant/
├── app.py                    # Main Streamlit application
├── ai_helper.py              # OpenAI integration module
├── data_manager.py           # Data storage and management
├── replit.md                 # Project documentation
├── LOCAL_SETUP_GUIDE.md      # This file
├── .streamlit/
│   └── config.toml          # Streamlit configuration
└── health_data/             # Data storage (created on first run)
    ├── appointments.json
    ├── prescriptions.json
    ├── health_records.json
    └── reminders.json
```

## Using the Application

### For Patients:
1. Select "Continue as Patient"
2. Choose your preferred language
3. Enter your name
4. Use features:
   - Describe symptoms (text or voice)
   - Chat with AI health assistant
   - View prescriptions in your language
   - Book appointments
   - Check health records
   - Set medication reminders

### For Doctors:
1. Select "Continue as Doctor"
2. Choose your working language
3. Use features:
   - Real-time translation with patients
   - Write and translate prescriptions
   - View patient records
   - Access AI clinical assistant
   - Manage appointments

## Supported Languages

The application supports:
- English
- हिंदी (Hindi)
- मराठी (Marathi)
- தமிழ் (Tamil)
- తెలుగు (Telugu)
- বাংলা (Bengali)
- ગુજરાતી (Gujarati)
- ಕನ್ನಡ (Kannada)
- മലയാളം (Malayalam)
- ਪੰਜਾਬੀ (Punjabi)

## Data Storage

All data is stored locally in JSON files within the `health_data/` folder:
- **appointments.json** - Appointment records
- **prescriptions.json** - Prescription data
- **health_records.json** - Patient health records and symptom analyses
- **reminders.json** - Medication and appointment reminders

**Note:** This data persists between sessions on your local computer.

## Updating the Application

If you make changes to the code:
1. Save the files
2. Stop the running application (Ctrl+C in terminal)
3. Run `streamlit run app.py --server.port 5000` again

Streamlit will automatically detect file changes and prompt you to rerun the app in most cases.

## Security Notes

- Never share your OpenAI API key publicly
- Keep your `.env` file secure and don't commit it to version control
- The application stores data locally - ensure your computer is secure
- For production use, implement proper authentication and use a database

## Getting Help

If you encounter issues:
1. Check the terminal/command prompt for error messages
2. Ensure all dependencies are installed correctly
3. Verify your OpenAI API key is valid
4. Check Python version: `python --version` (should be 3.11.x)

## Cost Considerations

This application uses OpenAI's API which incurs costs:
- **GPT-5** for chat, translation, and symptom analysis
- **Whisper** for voice transcription

Monitor your usage at: https://platform.openai.com/usage

## System Requirements

- **OS:** Windows 10/11, macOS 10.15+, or Linux
- **Python:** 3.11 or higher
- **RAM:** Minimum 4GB (8GB recommended)
- **Disk Space:** ~500MB for dependencies
- **Internet:** Required for AI features

## Next Steps

After successful setup:
1. Test the patient flow with symptom checker
2. Try the doctor interface with translation
3. Book a test appointment
4. Explore all multilingual features

Enjoy using your AI Health Assistant! 🏥
