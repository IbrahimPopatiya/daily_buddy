import os
import sys
import uuid
import asyncio
from dotenv import load_dotenv

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.agents.extraction_agent import ExtractionAgent
from src.agents.storage_agent import StorageAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.coordinator_agent import CoordinatorAgent

load_dotenv()

async def interactive_cli():
    # Initialize agents (same as in main.py)
    gemini_key = os.getenv("GEMINI_API_KEY")
    pinecone_key = os.getenv("PINECONE_API_KEY")
    pinecone_index = os.getenv("PINECONE_INDEX")
    postgres_url = os.getenv("POSTGRES_URL")

    engine = create_engine(postgres_url)
    db_session = Session(engine)

    extraction = ExtractionAgent(api_key=gemini_key)
    storage = StorageAgent(
        db_session=db_session,
        pinecone_key=pinecone_key,
        pinecone_index=pinecone_index,
        gemini_key=gemini_key,
        local_storage_path="d:/dailybuddy/storage"
    )
    retrieval = RetrievalAgent(
        db=db_session,
        pinecone_key=pinecone_key,
        pinecone_index=pinecone_index,
        gemini_key=gemini_key
    )
    
    coordinator = CoordinatorAgent(extraction, storage, retrieval)
    
    user_id = uuid.UUID("00000000-0000-0000-0000-000000000000") # Static user for local testing
    
    # Ensure user exists in DB
    from src.database.models import User
    existing_user = db_session.query(User).filter_by(id=user_id).first()
    if not existing_user:
        new_user = User(id=user_id, email="local_user@dailybuddy.com")
        db_session.add(new_user)
        db_session.commit()

    print("\n" + "="*30)
    print("      DAILYBUDDY CLI")
    print("="*30)
    print("Commands: upload [path], query [text], exit")
    
    while True:
        try:
            cmd_input = input("\nDailyBuddy > ").strip()
            if not cmd_input:
                continue
            
            if cmd_input.lower() == "exit":
                break
                
            if cmd_input.startswith("upload "):
                file_path = cmd_input[7:].strip()
                if not os.path.exists(file_path):
                    print(f"[-] File not found: {file_path}")
                    continue
                
                print(f"[*] Uploading and processing {file_path}...")
                result = await coordinator.handle_request(user_id, "upload_image", file_path)
                
                if result['status'] == 'success':
                    print(f"[+] {result['message']}")
                elif result['status'] == 'review_needed':
                    print(f"[!] {result['message']}")
                    print(f"    Extracted: {result['data']}")
                else:
                    print(f"[-] Error: {result.get('error')}")
                    
            elif cmd_input.startswith("query "):
                query_text = cmd_input[6:].strip()
                print(f"[*] Searching for: '{query_text}'...")
                result = await coordinator.handle_request(user_id, "query", query_text)
                
                print("\n" + "-"*30)
                print(f"Answer: {result['answer']}")
                print("-"*30)
                if result['sources']:
                    print("Sources:")
                    for s in result['sources']:
                        print(f"- {s['metadata'].get('type')} ({s['source']})")
                
            else:
                print("[-] Unknown command. Use 'upload [path]', 'query [text]', or 'exit'.")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[-] System error: {e}")

    print("\nGoodbye!")

if __name__ == "__main__":
    asyncio.run(interactive_cli())
