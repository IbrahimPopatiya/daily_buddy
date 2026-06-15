import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

def list_available_models():
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("[-] GEMINI_API_KEY is missing.")
        return

    try:
        client = genai.Client(api_key=gemini_key)
        print("--- Available Gemini Models ---")
        for model in client.models.list():
            print(f"- {model.name}")
    except Exception as e:
        print(f"[-] Failed to list models: {e}")

if __name__ == "__main__":
    list_available_models()
