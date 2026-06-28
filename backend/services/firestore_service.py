# =============================================
# LIFEPILOT AI - FIRESTORE SERVICE
# =============================================

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from datetime import datetime, timezone
import logging
import os

logger = logging.getLogger(__name__)

# Global db client
_db = None

def get_db():
    global _db
    if _db is None:
        _init_firebase()
    return _db

def _init_firebase():
    global _db
    if firebase_admin._apps:
        _db = firestore.client()
        return

    # Try multiple paths for the service account file
    possible_paths = [
        "/app/backend/firebase-service-account.json",
        os.path.join(os.path.dirname(__file__), "firebase-service-account.json"),
        "firebase-service-account.json",
    ]

    sa_path = None
    for path in possible_paths:
        if os.path.exists(path):
            sa_path = path
            break

    if sa_path:
        cred = credentials.Certificate(sa_path)
        firebase_admin.initialize_app(cred)
        logger.info(f"Firebase initialized from file: {sa_path}")
    else:
        # Fall back to Application Default Credentials
        logger.warning("No service account file found, trying default credentials")
        firebase_admin.initialize_app()

    _db = firestore.client()
    logger.info("Firestore client ready")

# Initialize on import but don't crash if it fails
try:
    _init_firebase()
except Exception as e:
    logger.error(f"Firebase init failed: {e}")

# =============================================
# HELPER FUNCTIONS
# =============================================

def _serialize(doc_data: dict) -> dict:
    result = {}
    for key, value in doc_data.items():
        if hasattr(value, 'isoformat'):
            result[key] = value.isoformat()
        elif hasattr(value, 'ToDatetime'):
            result[key] = value.ToDatetime(tzinfo=timezone.utc).isoformat()
        elif isinstance(value, dict):
            result[key] = _serialize(value)
        elif isinstance(value, list):
            result[key] = [
                _serialize(i) if isinstance(i, dict) else i
                for i in value
            ]
        else:
            result[key] = value
    return result

def _doc_to_dict(doc) -> dict:
    if not doc.exists:
        return None
    data = _serialize(doc.to_dict())
    data['id'] = doc.id
    return data

# =============================================
# TASK OPERATIONS
# =============================================

async def get_tasks(user_id: str) -> list:
    try:
        db = get_db()
        docs = (
            db.collection('tasks')
              .where(filter=FieldFilter('userId', '==', user_id))
              .stream()
        )
        tasks = [_doc_to_dict(d) for d in docs]
        tasks.sort(key=lambda t: t.get('createdAt') or '', reverse=True)
        return tasks
    except Exception as e:
        logger.error(f"get_tasks error: {e}")
        raise

async def get_task(task_id: str, user_id: str) -> dict:
    db   = get_db()
    doc  = db.collection('tasks').document(task_id).get()
    data = _doc_to_dict(doc)
    if not data or data.get('userId') != user_id:
        return None
    return data

async def create_task(user_id: str, task_data: dict) -> dict:
    db = get_db()
    task_data['userId']       = user_id
    task_data['status']       = 'pending'
    task_data['riskScore']    = None
    task_data['subtasks']     = []
    task_data['aiSuggestion'] = None
    task_data['createdAt']    = firestore.SERVER_TIMESTAMP
    task_data['updatedAt']    = firestore.SERVER_TIMESTAMP
    task_data['completedAt']  = None

    if 'deadline' in task_data and isinstance(task_data['deadline'], str):
        task_data['deadline'] = datetime.fromisoformat(
            task_data['deadline'].replace('Z', '+00:00')
        )

    ref = db.collection('tasks').document()
    ref.set(task_data)
    return _doc_to_dict(ref.get())

async def update_task(task_id: str, user_id: str, updates: dict) -> dict:
    db  = get_db()
    ref = db.collection('tasks').document(task_id)
    doc = ref.get()
    if not doc.exists or doc.to_dict().get('userId') != user_id:
        return None

    updates = {k: v for k, v in updates.items() if v is not None}
    updates['updatedAt'] = firestore.SERVER_TIMESTAMP

    if 'deadline' in updates and isinstance(updates['deadline'], str):
        updates['deadline'] = datetime.fromisoformat(
            updates['deadline'].replace('Z', '+00:00')
        )

    if updates.get('status') == 'completed':
        updates['completedAt'] = firestore.SERVER_TIMESTAMP

    ref.update(updates)
    return _doc_to_dict(ref.get())

async def delete_task(task_id: str, user_id: str) -> bool:
    db  = get_db()
    ref = db.collection('tasks').document(task_id)
    doc = ref.get()
    if not doc.exists or doc.to_dict().get('userId') != user_id:
        return False
    ref.delete()
    return True

async def get_todays_tasks(user_id: str) -> list:
    db    = get_db()
    today = datetime.now(timezone.utc).date()
    docs  = (
        db.collection('tasks')
          .where(filter=FieldFilter('userId', '==', user_id))
          .stream()
    )
    result = []
    for d in docs:
        task = _doc_to_dict(d)
        if not task:
            continue
        deadline = task.get('deadline')
        if not deadline:
            continue
        try:
            deadline_date = datetime.fromisoformat(deadline).date()
            if deadline_date == today:
                result.append(task)
        except (ValueError, TypeError):
            continue
    return result

# =============================================
# GOAL OPERATIONS
# =============================================

async def get_goals(user_id: str) -> list:
    try:
        db   = get_db()
        docs = (
            db.collection('goals')
              .where(filter=FieldFilter('userId', '==', user_id))
              .stream()
        )
        goals = [_doc_to_dict(d) for d in docs]
        goals.sort(key=lambda g: g.get('createdAt') or '', reverse=True)
        return goals
    except Exception as e:
        logger.error(f"get_goals error: {e}")
        raise

async def create_goal(user_id: str, goal_data: dict) -> dict:
    db = get_db()
    goal_data['userId']    = user_id
    goal_data['progress']  = 0
    goal_data['status']    = 'active'
    goal_data['createdAt'] = firestore.SERVER_TIMESTAMP

    if 'targetDate' in goal_data and isinstance(goal_data['targetDate'], str):
        goal_data['targetDate'] = datetime.fromisoformat(
            goal_data['targetDate'].replace('Z', '+00:00')
        )

    ref = db.collection('goals').document()
    ref.set(goal_data)
    return _doc_to_dict(ref.get())

async def update_goal(goal_id: str, user_id: str, updates: dict) -> dict:
    db  = get_db()
    ref = db.collection('goals').document(goal_id)
    doc = ref.get()
    if not doc.exists or doc.to_dict().get('userId') != user_id:
        return None
    updates = {k: v for k, v in updates.items() if v is not None}
    ref.update(updates)
    return _doc_to_dict(ref.get())

async def delete_goal(goal_id: str, user_id: str) -> bool:
    db  = get_db()
    ref = db.collection('goals').document(goal_id)
    doc = ref.get()
    if not doc.exists or doc.to_dict().get('userId') != user_id:
        return False
    ref.delete()
    return True

# =============================================
# HABIT OPERATIONS
# =============================================

async def get_habits(user_id: str) -> list:
    try:
        db   = get_db()
        docs = (
            db.collection('habits')
              .where(filter=FieldFilter('userId', '==', user_id))
              .stream()
        )
        return [_doc_to_dict(d) for d in docs]
    except Exception as e:
        logger.error(f"get_habits error: {e}")
        raise

async def create_habit(user_id: str, habit_data: dict) -> dict:
    db = get_db()
    habit_data['userId']         = user_id
    habit_data['streak']         = 0
    habit_data['longestStreak']  = 0
    habit_data['completedDates'] = []
    habit_data['createdAt']      = firestore.SERVER_TIMESTAMP
    ref = db.collection('habits').document()
    ref.set(habit_data)
    return _doc_to_dict(ref.get())

async def complete_habit_today(habit_id: str, user_id: str) -> dict:
    db  = get_db()
    ref = db.collection('habits').document(habit_id)
    doc = ref.get()
    if not doc.exists or doc.to_dict().get('userId') != user_id:
        return None

    data            = doc.to_dict()
    today_str       = datetime.now().strftime('%Y-%m-%d')
    completed_dates = data.get('completedDates', [])

    if today_str in completed_dates:
        return _doc_to_dict(doc)

    completed_dates.append(today_str)
    new_streak = data.get('streak', 0) + 1
    longest    = max(data.get('longestStreak', 0), new_streak)

    ref.update({
        'completedDates': completed_dates,
        'streak':         new_streak,
        'longestStreak':  longest
    })
    return _doc_to_dict(ref.get())

async def update_habit(habit_id: str, user_id: str, updates: dict) -> dict:
    db  = get_db()
    ref = db.collection('habits').document(habit_id)
    doc = ref.get()
    if not doc.exists or doc.to_dict().get('userId') != user_id:
        return None
    updates = {k: v for k, v in updates.items() if v is not None}
    ref.update(updates)
    return _doc_to_dict(ref.get())

async def delete_habit(habit_id: str, user_id: str) -> bool:
    db  = get_db()
    ref = db.collection('habits').document(habit_id)
    doc = ref.get()
    if not doc.exists or doc.to_dict().get('userId') != user_id:
        return False
    ref.delete()
    return True

# =============================================
# CHAT HISTORY
# =============================================

async def save_chat_message(user_id: str, role: str, content: str):
    db = get_db()
    db.collection('chat_history').add({
        'userId':    user_id,
        'role':      role,
        'content':   content,
        'timestamp': firestore.SERVER_TIMESTAMP
    })

async def get_chat_history(user_id: str, limit: int = 20) -> list:
    db   = get_db()
    docs = (
        db.collection('chat_history')
          .where(filter=FieldFilter('userId', '==', user_id))
          .stream()
    )
    messages = [_doc_to_dict(d) for d in docs]
    messages.sort(key=lambda m: m.get('timestamp') or '')
    return messages[-limit:]

# =============================================
# USER OPERATIONS
# =============================================

async def get_user(user_id: str) -> dict:
    db  = get_db()
    doc = db.collection('users').document(user_id).get()
    return _doc_to_dict(doc)

async def update_user(user_id: str, updates: dict) -> dict:
    db  = get_db()
    ref = db.collection('users').document(user_id)
    updates = {k: v for k, v in updates.items() if v is not None}
    ref.set(updates, merge=True)
    return _doc_to_dict(ref.get())