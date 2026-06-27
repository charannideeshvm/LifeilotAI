# =============================================
# LIFEPILOT AI - TASK MODELS
# =============================================

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums enforce that only allowed values can be used
class TaskStatus(str, Enum):
    PENDING     = "pending"
    IN_PROGRESS = "in-progress"
    COMPLETED   = "completed"
    MISSED      = "missed"

class TaskPriority(str, Enum):
    LOW    = "low"
    MEDIUM = "medium"
    HIGH   = "high"
    URGENT = "urgent"

class TaskCategory(str, Enum):
    STUDY    = "Study"
    WORK     = "Work"
    PERSONAL = "Personal"
    HEALTH   = "Health"
    FINANCE  = "Finance"
    OTHER    = "Other"

class Subtask(BaseModel):
    id:    str
    title: str
    done:  bool = False

class TaskCreate(BaseModel):
    """Data required to create a new task."""
    title:             str          = Field(..., min_length=1, max_length=200)
    description:       Optional[str] = ""
    category:          TaskCategory  = TaskCategory.OTHER
    priority:          TaskPriority  = TaskPriority.MEDIUM
    deadline:          Optional[datetime] = None
    estimatedMinutes:  Optional[int] = Field(None, ge=5, le=1440)
    tags:              Optional[List[str]] = []

class TaskUpdate(BaseModel):
    """All fields are optional for updates — only send what changed."""
    title:            Optional[str]          = None
    description:      Optional[str]          = None
    category:         Optional[TaskCategory] = None
    priority:         Optional[TaskPriority] = None
    status:           Optional[TaskStatus]   = None
    deadline:         Optional[datetime]     = None
    estimatedMinutes: Optional[int]          = None
    tags:             Optional[List[str]]    = None

class TaskResponse(BaseModel):
    """What the API returns when you request a task."""
    id:               str
    userId:           str
    title:            str
    description:      Optional[str]
    category:         Optional[str]
    priority:         Optional[str]
    status:           str
    deadline:         Optional[str]   # ISO string for JSON
    estimatedMinutes: Optional[int]
    riskScore:        Optional[float]
    aiSuggestion:     Optional[str]
    subtasks:         Optional[List[dict]]
    tags:             Optional[List[str]]
    createdAt:        Optional[str]
    completedAt:      Optional[str]