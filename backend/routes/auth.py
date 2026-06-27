from fastapi import APIRouter, Depends
from middleware.auth_middleware import get_current_user
from services import firestore_service as db

router = APIRouter()

@router.post("/verify")
async def verify_token(user: dict = Depends(get_current_user)):
    """Verify a Firebase token and return user info."""
    user_data = await db.get_user(user["uid"])
    return {"valid": True, "user": user, "profile": user_data}

@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    """Get the current user's profile from Firestore."""
    profile = await db.get_user(user["uid"])
    return {"user": user, "profile": profile}