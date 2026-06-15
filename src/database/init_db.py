import os
import sys
from dotenv import load_dotenv

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy import create_engine
from src.database.models import Base

load_dotenv()

def init_db():
    postgres_url = os.getenv("POSTGRES_URL")
    if not postgres_url:
        print("Error: POSTGRES_URL not set in .env file.")
        return

    print(f"Connecting to database at {postgres_url.split('@')[-1]}...")
    try:
        engine = create_engine(postgres_url)
        Base.metadata.create_all(engine)
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")

if __name__ == "__main__":
    init_db()
