# 🚀 Deployment Guide — LifePilot AI

This guide deploys:
- **Backend** → Google Cloud Run
- **Frontend** → Firebase Hosting

---

## Prerequisites

Install these tools first:

```bash
# Google Cloud CLI
# Download from: https://cloud.google.com/sdk/docs/install

# Firebase CLI (already installed in Milestone 2)
npm install -g firebase-tools

# Verify installations
gcloud --version
firebase --version
```

---

## PART 1 — Deploy Backend to Google Cloud Run

### Step 1: Create the Dockerfile

Create `Dockerfile` in the root `LifePilotAI` folder:

```dockerfile
# Use official Python slim image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend folder
COPY backend/ ./backend/

# Copy the Firebase service account (will use Secret Manager in production)
# COPY backend/firebase-service-account.json ./backend/

# Set working directory to backend
WORKDIR /app/backend

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Start the FastAPI server
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Step 2: Update PORT for Cloud Run

Cloud Run uses port **8080** by default. Update `backend/main.py`:

```python
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
```

Add the `os` import at the top if not already there:
```python
import os
```

### Step 3: Authenticate with Google Cloud

```bash
gcloud auth login
```

This opens your browser. Sign in with your Google account.

### Step 4: Set Your Project

```bash
# Replace lifepilot-ai with your actual project ID
gcloud config set project lifepilot-ai
```

Verify it worked:
```bash
gcloud config get-value project
```

### Step 5: Enable Required APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

Each command takes about 30 seconds.

### Step 6: Store Secrets in Google Cloud Secret Manager

Never put your API keys in the Docker image. Use Secret Manager instead.

```bash
# Enable Secret Manager
gcloud services enable secretmanager.googleapis.com

# Store Gemini API key as a secret
echo -n "your_actual_gemini_api_key" | gcloud secrets create GEMINI_API_KEY --data-file=-

# Verify the secret was created
gcloud secrets list
```

### Step 7: Upload Firebase Service Account as Secret

```bash
gcloud secrets create FIREBASE_SERVICE_ACCOUNT \
  --data-file=backend/firebase-service-account.json
```

### Step 8: Update Backend to Read Secrets from Cloud

Create `backend/config_cloud.py`:

```python
import os
import json

def get_secret(secret_name: str) -> str:
    """
    Read a secret from Google Cloud Secret Manager.
    Falls back to environment variable if Secret Manager is unavailable.
    This lets the same code work locally and on Cloud Run.
    """
    try:
        from google.cloud import secretmanager
        client     = secretmanager.SecretManagerServiceClient()
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "lifepilot-ai")
        name       = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        response   = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception:
        # Fall back to environment variable (works locally)
        return os.getenv(secret_name, "")
```

Install the Secret Manager library:
```bash
pip install google-cloud-secret-manager
pip freeze > requirements.txt
```

### Step 9: Deploy to Cloud Run

Run this from the `LifePilotAI` root folder:

```bash
gcloud run deploy lifepilot-ai-backend \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars="GEMINI_API_KEY=your_gemini_api_key,ENVIRONMENT=production,PORT=8080,ALLOWED_ORIGINS=https://lifepilot-ai.web.app" \
  --memory 512Mi \
  --timeout 60
```

Replace `your_gemini_api_key` with your actual key.

This will:
1. Build a Docker container from your code
2. Push it to Google's container registry
3. Deploy it to Cloud Run
4. Give you a public URL

**The deployment takes 3–5 minutes.** At the end you will see:
Service URL: https://lifepilot-ai-backend-xxxx-uc.a.run.app

**Save this URL — you need it for the frontend.**

### Step 10: Verify the Backend is Live

Visit these URLs in your browser:
https://lifepilot-ai-backend-xxxx-uc.a.run.app

https://lifepilot-ai-backend-xxxx-uc.a.run.app/health

https://lifepilot-ai-backend-xxxx-uc.a.run.app/docs

All three should respond correctly.

---

## PART 2 — Deploy Frontend to Firebase Hosting

### Step 1: Update API URL in Frontend

Now that the backend has a real URL, update `frontend/js/utils.js`:

```javascript
// Replace this line
const API_BASE = 'http://localhost:8000';

// With your actual Cloud Run URL
const API_BASE = 'https://lifepilot-ai-backend-xxxx-uc.a.run.app';
```

### Step 2: Initialize Firebase Hosting

From the `LifePilotAI` root folder:

```bash
firebase login
firebase init hosting
```

You will be asked several questions. Answer exactly like this:
? Which Firebase project do you want to use?

→ Select: lifepilot-ai (your project)
? What do you want to use as your public directory?

→ Type: frontend
? Configure as a single-page app (rewrite all urls to /index.html)?

→ Type: N (No)
? Set up automatic builds with GitHub?

→ Type: N (No)
? File frontend/index.html already exists. Overwrite?

→ Type: N (No)

This creates a `firebase.json` file in your root folder.

### Step 3: Verify firebase.json

Open `firebase.json` and make sure it looks like this:

```json
{
  "hosting": {
    "public": "frontend",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "headers": [
      {
        "source": "**",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "no-cache"
          }
        ]
      }
    ]
  }
}
```

### Step 4: Deploy Frontend

```bash
firebase deploy --only hosting
```

At the end you will see:
Hosting URL: https://lifepilot-ai.web.app

**Visit that URL — your app is live on the internet.**

### Step 5: Update CORS for Production

Now that your frontend has a real URL, update the backend CORS settings.

Redeploy the backend with the new frontend URL in ALLOWED_ORIGINS:

```bash
gcloud run services update lifepilot-ai-backend \
  --region us-central1 \
  --set-env-vars="ALLOWED_ORIGINS=https://lifepilot-ai.web.app,http://localhost:5500,http://127.0.0.1:5500"
```

---

## PART 3 — Final Verification Checklist

Test every feature on the live deployment:
LIVE APP CHECKLIST

✅ https://lifepilot-ai.web.app loads

✅ Register creates an account

✅ Login works

✅ Dashboard loads with stats

✅ Create a task → saved to Firestore

✅ AI Daily Brief generates (calls Gemini)

✅ Today's Plan generates schedule

✅ Task breakdown works

✅ Goals page — create and update goal

✅ Habits page — create and mark done

✅ Analytics page loads data

✅ AI Weekly Report generates

✅ AI Chat responds

✅ Calendar shows task deadlines

✅ Dark mode works

✅ Mobile responsive layout works