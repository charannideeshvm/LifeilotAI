from fastapi import APIRouter, Depends, HTTPException
from middleware.auth_middleware import get_current_user
from services import firestore_service as db
from models.goal import GoalCreate, GoalUpdate

router = APIRouter()

@router.get("")
async def get_goals(user: dict = Depends(get_current_user)):
    goals = await db.get_goals(user["uid"])
    return {"goals": goals, "count": len(goals)}

@router.post("")
async def create_goal(goal: GoalCreate, user: dict = Depends(get_current_user)):
    goal_dict = goal.model_dump()
    if goal_dict.get("targetDate"):
        goal_dict["targetDate"] = goal_dict["targetDate"].isoformat()
    created = await db.create_goal(user["uid"], goal_dict)
    return created

@router.put("/{goal_id}")
async def update_goal(
    goal_id: str,
    updates: GoalUpdate,
    user: dict = Depends(get_current_user)
):
    update_dict = {k: v for k, v in updates.model_dump().items() if v is not None}
    updated = await db.update_goal(goal_id, user["uid"], update_dict)
    if not updated:
        raise HTTPException(status_code=404, detail="Goal not found")
    return updated

@router.delete("/{goal_id}")
async def delete_goal(goal_id: str, user: dict = Depends(get_current_user)):
    deleted = await db.delete_goal(goal_id, user["uid"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"deleted": True}