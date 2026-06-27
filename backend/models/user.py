from pydantic import BaseModel
from typing import Optional

class UserSettings(BaseModel):
    darkMode:      bool = False
    notifications: bool = True
    timezone:      str  = "Asia/Kolkata"

class UserUpdate(BaseModel):
    displayName: Optional[str]         = None
    settings:    Optional[UserSettings] = None