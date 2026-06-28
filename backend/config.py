# =============================================
# LIFEPILOT AI - CONFIGURATION
# =============================================

import os
from dotenv import load_dotenv

# Load the .env file from the project root
# dirname(__file__) = the backend folder
# join(.., '..', '.env') goes one level up to the root
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
class Settings:
    """
    All configuration values for the application.
    Values are read from environment variables (the .env file).
    If a variable is missing, the default value is used.
    """

    # App
    APP_NAME:    str = os.getenv("APP_NAME", "LifePilot AI")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    PORT:        int = int(os.getenv("PORT", 8000))

    # Gemini AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Firebase
    FIREBASE_SERVICE_ACCOUNT_PATH: str = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT_PATH",
        "firebase-service-account.json"
    )

    # CORS — which frontend URLs are allowed to call this backend
    # We split the comma-separated string into a list
    ALLOWED_ORIGINS: list = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5500,http://127.0.0.1:5500,https://lifepilot-ai-e8699.web.app"
    ).split(",")

    def validate(self):
        if not self.GEMINI_API_KEY:
            print("⚠️  CONFIG WARNING: GEMINI_API_KEY is missing from .env")
        else:
            print("✅ GEMINI_API_KEY loaded successfully")

# Create a single shared instance used everywhere
settings = Settings()
settings.validate()