import asyncio
import os
import uuid
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.agents.extraction_agent import ExtractionAgent
from src.agents.storage_agent import StorageAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.coordinator_agent import CoordinatorAgent

load_dotenv()

async def main():
    # Check for API keys
    if not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "your-api-key":
        print("Error: GEMINI_API_KEY not set in .env file.")
        return

    # Initialize database
    postgres_url = os.getenv("POSTGRES_URL")
    if not postgres_url:
        print("Error: POSTGRES_URL not set in .env file.")
        return
        
    try:
        engine = create_engine(postgres_url)
        db_session = Session(engine)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return
    
    # Initialize agents
    extraction = ExtractionAgent(api_key=os.getenv("GEMINI_API_KEY"))
    storage = StorageAgent(
        db_session=db_session,
        pinecone_key=os.getenv("PINECONE_API_KEY"),
        pinecone_index=os.getenv("PINECONE_INDEX"),
        gemini_key=os.getenv("GEMINI_API_KEY"),
        local_storage_path="d:/dailybuddy/storage"
    )
    retrieval = RetrievalAgent(
        db=db_session,
        pinecone_key=os.getenv("PINECONE_API_KEY"),
        pinecone_index=os.getenv("PINECONE_INDEX"),
        gemini_key=os.getenv("GEMINI_API_KEY")
    )
    
    coordinator = CoordinatorAgent(extraction, storage, retrieval)
    
    user_id = uuid.uuid4() # In a real app, this would be the logged-in user's ID
    
    print("DailyBuddy initialized. Waiting for user keys and input...")
    # This is a placeholder for a loop or interactive CLI
    # Example usage:
    # result = await coordinator.handle_request(user_id, "upload_image", "path/to/receipt.jpg")
    # print(result)

if __name__ == "__main__":
    asyncio.run(main())
