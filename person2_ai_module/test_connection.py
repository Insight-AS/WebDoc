import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(".env", override=True)

key = os.getenv("GEMINI_API_KEY", "").strip()
model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()

if not key:
    raise SystemExit("ERROR: API key missing in .env")

print("API key loaded successfully", flush=True)
print(f"Model: {model}", flush=True)
print("Connecting to Gemini...", flush=True)

try:
    client = genai.Client(
        api_key=key,
        http_options=types.HttpOptions(timeout=30000)
    )

    response = client.models.generate_content(
        model=model,
        contents="Reply with exactly: GEMINI CONNECTED"
    )

    print("\nSUCCESS!")
    print(response.text)

except Exception as e:
    print("\nCONNECTION FAILED")
    print(type(e).__name__)
    print(str(e))

