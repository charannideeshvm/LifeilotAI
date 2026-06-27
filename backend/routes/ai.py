from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from middleware.auth_middleware import get_current_user
from services import firestore_service as db
from services import gemini_service as ai

router = APIRouter()

# --- Request Models ---
class BreakdownRequest(BaseModel):
    task_id:          str
    task_title:       str
    task_description: Optional[str] = ""

class RiskRequest(BaseModel):
    task_id: str

class RescueRequest(BaseModel):
    task_id: str

# --- Endpoints ---

@router.post("/prioritize")
async def prioritize_tasks(user: dict = Depends(get_current_user)):
    """Rank all user tasks by urgency and importance using Gemini."""
    tasks  = await db.get_tasks(user["uid"])
    result = await ai.prioritize_tasks(tasks)
    return result

@router.post("/risk")
async def predict_risk(req: RiskRequest, user: dict = Depends(get_current_user)):
    """Predict deadline risk for a specific task."""
    task = await db.get_task(req.task_id, user["uid"])
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    result = await ai.predict_deadline_risk(task)
    # Save the risk score back to Firestore
    if "risk_score" in result:
        await db.update_task(req.task_id, user["uid"], {
            "riskScore":    result["risk_score"],
            "aiSuggestion": result.get("recommended_action", "")
        })
    return result

@router.post("/daily-plan")
async def daily_plan(user: dict = Depends(get_current_user)):
    """Generate a personalized daily schedule."""
    tasks  = await db.get_todays_tasks(user["uid"])
    # If no tasks today, use upcoming tasks
    if not tasks:
        all_tasks = await db.get_tasks(user["uid"])
        tasks     = [t for t in all_tasks if t.get("status") != "completed"][:8]
    result = await ai.generate_daily_plan(tasks, user.get("name", "User"))
    return result

@router.post("/daily-brief")
async def daily_brief(user: dict = Depends(get_current_user)):
    """Get a short personalized daily brief from Gemini."""
    tasks  = await db.get_tasks(user["uid"])
    pending = [t for t in tasks if t.get("status") != "completed"]
    result  = await ai.generate_daily_plan(pending[:8], user.get("name", "User"))
    return {"brief": result.get("brief", "Have a productive day!")}

@router.post("/breakdown")
async def breakdown_task(req: BreakdownRequest, user: dict = Depends(get_current_user)):
    """Break a task into smaller subtasks."""
    result = await ai.breakdown_task(req.task_title, req.task_description)
    # Save subtasks to Firestore
    if result.get("subtasks") and req.task_id:
        subtasks = [
            {"id": str(i), "title": s, "done": False}
            for i, s in enumerate(result["subtasks"])
        ]
        await db.update_task(req.task_id, user["uid"], {"subtasks": subtasks})
    return result

@router.post("/reminder")
async def smart_reminder(req: RiskRequest, user: dict = Depends(get_current_user)):
    """Generate a context-aware reminder for a task."""
    task   = await db.get_task(req.task_id, user["uid"])
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return await ai.generate_smart_reminder(task)

@router.post("/rescue")
async def rescue_mode(req: RescueRequest, user: dict = Depends(get_current_user)):
    """Emergency rescue mode for a task with a tight deadline."""
    task = await db.get_task(req.task_id, user["uid"])
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return await ai.emergency_rescue(task)

@router.post("/coach")
async def productivity_coach(user: dict = Depends(get_current_user)):
    """Get personalized productivity coaching based on task history."""
    tasks     = await db.get_tasks(user["uid"])
    completed = [t for t in tasks if t.get("status") == "completed"]
    missed    = [t for t in tasks if t.get("status") == "missed"]
    return await ai.productivity_coach_analysis(completed, missed)

@router.get("/weekly-report")
async def weekly_report(user: dict = Depends(get_current_user)):
    """Generate a weekly productivity report."""
    tasks     = await db.get_tasks(user["uid"])
    habits    = await db.get_habits(user["uid"])
    completed = [t for t in tasks if t.get("status") == "completed"]
    missed    = [t for t in tasks if t.get("status") == "missed"]
    return await ai.generate_weekly_report(
        completed, missed, habits, user.get("name", "User")
    )