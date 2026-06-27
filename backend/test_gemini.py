# backend/test_gemini.py
# Run this from the backend folder: python test_gemini.py

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from config import settings

print("=" * 50)
print("LIFEPILOT AI — GEMINI DIAGNOSTIC")
print("=" * 50)

# Test 1: API Key
print(f"\n1. API Key loaded: {'✅ YES' if settings.GEMINI_API_KEY else '❌ MISSING'}")
if settings.GEMINI_API_KEY:
    print(f"   Starts with: {settings.GEMINI_API_KEY[:12]}...")

# Test 2: Import
print("\n2. Testing import...")
try:
    from google import genai
    from google.genai import types
    print("   ✅ google-genai imported successfully")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    print("   FIX: pip install google-genai")
    sys.exit(1)

# Test 3: Client creation
print("\n3. Testing client creation...")
try:
    client = genai.Client(
        api_key=settings.GEMINI_API_KEY,
        http_options={"api_version": "v1beta"}
    )
    print("   ✅ Client created successfully")
except Exception as e:
    print(f"   ❌ Client creation failed: {e}")
    sys.exit(1)

# Test 4: Simple generation
print("\n4. Testing Gemini API call with gemini-2.5-flash...")
try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Say hello in exactly 5 words.",
    )
    print(f"   ✅ Response: {response.text.strip()}")
except Exception as e:
    print(f"   ❌ gemini-2.5-flash failed: {e}")
    print("\n   Trying gemini-2.0-flash...")
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Say hello in exactly 5 words.",
        )
        print(f"   ✅ gemini-2.0-flash works: {response.text.strip()}")
        print("   ACTION: Change MODEL_NAME to 'gemini-2.0-flash' in gemini_service.py")
    except Exception as e2:
        print(f"   ❌ gemini-2.0-flash also failed: {e2}")
        print("\n   Trying gemini-1.5-flash...")
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents="Say hello in exactly 5 words.",
            )
            print(f"   ✅ gemini-1.5-flash works: {response.text.strip()}")
            print("   ACTION: Change MODEL_NAME to 'gemini-1.5-flash' in gemini_service.py")
        except Exception as e3:
            print(f"   ❌ All models failed: {e3}")

# Test 5: JSON response
print("\n5. Testing JSON response parsing...")
try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents='Return ONLY this JSON with no other text: {"status": "working", "score": 99}',
    )
    import json, re
    text = response.text
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text).strip()
    parsed = json.loads(text)
    print(f"   ✅ JSON parsed correctly: {parsed}")
except Exception as e:
    print(f"   ⚠️  JSON parsing issue: {e}")
    print(f"   Raw response was: {response.text[:200] if 'response' in dir() else 'N/A'}")

# Test 6: Async wrapper check
print("\n6. Testing async wrapper...")
import asyncio
async def test_async():
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    executor = ThreadPoolExecutor()
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor,
        lambda: client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Say OK"
        )
    )
    return result.text

try:
    result = asyncio.run(test_async())
    print(f"   ✅ Async wrapper works: {result.strip()}")
except Exception as e:
    print(f"   ❌ Async issue: {e}")

print("\n" + "=" * 50)
print("Diagnostic complete.")
print("=" * 50)