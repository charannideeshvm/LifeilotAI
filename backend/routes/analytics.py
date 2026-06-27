from fastapi import APIRouter, Depends
from middleware.auth_middleware import get_current_user
from services import firestore_service as db
from services import gemini_service as ai
from datetime import datetime, timezone, timedelta

router = APIRouter()

@router.get("")
async def get_analytics(user: dict = Depends(get_current_user)):
    """Get comprehensive analytics for the user."""
    tasks  = await db.get_tasks(user["uid"])
    habits = await db.get_habits(user["uid"])

    total     = len(tasks)
    completed = [t for t in tasks if t.get("status") == "completed"]
    pending   = [t for t in tasks if t.get("status") == "pending"]
    missed    = [t for t in tasks if t.get("status") == "missed"]

    # Completion rate
    rate = round((len(completed) / total * 100), 1) if total > 0 else 0

    # Category breakdown
    categories = {}
    for t in tasks:
        cat = t.get("category", "Other")
        categories[cat] = categories.get(cat, 0) + 1

    # Priority breakdown
    priorities = {}
    for t in tasks:
        pri = t.get("priority", "medium")
        priorities[pri] = priorities.get(pri, 0) + 1

    # Habit stats
    habit_stats = []
    for h in habits:
        total_days    = len(h.get("completedDates", []))
        habit_stats.append({
            "title":         h.get("title"),
            "streak":        h.get("streak", 0),
            "total_days":    total_days,
            "longest_streak": h.get("longestStreak", 0)
        })

    return {
        "overview": {
            "total_tasks":       total,
            "completed":         len(completed),
            "pending":           len(pending),
            "missed":            len(missed),
            "completion_rate":   rate,
            "total_habits":      len(habits)
        },
        "categories":  categories,
        "priorities":  priorities,
        "habit_stats": habit_stats
    }

@router.get("/weekly")
async def get_weekly_report(user: dict = Depends(get_current_user)):
    """Generate a full weekly AI report."""
    tasks     = await db.get_tasks(user["uid"])
    habits    = await db.get_habits(user["uid"])
    completed = [t for t in tasks if t.get("status") == "completed"]
    missed    = [t for t in tasks if t.get("status") == "missed"]

    report = await ai.generate_weekly_report(
        completed, missed, habits, user.get("name", "User")
    )
    return report