from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Milestone(BaseModel):
    title: str
    done:  bool = False

class GoalCreate(BaseModel):
    title:       str               = Field(..., min_length=1, max_length=200)
    description: Optional[str]     = ""
    targetDate:  Optional[datetime] = None
    category:    Optional[str]     = "Personal"
    milestones:  Optional[List[Milestone]] = []

class GoalUpdate(BaseModel):
    title:       Optional[str]      = None
    description: Optional[str]      = None
    progress:    Optional[int]      = Field(None, ge=0, le=100)
    targetDate:  Optional[datetime] = None
    status:      Optional[str]      = None
    milestones:  Optional[List[dict]] = None

class GoalResponse(BaseModel):
    id:          str
    userId:      str
    title:       str
    description: Optional[str]
    targetDate:  Optional[str]
    progress:    Optional[int]
    milestones:  Optional[List[dict]]
    category:    Optional[str]
    status:      Optional[str]
    createdAt:   Optional[str]