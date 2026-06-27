# =============================================
# LIFEPILOT AI - AUTH MIDDLEWARE
# =============================================
# This verifies Firebase ID tokens sent from the frontend.
# Every protected API endpoint calls get_current_user().

from fastapi import HTTPException, Header
from firebase_admin import auth as firebase_auth
import logging
from typing import Optional

logger = logging.getLogger(__name__)

async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Dependency function — FastAPI injects this into route handlers.
    
    The frontend sends: Authorization: Bearer <firebase_id_token>
    We verify that token with Firebase and return the user info.
    
    Usage in a route:
        @router.get("/protected")
        async def my_route(user = Depends(get_current_user)):
            return {"user_id": user["uid"]}
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is missing. Please log in."
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization format. Expected: Bearer <token>"
        )

    token = authorization.split("Bearer ")[1]

    try:
        # Firebase verifies the token signature and expiry
        decoded = firebase_auth.verify_id_token(token)
        return {
            "uid":   decoded["uid"],
            "email": decoded.get("email", ""),
            "name":  decoded.get("name", "")
        }
    except firebase_auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")
    except firebase_auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid token. Please log in again.")
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed.")