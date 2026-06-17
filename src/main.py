import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.agents.extraction_agent import ExtractionAgent
from src.agents.storage_agent import StorageAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.coordinator_agent import CoordinatorAgent
from src.database.models import Base

load_dotenv()

async def main():
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key or gemini_key == "your-api-key":
        print("Error: GEMINI_API_KEY not set in .env file.")
        return

    db_url = os.getenv("DATABASE_URL", "sqlite:///dailybuddy.db")
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    db_session = Session(engine)

    pinecone_key = os.getenv("PINECONE_API_KEY")
    pinecone_index = os.getenv("PINECONE_INDEX")

    extraction = ExtractionAgent(api_key=gemini_key)
    storage = StorageAgent(
        db_session=db_session,
        gemini_key=gemini_key,
        pinecone_key=pinecone_key,
        pinecone_index=pinecone_index,
        local_storage_path=os.getenv("LOCAL_STORAGE_PATH", "storage")
    )
    retrieval = RetrievalAgent(
        db=db_session,
        gemini_key=gemini_key,
        pinecone_key=pinecone_key,
        pinecone_index=pinecone_index
    )

    coordinator = CoordinatorAgent(extraction, storage, retrieval)

    user_id = "default-user"

    if not pinecone_key:
        print("Note: Pinecone not configured. Running with local DB only.\n")

    print("=== DailyBuddy ===")
    print("Commands:")
    print("  image <path>  - Extract data from an image")
    print("  text <text>   - Extract data from text")
    print("  query <text>  - Search your memories")
    print("  quit          - Exit")
    print()

    while True:
        try:
            user_input = input("dailybuddy> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("Goodbye!")
            break

        parts = user_input.split(maxsplit=1)
        command = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        try:
            if command == "image" and arg:
                if not os.path.exists(arg):
                    print(f"File not found: {arg}")
                    continue
                result = await coordinator.handle_request(user_id, "upload_image", arg)
                print(f"Result: {result}")

            elif command == "text" and arg:
                extraction_result = extraction.extract_from_text(arg)
                if extraction_result.confidence_score >= 0.7:
                    store_result = await storage.store_memory(user_id, extraction_result)
                    print(f"Extracted and stored: {store_result}")
                else:
                    print(f"Low confidence extraction: {extraction_result.extracted_data}")
                    print(f"Confidence: {extraction_result.confidence_score}")

            elif command == "query" and arg:
                result = await coordinator.handle_request(user_id, "query", arg)
                print(f"Answer: {result.get('answer', 'No answer')}")
                if result.get('sources'):
                    print(f"Sources: {len(result['sources'])} found")

            else:
                print("Unknown command. Use: image <path>, text <text>, query <text>, quit")
        except Exception as e:
            print(f"Error: {e}")

    db_session.close()

if __name__ == "__main__":
    asyncio.run(main())
