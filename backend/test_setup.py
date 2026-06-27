# backend/test_setup.py
# This file tests that all packages installed correctly
# You can delete it after confirming everything works

print("Testing imports...")

try:
    import fastapi
    print(f"✅ FastAPI {fastapi.__version__} - OK")
except ImportError:
    print("❌ FastAPI - FAILED")

try:
    import uvicorn
    print("✅ Uvicorn - OK")
except ImportError:
    print("❌ Uvicorn - FAILED")

try:
    import firebase_admin
    print("✅ Firebase Admin - OK")
except ImportError:
    print("❌ Firebase Admin - FAILED")

try:
    import google.generativeai
    print("✅ Google Generative AI - OK")
except ImportError:
    print("❌ Google Generative AI - FAILED")

try:
    import dotenv
    print("✅ Python Dotenv - OK")
except ImportError:
    print("❌ Python Dotenv - FAILED")

try:
    import pydantic
    print(f"✅ Pydantic {pydantic.__version__} - OK")
except ImportError:
    print("❌ Pydantic - FAILED")

print("\n✅ Setup test complete!")
print("If all items above show ✅, your environment is ready.")