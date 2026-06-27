# 🔧 Installation Guide — LifePilot AI

## Prerequisites

Make sure you have these installed before starting:

| Tool | Version | Download |
|---|---|---|
| Python | 3.11 or newer | https://python.org |
| Node.js | 18 or newer | https://nodejs.org |
| Git | Any | https://git-scm.com |
| VS Code | Any | https://code.visualstudio.com |

You also need:
- A Google Account
- A Gemini API key from https://aistudio.google.com
- A Firebase project from https://console.firebase.google.com

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/YourUsername/LifePilotAI.git
cd LifePilotAI
```

## Step 2: Set Up Python Environment

```bash
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values:GEMINI_API_KEY=your_gemini_api_key_here

FIREBASE_SERVICE_ACCOUNT_PATH=firebase-service-account.json

APP_NAME=LifePilot AI

ENVIRONMENT=development

PORT=8000

ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500

## Step 4: Add Firebase Service Account

1. Go to Firebase Console → Project Settings → Service Accounts
2. Click "Generate new private key"
3. Download the JSON file
4. Rename it to `firebase-service-account.json`
5. Place it inside the `backend/` folder

## Step 5: Configure Firebase in Frontend

Open `frontend/js/firebase-config.js` and replace with your Firebase config:

```javascript
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};
```

Get this from Firebase Console → Project Settings → Your Apps → Web App.

## Step 6: Start the Backend

```bash
cd backend
python main.py
```

You should see:
INFO: Firebase Admin SDK initialized successfully

INFO: Uvicorn running on http://0.0.0.0:8000

## Step 7: Start the Frontend

In VS Code, right-click `frontend/index.html` → Open with Live Server.

The app will open at `http://127.0.0.1:5500/frontend/index.html`

## Step 8: Verify Everything Works

Visit these URLs to confirm:
- Frontend: `http://127.0.0.1:5500/frontend/index.html`
- Backend health: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`

---

## Common Issues

**`ModuleNotFoundError`** — Virtual environment not activated. Run `venv\Scripts\activate`.

**`firebase-service-account.json not found`** — Make sure the file is inside the `backend/` folder.

**`GEMINI_API_KEY is missing`** — Check your `.env` file is in the root folder, not inside backend.

**CORS error** — Make sure the backend is running on port 8000 and `.env` has the correct origins.