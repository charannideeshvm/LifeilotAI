# =============================================
# LIFEPILOT AI - FASTAPI ENTRY POINT
# =============================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

from config import settings
from routes import auth, tasks, goals, habits, ai, chat, analytics

# --- Logging Setup ---
# This makes log messages appear in your terminal with timestamps
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# --- Create FastAPI App ---
app = FastAPI(
    title="LifePilot AI API",
    description="AI-powered productivity companion backend",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI at http://localhost:8000/docs
    redoc_url="/redoc"      # ReDoc UI at http://localhost:8000/redoc
)

# --- CORS Middleware ---
# CORS = Cross-Origin Resource Sharing
# This allows your frontend (running on port 5500) to call
# your backend (running on port 8000). Without this, browsers
# block the requests for security reasons.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],    # Allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],    # Allow all headers including Authorization
)

# --- Register Routes ---
# Each router handles a group of related endpoints.
# The prefix means all routes in that file start with that path.
app.include_router(auth.router,      prefix="/api/auth",      tags=["Authentication"])
app.include_router(tasks.router,     prefix="/api/tasks",     tags=["Tasks"])
app.include_router(goals.router,     prefix="/api/goals",     tags=["Goals"])
app.include_router(habits.router,    prefix="/api/habits",    tags=["Habits"])
app.include_router(ai.router,        prefix="/api/ai",        tags=["AI Features"])
app.include_router(chat.router,      prefix="/api/chat",      tags=["Chat"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

# --- Root Endpoint ---
@app.get("/")
async def root():
    """Health check endpoint. Visit http://localhost:8000 to confirm server is running."""
    return {
        "status":  "running",
        "app":     "LifePilot AI",
        "version": "1.0.0",
        "docs":    "/docs"
    }

@app.get("/health")
async def health():
    """Used by Google Cloud Run to check if the service is alive."""
    return {"status": "healthy"}

# --- Start Server ---
# This block only runs when you execute: python main.py
# uvicorn is the ASGI server that runs FastAPI
if __name__ == "__main__":
    logger.info(f"Starting LifePilot AI on port {settings.PORT}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",     # Listen on all network interfaces
        port=settings.PORT,
        reload=True         # Auto-restart when you save a file (development only)
    )