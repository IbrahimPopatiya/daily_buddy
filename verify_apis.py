import os
from dotenv import load_dotenv
from google import genai
from pinecone import Pinecone

load_dotenv()

def verify_apis():
    print("--- Verifying Connectivity ---")
    
    # 1. Gemini API
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("[-] GEMINI_API_KEY is missing.")
    else:
        try:
            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents="Hello"
            )
            print(f"[+] Gemini API connected. Response: {response.text[:10]}...")
        except Exception as e:
            print(f"[-] Gemini API failed: {e}")

    # 2. Pinecone API
    pinecone_key = os.getenv("PINECONE_API_KEY")
    pinecone_index = os.getenv("PINECONE_INDEX")
    if not pinecone_key or not pinecone_index:
        print("[-] PINECONE_API_KEY or PINECONE_INDEX is missing.")
    else:
        try:
            pc = Pinecone(api_key=pinecone_key)
            indexes = [idx.name for idx in pc.list_indexes()]
            if pinecone_index in indexes:
                print(f"[+] Pinecone connected. Index '{pinecone_index}' found.")
            else:
                print(f"[-] Pinecone connected, but index '{pinecone_index}' not found.")
        except Exception as e:
            print(f"[-] Pinecone API failed: {e}")

if __name__ == "__main__":
    verify_apis()
