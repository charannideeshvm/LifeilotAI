from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from middleware.auth_middleware import get_current_user
from services import firestore_service as db
from services import gemini_service as ai

router = APIRouter()

class ChatMessage(BaseModel):
    role:    str   # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []

@router.post("")
async def send_chat(req: ChatRequest, user: dict = Depends(get_current_user)):
    """Send a message to the AI coach and get a response."""

    # Build context from user's actual data
    tasks       = await db.get_tasks(user["uid"])
    today_tasks = await db.get_todays_tasks(user["uid"])
    pending     = [t for t in tasks if t.get("status") != "completed"]
    urgent      = [t for t in pending if t.get("priority") in ("urgent", "high")]

    context = {
        "task_count":   len(pending),
        "today_tasks":  today_tasks,
        "urgent_tasks": urgent
    }

    # Convert history to plain dicts
    history = [{"role": m.role, "content": m.content} for m in req.history]

    response = await ai.chat_with_ai(req.message, history, context)

    # Save to Firestore chat history
    await db.save_chat_message(user["uid"], "user",      req.message)
    await db.save_chat_message(user["uid"], "assistant", response)

    return {"response": response}

@router.get("/history")
async def get_history(user: dict = Depends(get_current_user)):
    """Get the last 20 chat messages."""
    history = await db.get_chat_history(user["uid"])
    return {"history": history}