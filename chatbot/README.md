# DiaBeat AI — Intelligent Diabetes Management

DiaBeat AI is a futuristic healthcare assistant that helps manage diabetes through intelligent tracking, AI-powered insights, and smart reminders.

## Permanent Fix for "Neural Link Failed"

The "Neural Link Failed" error occurs when the frontend cannot communicate with the Python backend server. 

### How to Run (Recommended)
Simply double-click the **`start_app.bat`** file in the root directory. This will:
1. Start the FastAPI backend server.
2. Automatically open your browser to `http://127.0.0.1:8000`.

### Manual Start
If you prefer running commands manually:
1. Open a terminal in the project root.
2. Run the backend: `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`
3. Open `http://127.0.0.1:8000` in your browser.

## Features
- **Neural Bridge**: Real-time connectivity status indicator in the header.
- **AI Wellness Insights**: Intelligent summaries of your health data.
- **Smart Reminders**: Context-aware medication and hydration tracking.
- **Risk Analysis**: Machine learning models to predict hospital readmission.
