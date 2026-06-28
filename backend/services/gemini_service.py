# =============================================
# LIFEPILOT AI - GEMINI AI SERVICE
# =============================================

import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import json
import re
from datetime import datetime

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=4)
MODEL_NAME = "gemini-2.5-flash"

# Initialize client lazily to avoid startup crash
_client = None

def get_client():
    global _client
    if _client is None:
        from google import genai
        from google.genai import types
        import os
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        _client = genai.Client(
            api_key=api_key,
            http_options={"api_version": "v1beta"}
        )
        logger.info("Gemini client initialized")
    return _client


def _safe_json(text: str) -> dict:
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {"raw": text}


async def _generate(prompt: str) -> str:
    from google.genai import types
    client = get_client()
    loop   = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        _executor,
        lambda: client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=2048,
            )
        )
    )
    return response.text


async def prioritize_tasks(tasks: list) -> dict:
    if not tasks:
        return {"prioritized": [], "summary": "No tasks to prioritize."}

    task_list = "\n".join([
        f"- ID:{t.get('id','?')} | {t.get('title','?')} | "
        f"Priority:{t.get('priority','medium')} | "
        f"Deadline:{t.get('deadline','none')} | "
        f"Status:{t.get('status','pending')}"
        for t in tasks[:20]
    ])

    prompt = (
        "You are LifePilot AI, an expert productivity coach.\n\n"
        f"A user has these tasks:\n{task_list}\n\n"
        f"Today is {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}.\n\n"
        "Analyze these tasks and return ONLY this JSON with no other text:\n"
        "{\n"
        '  "prioritized": [\n'
        "    {\n"
        '      "id": "task id",\n'
        '      "title": "task title",\n'
        '      "rank": 1,\n'
        '      "urgency_score": 8,\n'
        '      "importance_score": 9,\n'
        '      "reason": "Why this should be done first in 1-2 sentences",\n'
        '      "suggested_start": "Start now"\n'
        "    }\n"
        "  ],\n"
        '  "summary": "Overall 2-sentence productivity summary"\n'
        "}"
    )

    try:
        return _safe_json(await _generate(prompt))
    except Exception as e:
        logger.error(f"prioritize_tasks error: {e}")
        return {"error": str(e), "prioritized": [], "summary": "AI unavailable."}


async def predict_deadline_risk(task: dict) -> dict:
    prompt = (
        "You are LifePilot AI, a deadline risk predictor.\n\n"
        "Analyze this task and predict the risk of missing its deadline:\n"
        f"- Title: {task.get('title')}\n"
        f"- Description: {task.get('description', 'none')}\n"
        f"- Priority: {task.get('priority', 'medium')}\n"
        f"- Deadline: {task.get('deadline', 'not set')}\n"
        f"- Estimated time: {task.get('estimatedMinutes', 'unknown')} minutes\n"
        f"- Status: {task.get('status', 'pending')}\n"
        f"- Today: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}\n\n"
        "Return ONLY this JSON with no other text:\n"
        "{\n"
        '  "risk_score": 0.75,\n'
        '  "risk_level": "high",\n'
        '  "reason": "Why this task is at risk in 2 sentences",\n'
        '  "recommended_action": "Specific actionable advice",\n'
        '  "best_start_time": "Today at 7 PM",\n'
        '  "estimated_completion": "Tomorrow at 9 AM"\n'
        "}"
    )

    try:
        return _safe_json(await _generate(prompt))
    except Exception as e:
        logger.error(f"predict_risk error: {e}")
        return {"risk_score": 0, "risk_level": "unknown", "error": str(e)}


async def generate_daily_plan(tasks: list, user_name: str = "User") -> dict:
    if not tasks:
        return {
            "plan": [],
            "summary": "You have no tasks today. Great time to plan ahead!",
            "brief": "No tasks due today. Use this time to review your goals."
        }

    task_summary = "\n".join([
        f"- {t.get('title')} ({t.get('estimatedMinutes', 60)} min, "
        f"{t.get('priority', 'medium')} priority, due: {t.get('deadline', 'today')})"
        for t in tasks[:10]
    ])

    prompt = (
        f"You are LifePilot AI, a personal productivity coach for {user_name}.\n\n"
        f"Tasks to schedule today:\n{task_summary}\n\n"
        f"Today is {datetime.now().strftime('%A, %B %d, %Y')}.\n"
        f"Current time: {datetime.now().strftime('%I:%M %p')}.\n\n"
        "Create a realistic daily schedule and return ONLY this JSON with no other text:\n"
        "{\n"
        '  "plan": [\n'
        "    {\n"
        '      "time": "9:00 AM",\n'
        '      "task": "Task title",\n'
        '      "duration": "90 minutes",\n'
        '      "tip": "Brief focus tip for this task"\n'
        "    }\n"
        "  ],\n"
        '  "summary": "2-sentence overview of the day",\n'
        f'  "brief": "Motivating 3-sentence brief addressing {user_name} directly",\n'
        '  "total_hours": "X hours Y minutes",\n'
        '  "focus_tip": "One key focus tip for today"\n'
        "}"
    )

    try:
        return _safe_json(await _generate(prompt))
    except Exception as e:
        logger.error(f"daily_plan error: {e}")
        return {"error": str(e), "plan": [], "brief": "Could not generate plan."}


async def breakdown_task(task_title: str, task_description: str = "") -> dict:
    prompt = (
        "You are LifePilot AI, an expert at breaking down complex tasks.\n\n"
        f"Break this task into small, concrete, actionable subtasks:\n"
        f"Task: {task_title}\n"
        f"Description: {task_description or 'none'}\n\n"
        "Create 4 to 8 subtasks. Each should take 15-45 minutes.\n"
        "Return ONLY this JSON with no other text:\n"
        "{\n"
        '  "subtasks": ["Step 1 (20 min)", "Step 2 (15 min)"],\n'
        '  "total_estimated_minutes": 120,\n'
        '  "first_step": "The single easiest first action to start immediately",\n'
        '  "tip": "One productivity tip specific to this task"\n'
        "}"
    )

    try:
        return _safe_json(await _generate(prompt))
    except Exception as e:
        logger.error(f"breakdown_task error: {e}")
        return {"subtasks": [], "error": str(e)}


async def generate_smart_reminder(task: dict) -> dict:
    prompt = (
        "You are LifePilot AI. Generate a smart, helpful reminder for this task.\n\n"
        f"Task: {task.get('title')}\n"
        f"Deadline: {task.get('deadline', 'soon')}\n"
        f"Estimated time: {task.get('estimatedMinutes', 60)} minutes\n"
        f"Priority: {task.get('priority', 'medium')}\n"
        f"Current time: {datetime.now().strftime('%I:%M %p on %A')}\n\n"
        "Return ONLY this JSON with no other text:\n"
        "{\n"
        '  "reminder_message": "Your specific context-aware reminder message",\n'
        '  "urgency": "low/medium/high/critical",\n'
        '  "best_start_time": "e.g. Start at 6 PM today",\n'
        '  "motivational_note": "Short encouraging message"\n'
        "}"
    )

    try:
        return _safe_json(await _generate(prompt))
    except Exception as e:
        logger.error(f"smart_reminder error: {e}")
        return {"reminder_message": f"Don't forget: {task.get('title')}", "error": str(e)}


async def emergency_rescue(task: dict) -> dict:
    prompt = (
        "You are LifePilot AI in EMERGENCY RESCUE MODE.\n\n"
        f"Task: {task.get('title')}\n"
        f"Description: {task.get('description', 'none')}\n"
        f"Deadline: {task.get('deadline', 'in a few hours')}\n"
        f"Estimated time: {task.get('estimatedMinutes', 60)} minutes\n"
        f"Current time: {datetime.now().strftime('%I:%M %p')}\n\n"
        "Return ONLY this JSON with no other text:\n"
        "{\n"
        '  "rescue_plan": ["Step 1 (15 min)", "Step 2 (20 min)"],\n'
        '  "minimum_time_needed": "45 minutes",\n'
        '  "can_finish": true,\n'
        '  "critical_message": "Direct urgent message about what to do RIGHT NOW",\n'
        '  "what_to_skip": "Non-essential parts you can skip",\n'
        '  "success_probability": "75%"\n'
        "}"
    )

    try:
        return _safe_json(await _generate(prompt))
    except Exception as e:
        logger.error(f"emergency_rescue error: {e}")
        return {"rescue_plan": [], "error": str(e)}


async def productivity_coach_analysis(completed_tasks: list, missed_tasks: list) -> dict:
    completed_titles = [t.get('title', '?') for t in completed_tasks[:10]]
    missed_titles    = [t.get('title', '?') for t in missed_tasks[:10]]

    prompt = (
        "You are LifePilot AI, a supportive productivity coach.\n\n"
        f"Completed tasks: {completed_titles}\n"
        f"Missed tasks: {missed_titles}\n"
        f"Total completed: {len(completed_tasks)}\n"
        f"Total missed: {len(missed_tasks)}\n\n"
        "Return ONLY this JSON with no other text:\n"
        "{\n"
        '  "productivity_score": 72,\n'
        '  "strengths": ["Strength 1", "Strength 2"],\n'
        '  "areas_to_improve": ["Area 1", "Area 2"],\n'
        '  "procrastination_detected": false,\n'
        '  "procrastination_insight": "Insight if detected",\n'
        '  "top_recommendation": "The single most important thing to change",\n'
        '  "encouragement": "A personalized encouraging message",\n'
        '  "next_week_goal": "One specific goal for next week"\n'
        "}"
    )

    try:
        return _safe_json(await _generate(prompt))
    except Exception as e:
        logger.error(f"coach_analysis error: {e}")
        return {"productivity_score": 0, "error": str(e)}


async def chat_with_ai(message: str, history: list, context: dict = None) -> str:
    context_block = ""
    if context:
        task_count  = context.get('task_count', 0)
        urgent      = context.get('urgent_tasks', [])
        today_tasks = context.get('today_tasks', [])
        context_block = (
            "\nCurrent user context:\n"
            f"- Total pending tasks: {task_count}\n"
            f"- Tasks due today: {[t.get('title') for t in today_tasks[:5]]}\n"
            f"- Urgent tasks: {[t.get('title') for t in urgent[:3]]}\n"
            f"- Current time: {datetime.now().strftime('%I:%M %p on %A, %B %d')}\n"
        )

    history_text = ""
    for msg in history[-6:]:
        role    = "User" if msg.get("role") == "user" else "Assistant"
        content = msg.get("content", "")
        if content:
            history_text += f"{role}: {content}\n"

    prompt = (
        "You are LifePilot AI, a friendly expert productivity coach.\n"
        "Be concise, practical, warm, and motivating.\n"
        + context_block
        + "\nConversation history:\n"
        + history_text
        + f"\nUser: {message}\nAssistant:"
    )

    try:
        return await _generate(prompt)
    except Exception as e:
        logger.error(f"chat error: {e}")
        return f"I'm having trouble connecting right now. Please try again. (Error: {str(e)[:100]})"


async def generate_weekly_report(completed: list, missed: list, habits: list, user_name: str = "User") -> dict:
    prompt = (
        f"You are LifePilot AI generating a weekly report for {user_name}.\n\n"
        f"Tasks completed: {len(completed)}\n"
        f"Completed titles: {[t.get('title','?') for t in completed[:5]]}\n"
        f"Tasks missed: {len(missed)}\n"
        f"Missed titles: {[t.get('title','?') for t in missed[:5]]}\n"
        f"Habits tracked: {len(habits)}\n\n"
        "Return ONLY this JSON with no other text:\n"
        "{\n"
        '  "productivity_score": 78,\n'
        '  "grade": "B+",\n'
        '  "summary": "2-3 sentence overall summary",\n'
        '  "wins": ["Win 1", "Win 2"],\n'
        '  "missed_analysis": "Why tasks were likely missed",\n'
        '  "focus_score": 72,\n'
        '  "habit_consistency": "Good/Fair/Poor with brief note",\n'
        '  "top_insight": "Most important insight from this week",\n'
        '  "next_week_priorities": ["Priority 1", "Priority 2"],\n'
        f'  "motivational_close": "Uplifting closing message for {user_name}"\n'
        "}"
    )

    try:
        return _safe_json(await _generate(prompt))
    except Exception as e:
        logger.error(f"weekly_report error: {e}")
        return {"error": str(e), "productivity_score": 0}