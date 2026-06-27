from pydantic import BaseModel, Field
from typing import Optional, List

class HabitCreate(BaseModel):
    title:       str            = Field(..., min_length=1, max_length=200)
    frequency:   str            = "daily"   # daily or weekly
    targetDays:  Optional[List[str]] = ["mon","tue","wed","thu","fri","sat","sun"]
    category:    Optional[str]  = "Personal"

class HabitUpdate(BaseModel):
    title:      Optional[str]       = None
    frequency:  Optional[str]       = None
    targetDays: Optional[List[str]] = None
    category:   Optional[str]       = None

class HabitResponse(BaseModel):
    id:             str
    userId:         str
    title:          str
    frequency:      Optional[str]
    targetDays:     Optional[List[str]]
    streak:         Optional[int]
    longestStreak:  Optional[int]
    completedDates: Optional[List[str]]
    category:       Optional[str]
    createdAt:      Optional[str]