# 🧭 LifePilot AI — Never Miss What Matters

> An AI-powered productivity companion that predicts missed deadlines, builds intelligent schedules, and coaches you to peak performance.

[![Deploy on Google Cloud Run](https://img.shields.io/badge/Deploy-Google%20Cloud%20Run-4285F4?logo=google-cloud)](https://cloud.google.com/run)
[![Powered by Gemini](https://img.shields.io/badge/AI-Google%20Gemini-8E44AD)](https://aistudio.google.com)
[![Firebase](https://img.shields.io/badge/Database-Firebase%20Firestore-FFA000?logo=firebase)](https://firebase.google.com)

---

## 🌐 Live Demo

- **Frontend:** https://lifepilot-ai.web.app
- **Backend API:** https://lifepilot-ai-backend-xxxx-uc.a.run.app
- **API Docs:** https://lifepilot-ai-backend-xxxx-uc.a.run.app/docs

---

## 🚀 What is LifePilot AI?

Most reminder apps only notify users. LifePilot AI **actively helps users complete tasks** before deadlines. It acts like a personal AI productivity coach powered by Google Gemini.

### The Problem
Students, professionals, and entrepreneurs miss assignments, meetings, bill payments, and deadlines — not because they forget, but because they have no intelligent system helping them prioritize and plan.

### The Solution
LifePilot AI uses Google Gemini to:
- Predict which tasks you will likely miss
- Build a personalized daily schedule
- Break large tasks into small steps
- Give context-aware reminders
- Coach you based on your actual performance

---

## ✨ Features

### Core Features
- ✅ Task Management (Create, Edit, Delete, Complete)
- ✅ Goal Tracking with Milestones and Progress
- ✅ Habit Tracking with Streak Counter
- ✅ Calendar View with Task Deadlines
- ✅ Analytics Dashboard
- ✅ Dark Mode
- ✅ Responsive Design (Mobile + Desktop)

### AI Features (Powered by Gemini)
- 🤖 Smart Task Prioritization
- ⚠️ Deadline Risk Prediction
- 📅 Daily AI Planner
- 🔪 Task Breakdown into Subtasks
- 💬 Context-Aware Reminders
- 🚨 Emergency Rescue Mode
- 📊 Weekly Productivity Report
- 🧠 AI Productivity Coach
- 💬 AI Chat Assistant

---

## 🛠️ Google Technologies Used

| Technology | Purpose |
|---|---|
| **Gemini 2.5 Flash** | All AI features — planning, coaching, chat |
| **Google AI Studio** | API key creation and prompt testing |
| **Firebase Authentication** | User login and registration |
| **Firebase Firestore** | Database for all app data |
| **Google Cloud Run** | Backend deployment |
| **Firebase Hosting** | Frontend deployment |

---

## 🏗️ Architecture

---

## ⚡ Quick Start

See [INSTALLATION.md](docs/INSTALLATION.md) for full setup instructions.

```bash
# Clone the repository
git clone https://github.com/YourUsername/LifePilotAI.git
cd LifePilotAI

# Set up Python environment
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start backend
cd backend
python main.py

# Open frontend with Live Server in VS Code
```

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

Built with ❤️ for Vibe2Ship · Powered by Google Gemini · Deployed on Google Cloud