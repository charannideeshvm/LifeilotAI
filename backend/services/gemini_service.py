# =============================================
# LIFEPILOT AI - GEMINI AI SERVICE
# =============================================
# This file handles ALL communication with Google's Gemini AI.
# Every AI feature calls a function from this file.

import google.generativeai as genai
import logging
import json
import re
from datetime import datetime

from config import settings

logger = logging.getLogger(__name__)

# --- Configure Gemini ---
# This sets up the API key once. After this, we can call genai.GenerativeModel()
genai.configure(api_key=settings.GEMINI_API_KEY)

# We use gemini-1.5-flash — it's fast and free-tier friendly
MODEL_NAME = "gemini-1.5-flash"

def _get_model():
    """Return a configured Gemini model instance."""
    return genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config={
            "temperature":     0.7,   # 0=robotic/precise, 1=creative/varied
            "max_output_tokens": 1024,
            "top_p":           0.95,
        }
    )

def _safe_json(text: str) -> dict:
    """
    Try to extract JSON from Gemini's response.
    Gemini sometimes wraps JSON in ```json ... ``` code blocks.
    This function strips those wrappers before parsing.
    """
    # Remove markdown code fences
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()

    # Find JSON object in the text
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # If JSON parsing fails, return raw text in a dict
    return {"raw": text}

# =============================================
# AI FEATURE 1 — SMART TASK PRIORITIZATION
# =============================================

async def prioritize_tasks(tasks: list) -> dict:
    """
    Given a list of tasks, ask Gemini to rank them by urgency and importance.
    Returns a ranked list with explanations.
    """
    if not tasks:
        return {"prioritized": [], "summary": "No tasks to prioritize."}

    # Build a readable list of tasks for the prompt
    task_list = "\n".join([
        f"- ID:{t.get('id','?')} | {t.get('title','?')} | "
        f"Priority:{t.get('priority','medium')} | "
        f"Deadline:{t.get('deadline','none')} | "
        f"Status:{t.get('status','pending')}"
        for t in tasks[:20]  # Limit to 20 to keep prompt short
    ])

    prompt = f"""You are LifePilot AI, an expert productivity coach.

A user has these tasks:
{task_list}

Today is {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}.

Analyze these tasks and return a JSON object with this exact structure:
{{
  "prioritized": [
    {{
      "id": "task id",
      "title": "task title",
      "rank": 1,
      "urgency_score": 8,
      "importance_score": 9,
      "reason": "Why this should be done first in 1-2 sentences",
      "suggested_start": "When to start e.g. Start now, Start at 3 PM"
    }}
  ],
  "summary": "Overall 2-sentence productivity summary for the user"
}}

Rank by combining urgency (deadline proximity) and importance (priority level).
Return ONLY the JSON, no other text."""

    try:
        model    = _get_model()
        response = model.generate_content(prompt)
        return _safe_json(response.text)
    except Exception as e:
        logger.error(f"prioritize_tasks error: {e}")
        return {"error": str(e), "prioritized": [], "summary": "AI unavailable."}

# =============================================
# AI FEATURE 2 — DEADLINE RISK PREDICTION
# =============================================

async def predict_deadline_risk(task: dict) -> dict:
    """
    For a single task, predict the risk of missing its deadline.
    Returns risk score (0-1), reason, and recommended action.
    """
    prompt = f"""You are LifePilot AI, a deadline risk predictor.

Analyze this task and predict the risk of missing its deadline:
- Title: {task.get('title')}
- Description: {task.get('description', 'none')}
- Priority: {task.get('priority', 'medium')}
- Deadline: {task.get('deadline', 'not set')}
- Estimated time needed: {task.get('estimatedMinutes', 'unknown')} minutes
- Current status: {task.get('status', 'pending')}
- Today: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}

Return ONLY this JSON structure:
{{
  "risk_score": 0.75,
  "risk_level": "high",
  "reason": "Why this task is at risk in 2 sentences",
  "recommended_action": "Specific actionable advice e.g. Start immediately, spend 2 hours on it tonight",
  "best_start_time": "e.g. Today at 7 PM",
  "estimated_completion": "e.g. Tomorrow at 9 AM"
}}

risk_score is a float between 0.0 (no risk) and 1.0 (definitely missed).
risk_level is one of: low, medium, high."""

    try:
        model    = _get_model()
        response = model.generate_content(prompt)
        return _safe_json(response.text)
    except Exception as e:
        logger.error(f"predict_risk error: {e}")
        return {"risk_score": 0, "risk_level": "unknown", "error": str(e)}

# =============================================
# AI FEATURE 3 — DAILY PLANNER
# =============================================

async def generate_daily_plan(tasks: list, user_name: str = "User") -> dict:
    """
    Create a personalized daily schedule based on the user's tasks.
    """
    if not tasks:
        return {
            "plan":    [],
            "summary": "You have no tasks today. Great time to plan ahead!",
            "brief":   "No tasks due today. Use this time to review your goals and plan the week ahead."
        }

    task_summary = "\n".join([
        f"- {t.get('title')} ({t.get('estimatedMinutes', 60)} min, {t.get('priority', 'medium')} priority, due: {t.get('deadline', 'today')})"
        for t in tasks[:10]
    ])

    prompt = f"""You are LifePilot AI, a personal productivity coach for {user_name}.

Tasks to schedule today:
{task_summary}

Today is {datetime.now().strftime('%A, %B %d, %Y')}.
Current time: {datetime.now().strftime('%I:%M %p')}.

Create a realistic daily schedule. Consider:
- Morning for difficult/important tasks (9 AM - 12 PM)
- Short breaks every 90 minutes
- Lighter tasks in the afternoon
- Leave buffer time between tasks

Return ONLY this JSON:
{{
  "plan": [
    {{
      "time": "9:00 AM",
      "task": "Task title",
      "duration": "90 minutes",
      "tip": "Brief focus tip for this task"
    }}
  ],
  "summary": "2-sentence overview of the day",
  "brief": "Motivating 3-sentence daily brief addressing {user_name} directly",
  "total_hours": "X hours Y minutes",
  "focus_tip": "One key focus tip for today"
}}"""

    try:
        model    = _get_model()
        response = model.generate_content(prompt)
        return _safe_json(response.text)
    except Exception as e:
        logger.error(f"daily_plan error: {e}")
        return {"error": str(e), "plan": [], "brief": "Could not generate plan."}

# =============================================
# AI FEATURE 4 — TASK BREAKDOWN
# =============================================

async def breakdown_task(task_title: str, task_description: str = "") -> dict:
    """
    Break a large task into small, actionable subtasks.
    """
    prompt = f"""You are LifePilot AI, an expert at breaking down complex tasks.

Break this task into small, concrete, actionable subtasks:
Task: {task_title}
Description: {task_description or 'none'}

Rules:
- Create 4 to 8 subtasks
- Each subtask should take 15-45 minutes
- Be very specific and actionable
- Order them logically

Return ONLY this JSON:
{{
  "subtasks": [
    "Open the textbook and read sections 3.1 to 3.3",
    "Write a summary of key concepts in your own words",
    "Attempt practice problems 1-5",
    "Check answers and note mistakes",
    "Review mistakes and redo incorrect problems"
  ],
  "total_estimated_minutes": 120,
  "first_step": "The single easiest first action to get started immediately",
  "tip": "One productivity tip specific to this task"
}}"""

    try:
        model    = _get_model()
        response = model.generate_content(prompt)
        return _safe_json(response.text)
    except Exception as e:
        logger.error(f"breakdown_task error: {e}")
        return {"subtasks": [], "error": str(e)}

# =============================================
# AI FEATURE 5 — CONTEXT-AWARE REMINDER
# =============================================

async def generate_smart_reminder(task: dict) -> dict:
    """
    Generate a smart, context-aware reminder instead of a generic one.
    """
    prompt = f"""You are LifePilot AI. Generate a smart, helpful reminder for this task.

Task: {task.get('title')}
Deadline: {task.get('deadline', 'soon')}
Estimated time: {task.get('estimatedMinutes', 60)} minutes
Priority: {task.get('priority', 'medium')}
Current time: {datetime.now().strftime('%I:%M %p on %A')}

Instead of saying "Task due tomorrow", generate a specific, actionable reminder.
Example: "You need about 2 hours for this. To finish comfortably, start by 6 PM today."

Return ONLY this JSON:
{{
  "reminder_message": "Your specific context-aware reminder message",
  "urgency": "low/medium/high/critical",
  "best_start_time": "e.g. Start at 6 PM today",
  "motivational_note": "Short encouraging message"
}}"""

    try:
        model    = _get_model()
        response = model.generate_content(prompt)
        return _safe_json(response.text)
    except Exception as e:
        logger.error(f"smart_reminder error: {e}")
        return {"reminder_message": f"Don't forget: {task.get('title')}", "error": str(e)}

# =============================================
# AI FEATURE 6 — EMERGENCY RESCUE MODE
# =============================================

async def emergency_rescue(task: dict) -> dict:
    """
    Deadline is very close — create the fastest possible completion plan.
    """
    prompt = f"""You are LifePilot AI in EMERGENCY RESCUE MODE.

This task has a very close deadline. Create the fastest possible plan:
Task: {task.get('title')}
Description: {task.get('description', 'none')}
Deadline: {task.get('deadline', 'in a few hours')}
Estimated time: {task.get('estimatedMinutes', 60)} minutes
Current time: {datetime.now().strftime('%I:%M %p')}

Create a fast, no-nonsense completion plan. Cut out all non-essentials.
Focus on the minimum viable completion.

Return ONLY this JSON:
{{
  "rescue_plan": [
    "Step 1: Do X right now (15 min)",
    "Step 2: Do Y immediately after (20 min)",
    "Step 3: Final step (10 min)"
  ],
  "minimum_time_needed": "45 minutes",
  "can_finish": true,
  "critical_message": "Direct, urgent message about what to do RIGHT NOW",
  "what_to_skip": "Non-essential parts you can skip or do later",
  "success_probability": "75%"
}}"""

    try:
        model    = _get_model()
        response = model.generate_content(prompt)
        return _safe_json(response.text)
    except Exception as e:
        logger.error(f"emergency_rescue error: {e}")
        return {"rescue_plan": [], "error": str(e)}

# =============================================
# AI FEATURE 7 — PRODUCTIVITY COACH
# =============================================

async def productivity_coach_analysis(completed_tasks: list, missed_tasks: list) -> dict:
    """
    Analyze completed and missed tasks to give productivity coaching insights.
    """
    completed_titles = [t.get('title','?') for t in completed_tasks[:10]]
    missed_titles    = [t.get('title','?') for t in missed_tasks[:10]]

    prompt = f"""You are LifePilot AI, a supportive productivity coach.

Analyze this user's recent performance:
Completed tasks: {completed_titles}
Missed tasks: {missed_titles}
Total completed: {len(completed_tasks)}
Total missed: {len(missed_tasks)}

Provide honest, constructive, encouraging coaching.

Return ONLY this JSON:
{{
  "productivity_score": 72,
  "strengths": ["What the user is doing well"],
  "areas_to_improve": ["What needs improvement"],
  "procrastination_detected": true,
  "procrastination_insight": "Specific insight about their procrastination patterns if detected",
  "top_recommendation": "The single most important thing to change",
  "encouragement": "A personalized encouraging message",
  "next_week_goal": "One specific goal for next week"
}}"""

    try:
        model    = _get_model()
        response = model.generate_content(prompt)
        return _safe_json(response.text)
    except Exception as e:
        logger.error(f"coach_analysis error: {e}")
        return {"productivity_score": 0, "error": str(e)}

# =============================================
# AI FEATURE 8 — AI CHAT ASSISTANT
# =============================================

async def chat_with_ai(message: str, history: list, context: dict = None) -> str:
    """
    Multi-turn conversation with the AI coach.
    history is a list of {"role": "user/assistant", "content": "..."}
    context contains the user's tasks and goals for personalized answers.
    """
    # Build a context block if we have user data
    context_block = ""
    if context:
        task_count  = context.get('task_count', 0)
        urgent      = context.get('urgent_tasks', [])
        today_tasks = context.get('today_tasks', [])
        context_block = f"""
Current user context:
- Total pending tasks: {task_count}
- Tasks due today: {[t.get('title') for t in today_tasks[:5]]}
- Urgent tasks: {[t.get('title') for t in urgent[:3]]}
- Current time: {datetime.now().strftime('%I:%M %p on %A, %B %d')}
"""

    system_prompt = f"""You are LifePilot AI, a friendly, expert productivity coach.
You help users manage tasks, beat procrastination, and hit their goals.
Be concise, practical, warm, and motivating.
When giving plans or lists, use clear numbered steps.
{context_block}
You have access to the user's task data. Use it to give personalized advice.
If asked to reschedule or prioritize, give specific actionable suggestions."""

    # Convert history to Gemini's format
    # Gemini expects alternating user/model turns
    gemini_history = []
    for msg in history[-8:]:  # Last 8 messages for context
        role    = "user"  if msg.get("role") == "user" else "model"
        content = msg.get("content", "")
        if content:
            gemini_history.append({"role": role, "parts": [content]})

    try:
        model = _get_model()
        # Start a chat session with history
        chat  = model.start_chat(history=gemini_history)
        # Send the new message with the system prompt prepended
        full_message = f"{system_prompt}\n\nUser: {message}"
        response     = chat.send_message(full_message)
        return response.text
    except Exception as e:
        logger.error(f"chat error: {e}")
        return f"I'm having trouble connecting right now. Please try again in a moment. (Error: {str(e)[:100]})"

# =============================================
# AI FEATURE 9 — WEEKLY PRODUCTIVITY REPORT
# =============================================

async def generate_weekly_report(
    completed: list, missed: list,
    habits: list, user_name: str = "User"
) -> dict:
    """
    Generate a full weekly productivity report with AI insights.
    """
    prompt = f"""You are LifePilot AI generating a weekly productivity report for {user_name}.

This week's data:
- Tasks completed: {len(completed)} ({[t.get('title','?') for t in completed[:5]]})
- Tasks missed: {len(missed)} ({[t.get('title','?') for t in missed[:5]]})
- Habits tracked: {len(habits)}

Generate a comprehensive, encouraging, honest weekly report.

Return ONLY this JSON:
{{
  "productivity_score": 78,
  "grade": "B+",
  "summary": "2-3 sentence overall summary",
  "wins": ["Specific win 1", "Specific win 2"],
  "missed_analysis": "Why tasks were likely missed and pattern",
  "focus_score": 72,
  "habit_consistency": "Good/Fair/Poor with brief note",
  "top_insight": "The most important insight from this week",
  "next_week_priorities": ["Priority 1", "Priority 2", "Priority 3"],
  "motivational_close": "Uplifting closing message for {user_name}"
}}"""

    try:
        model    = _get_model()
        response = model.generate_content(prompt)
        return _safe_json(response.text)
    except Exception as e:
        logger.error(f"weekly_report error: {e}")
        return {"error": str(e), "productivity_score": 0}