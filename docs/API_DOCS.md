# 📡 API Documentation — LifePilot AI

Base URL (local): `https://lifeilotai-491066567011.europe-west1.run.app`
Base URL (production): `https://your-cloud-run-url.a.run.app`

Interactive docs: `{BASE_URL}/docs`

---

## Authentication

All protected endpoints require a Firebase ID token in the Authorization header:
Authorization: Bearer <firebase_id_token>

Get the token from the frontend:
```javascript
const token = await firebase.auth().currentUser.getIdToken();
```

---

## Endpoints

### Health Check
GET /health

Response: {"status": "healthy"}
---

### Authentication

#### Verify Token
POST /api/auth/verify

Headers: Authorization: Bearer <token>

Response: {

"valid": true,

"user": {"uid": "...", "email": "..."},

"profile": {...}

}
#### Get Current User
GET /api/auth/me

Headers: Authorization: Bearer <token>

Response: {"user": {...}, "profile": {...}}

---

### Tasks

#### Get All Tasks
GET /api/tasks

Headers: Authorization: Bearer <token>

Response: {"tasks": [...], "count": 5}

#### Get Today's Tasks
GET /api/tasks/today

Headers: Authorization: Bearer <token>

Response: {"tasks": [...], "count": 2}

#### Create Task
POST /api/tasks

Headers: Authorization: Bearer <token>

Body: {

"title": "Complete assignment",

"description": "Chapter 5 problems",

"category": "Study",

"priority": "high",

"deadline": "2025-01-15T18:00:00",

"estimatedMinutes": 90

}

Response: {created task object}

#### Update Task
PUT /api/tasks/{task_id}

Headers: Authorization: Bearer <token>

Body: {"status": "completed"}

Response: {updated task object}

#### Delete Task
DELETE /api/tasks/{task_id}

Headers: Authorization: Bearer <token>

Response: {"deleted": true, "task_id": "..."}

---

### Goals

#### Get All Goals
GET /api/goals

Headers: Authorization: Bearer <token>

Response: {"goals": [...], "count": 3}

#### Create Goal
POST /api/goals

Headers: Authorization: Bearer <token>

Body: {

"title": "Run a 5K",

"category": "Health",

"targetDate": "2025-06-01T00:00:00",

"milestones": [

{"title": "Run 1K", "done": false},

{"title": "Run 3K", "done": false}

]

}

#### Update Goal
PUT /api/goals/{goal_id}

Body: {"progress": 50, "milestones": [...]}

---

### Habits

#### Get All Habits
GET /api/habits

Response: {"habits": [...], "count": 4}

#### Create Habit
POST /api/habits

Body: {

"title": "Read for 20 minutes",

"frequency": "daily",

"category": "Learning"

}

#### Mark Habit Done Today
POST /api/habits/{habit_id}/complete

Response: {updated habit with new streak}

---

### AI Features

#### Smart Task Prioritization
POST /api/ai/prioritize

Response: {

"prioritized": [

{

"id": "task_id",

"title": "Task name",

"rank": 1,

"urgency_score": 9,

"importance_score": 8,

"reason": "Due in 2 hours with high priority",

"suggested_start": "Start immediately"

}

],

"summary": "You have 3 urgent tasks today..."

}

#### Deadline Risk Prediction
POST /api/ai/risk

Body: {"task_id": "abc123"}

Response: {

"risk_score": 0.85,

"risk_level": "high",

"reason": "Only 3 hours left for a 4-hour task",

"recommended_action": "Start immediately",

"best_start_time": "Right now",

"estimated_completion": "Tonight at 11 PM"

}

#### Generate Daily Plan
POST /api/ai/daily-plan

Response: {

"plan": [

{

"time": "9:00 AM",

"task": "Math assignment",

"duration": "90 minutes",

"tip": "Do hardest problems first"

}

],

"summary": "You have 4 tasks today...",

"brief": "Good morning! Today looks manageable...",

"total_hours": "4 hours 30 minutes",

"focus_tip": "Turn off notifications for the first 2 hours"

}

#### Task Breakdown
POST /api/ai/breakdown

Body: {

"task_id": "abc123",

"task_title": "Write research paper",

"task_description": "10 pages on climate change"

}

Response: {

"subtasks": [

"Research 5 credible sources (30 min)",

"Create outline with 5 sections (20 min)",

"Write introduction (25 min)"

],

"total_estimated_minutes": 240,

"first_step": "Open Google Scholar and search for climate change statistics",

"tip": "Write the body paragraphs before the introduction"

}

#### Emergency Rescue Mode
POST /api/ai/rescue

Body: {"task_id": "abc123"}

Response: {

"rescue_plan": ["Do X now (15 min)", "Do Y next (20 min)"],

"minimum_time_needed": "45 minutes",

"can_finish": true,

"critical_message": "Stop everything and start this right now",

"what_to_skip": "Skip the formatting for now, focus on content",

"success_probability": "80%"

}

#### Weekly Productivity Report
GET /api/ai/weekly-report

Response: {

"productivity_score": 78,

"grade": "B+",

"summary": "Good week overall...",

"wins": ["Completed 8 tasks", "Maintained reading habit"],

"missed_analysis": "3 tasks missed due to poor time estimation",

"top_insight": "You work best in morning hours",

"next_week_priorities": ["Start tasks earlier", "Break down large tasks"],

"motivational_close": "Great progress this week!"

}

---

### AI Chat

#### Send Message
POST /api/chat

Body: {

"message": "What should I work on right now?",

"history": [

{"role": "user", "content": "Hello"},

{"role": "assistant", "content": "Hi! How can I help?"}

]

}

Response: {

"response": "Based on your tasks, I recommend starting with..."

}

#### Get Chat History
GET /api/chat/history

Response: {"history": [...messages...]}

---

### Analytics

#### Get Analytics Overview
GET /api/analytics

Response: {

"overview": {

"total_tasks": 15,

"completed": 10,

"pending": 4,

"missed": 1,

"completion_rate": 66.7,

"total_habits": 3

},

"categories": {"Study": 8, "Work": 5, "Personal": 2},

"priorities": {"high": 6, "medium": 7, "low": 2},

"habit_stats": [{"title": "Reading", "streak": 7, ...}]

}

#### Get Weekly AI Report
GET /api/analytics/weekly

Response: {full weekly report object}