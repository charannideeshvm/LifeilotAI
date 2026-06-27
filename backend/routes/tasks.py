from fastapi import APIRouter, Depends, HTTPException
from middleware.auth_middleware import get_current_user
from services import firestore_service as db
from models.task import TaskCreate, TaskUpdate

router = APIRouter()

@router.get("")
async def get_tasks(user: dict = Depends(get_current_user)):
    """Get all tasks for the logged-in user."""
    tasks = await db.get_tasks(user["uid"])
    return {"tasks": tasks, "count": len(tasks)}

@router.get("/today")
async def get_today_tasks(user: dict = Depends(get_current_user)):
    """Get tasks due today."""
    tasks = await db.get_todays_tasks(user["uid"])
    return {"tasks": tasks, "count": len(tasks)}

@router.get("/{task_id}")
async def get_task(task_id: str, user: dict = Depends(get_current_user)):
    task = await db.get_task(task_id, user["uid"])
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("")
async def create_task(task: TaskCreate, user: dict = Depends(get_current_user)):
    """Create a new task."""
    task_dict = task.model_dump()
    # Convert datetime to ISO string for Firestore service
    if task_dict.get("deadline"):
        task_dict["deadline"] = task_dict["deadline"].isoformat()
    created = await db.create_task(user["uid"], task_dict)
    return created

@router.put("/{task_id}")
async def update_task(
    task_id: str,
    updates: TaskUpdate,
    user: dict = Depends(get_current_user)
):
    """Update a task."""
    update_dict = {k: v for k, v in updates.model_dump().items() if v is not None}
    if update_dict.get("deadline"):
        update_dict["deadline"] = update_dict["deadline"].isoformat()
    updated = await db.update_task(task_id, user["uid"], update_dict)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@router.delete("/{task_id}")
async def delete_task(task_id: str, user: dict = Depends(get_current_user)):
    """Delete a task."""
    deleted = await db.delete_task(task_id, user["uid"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"deleted": True, "task_id": task_id}