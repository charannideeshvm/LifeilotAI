from fastapi import APIRouter, Depends, HTTPException
from middleware.auth_middleware import get_current_user
from services import firestore_service as db
from models.habit import HabitCreate, HabitUpdate

router = APIRouter()

@router.get("")
async def get_habits(user: dict = Depends(get_current_user)):
    habits = await db.get_habits(user["uid"])
    return {"habits": habits, "count": len(habits)}

@router.post("")
async def create_habit(habit: HabitCreate, user: dict = Depends(get_current_user)):
    created = await db.create_habit(user["uid"], habit.model_dump())
    return created

@router.put("/{habit_id}")
async def update_habit(
    habit_id: str,
    updates: HabitUpdate,
    user: dict = Depends(get_current_user)
):
    updated = await db.update_habit(habit_id, user["uid"], updates.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Habit not found")
    return updated

@router.post("/{habit_id}/complete")
async def complete_habit(habit_id: str, user: dict = Depends(get_current_user)):
    updated = await db.complete_habit_today(habit_id, user["uid"])
    if not updated:
        raise HTTPException(status_code=404, detail="Habit not found")
    return updated

@router.delete("/{habit_id}")
async def delete_habit(habit_id: str, user: dict = Depends(get_current_user)):
    deleted = await db.delete_habit(habit_id, user["uid"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Habit not found")
    return {"deleted": True}