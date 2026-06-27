# =============================================
# LIFEPILOT AI - FIRESTORE SERVICE
# =============================================
# This file handles all database operations.
# Instead of writing Firestore code in every route,
# we centralise it here so it's reusable and testable.

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone
import logging
import os

from config import settings

logger = logging.getLogger(__name__)

# --- Initialize Firebase Admin SDK ---
# We only initialize once. If it's already initialized, skip.
def init_firebase():
    if not firebase_admin._apps:
        # Build the path to the service account file
        # It could be relative to the backend folder or an absolute path
        sa_path = settings.FIREBASE_SERVICE_ACCOUNT_PATH
        if not os.path.isabs(sa_path):
            sa_path = os.path.join(os.path.dirname(__file__), '..', sa_path)

        if not os.path.exists(sa_path):
            logger.error(f"Firebase service account not found at: {sa_path}")
            raise FileNotFoundError(
                f"firebase-service-account.json not found at {sa_path}. "
                "Download it from Firebase Console > Project Settings > Service Accounts."
            )

        cred = credentials.Certificate(sa_path)
        firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin SDK initialized successfully")

init_firebase()

# Get the Firestore client — used for all database operations
_db = firestore.client()

# =============================================
# HELPER FUNCTIONS
# =============================================

def _serialize(doc_data: dict) -> dict:
    """
    Convert Firestore-specific types to plain Python types
    so they can be serialized to JSON.
    
    Firestore stores dates as Timestamp objects.
    JSON needs strings. This function converts them.
    """
    result = {}
    for key, value in doc_data.items():
        if hasattr(value, 'isoformat'):
            # datetime → ISO string e.g. "2025-01-15T09:00:00"
            result[key] = value.isoformat()
        elif hasattr(value, 'ToDatetime'):
            # Firestore Timestamp → datetime → ISO string
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
    """Convert a Firestore document snapshot to a plain dict with id."""
    if not doc.exists:
        return None
    data = _serialize(doc.to_dict())
    data['id'] = doc.id
    return data

# =============================================
# TASK OPERATIONS
# =============================================

async def get_tasks(user_id: str) -> list:
    """Get all tasks for a user, ordered by creation date."""
    try:
        docs = (_db.collection('tasks')
                   .where('userId', '==', user_id)
                   .order_by('createdAt', direction=firestore.Query.DESCENDING)
                   .stream())
        return [_doc_to_dict(d) for d in docs]
    except Exception as e:
        logger.error(f"get_tasks error: {e}")
        raise

async def get_task(task_id: str, user_id: str) -> dict:
    """Get a single task. Raises exception if not found or wrong user."""
    doc = _db.collection('tasks').document(task_id).get()
    data = _doc_to_dict(doc)
    if not data or data.get('userId') != user_id:
        return None
    return data

async def create_task(user_id: str, task_data: dict) -> dict:
    """Create a new task and return it with its generated ID."""
    task_data['userId']    = user_id
    task_data['status']    = 'pending'
    task_data['riskScore'] = None
    task_data['subtasks']  = []
    task_data['aiSuggestion'] = None
    task_data['createdAt'] = firestore.SERVER_TIMESTAMP
    task_data['updatedAt'] = firestore.SERVER_TIMESTAMP
    task_data['completedAt'] = None

    # Convert deadline string to datetime if needed
    if 'deadline' in task_data and isinstance(task_data['deadline'], str):
        task_data['deadline'] = datetime.fromisoformat(
            task_data['deadline'].replace('Z', '+00:00')
        )

    ref = _db.collection('tasks').document()
    ref.set(task_data)
    doc = ref.get()
    return _doc_to_dict(doc)

async def update_task(task_id: str, user_id: str, updates: dict) -> dict:
    """Update specific fields of a task."""
    ref = _db.collection('tasks').document(task_id)
    doc = ref.get()
    if not doc.exists or doc.to_dict().get('userId') != user_id:
        return None

    # Remove None values — we don't want to overwrite fields with None
    updates = {k: v for k, v in updates.items() if v is not None}
    updates['updatedAt'] = firestore.SERVER_TIMESTAMP

    # Handle deadline conversion
    if 'deadline' in updates and isinstance(updates['deadline'], str):
        updates['deadline'] = datetime.fromisoformat(
            updates['deadline'].replace('Z', '+00:00')
        )

    # If marking completed, record the time
    if updates.get('status') == 'completed':
        updates['completedAt'] = firestore.SERVER_TIMESTAMP

    ref.update(updates)
    return _doc_to_dict(ref.get())

async def delete_task(task_id: str, user_id: str) -> bool:
    """Delete a task. Returns True if deleted, False if not found."""
    ref = _db.collection('tasks').document(task_id)
    doc = ref.get()
    if not doc.exists or doc.to_dict().get('userId') != user_id:
        return False
    ref.delete()
    return True

async def get_todays_tasks(user_id: str) -> list:
    """Get all tasks due today."""
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    today_end = today_start.replace(hour=23, minute=59, second=59)

    docs = (_db.collection('tasks')
               .where('userId', '==', user_id)
               .where('deadline', '>=', today_start)
               .where('deadline', '<=', today_end)
               .stream())
    return [_doc_to_dict(d) for d in docs]

# =============================================
# GOAL OPERATIONS
# =============================================

async def get_goals(user_id: str) -> list:
    try:
        docs = (_db.collection('goals')
                   .where('userId', '==', user_id)
                   .order_by('createdAt', direction=firestore.Query.DESCENDING)
                   .stream())
        return [_doc_to_dict(d) for d in docs]
    except Exception as e:
        logger.error(f"get_goals error: {e}")
        raise

async def create_goal(user_id: str, goal_data: dict) -> dict:
    goal_data['userId']    = user_id
    goal_data['progress']  = 0
    goal_data['status']    = 'active'
    goal_data['createdAt'] = firestore.SERVER_TIMESTAMP

    if 'targetDate' in goal_data and isinstance(goal_data['targetDate'], str):
        goal_data['targetDate'] = datetime.fromisoformat(
            goal_data['targetDate'].replace('Z', '+00:00')
        )

    ref = _db.collection('goals').document()
    ref.set(goal_data)
    return _doc_to_dict(ref.get())

async def update_goal(goal_id: str, user_id: str, updates: dict) -> dict:
    ref = _db.collection('goals').document(goal_id)
    doc = ref.get()
    if not doc.exists or doc.to_dict().get('userId') != user_id:
        return None
    updates = {k: v for k, v in updates.items() if v is not None}
    ref.update(updates)
    return _doc_to_dict(ref.get())

async def delete_goal(goal_id: str, user_id: str) -> bool:
    ref = _db.collection('goals').document(goal_id)
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
        docs = (_db.collection('habits')
                   .where('userId', '==', user_id)
                   .stream())
        return [_doc_to_dict(d) for d in docs]
    except Exception as e:
        logger.error(f"get_habits error: {e}")
        raise

async def create_habit(user_id: str, habit_data: dict) -> dict:
    habit_data['userId']         = user_id
    habit_data['streak']         = 0
    habit_data['longestStreak']  = 0
    habit_data['completedDates'] = []
    habit_data['createdAt']      = firestore.SERVER_TIMESTAMP
    ref = _db.collection('habits').document()
    ref.set(habit_data)
    return _doc_to_dict(ref.get())

async def complete_habit_today(habit_id: str, user_id: str) -> dict:
    """Mark a habit as done for today and update streak."""
    ref = _db.collection('habits').document(habit_id)
    doc = ref.get()
    if not doc.exists or doc.to_dict().get('userId') != user_id:
        return None

    data = doc.to_dict()
    today_str = datetime.now().strftime('%Y-%m-%d')
    completed_dates = data.get('completedDates', [])

    if today_str in completed_dates:
        return _doc_to_dict(doc)  # Already done today

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
    ref = _db.collection('habits').document(habit_id)
    doc = ref.get()
    if not doc.exists or doc.to_dict().get('userId') != user_id:
        return None
    updates = {k: v for k, v in updates.items() if v is not None}
    ref.update(updates)
    return _doc_to_dict(ref.get())

async def delete_habit(habit_id: str, user_id: str) -> bool:
    ref = _db.collection('habits').document(habit_id)
    doc = ref.get()
    if not doc.exists or doc.to_dict().get('userId') != user_id:
        return False
    ref.delete()
    return True

# =============================================
# CHAT HISTORY
# =============================================

async def save_chat_message(user_id: str, role: str, content: str):
    """Append a message to the user's chat history."""
    _db.collection('chat_history').add({
        'userId':    user_id,
        'role':      role,
        'content':   content,
        'timestamp': firestore.SERVER_TIMESTAMP
    })

async def get_chat_history(user_id: str, limit: int = 20) -> list:
    docs = (_db.collection('chat_history')
               .where('userId', '==', user_id)
               .order_by('timestamp', direction=firestore.Query.DESCENDING)
               .limit(limit)
               .stream())
    messages = [_doc_to_dict(d) for d in docs]
    return list(reversed(messages))  # Oldest first

# =============================================
# USER OPERATIONS
# =============================================

async def get_user(user_id: str) -> dict:
    doc = _db.collection('users').document(user_id).get()
    return _doc_to_dict(doc)

async def update_user(user_id: str, updates: dict) -> dict:
    ref = _db.collection('users').document(user_id)
    updates = {k: v for k, v in updates.items() if v is not None}
    ref.set(updates, merge=True)  # merge=True means don't overwrite the whole doc
    return _doc_to_dict(ref.get())