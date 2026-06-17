import os
import json
import tempfile
import shutil
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.agents.extraction_agent import ExtractionAgent
from src.agents.storage_agent import StorageAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.coordinator_agent import CoordinatorAgent
from src.database.models import Base, Memory

load_dotenv()

app = FastAPI(title="DailyBuddy")

gemini_key = os.getenv("GEMINI_API_KEY")
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

USER_ID = "default-user"


@app.get("/", response_class=HTMLResponse)
async def index():
    with open(os.path.join(os.path.dirname(__file__), "templates", "index.html")) as f:
        return f.read()


@app.post("/api/text")
async def extract_text(text: str = Form(...)):
    try:
        result = extraction.extract_from_text(text)
        if result.confidence_score >= 0.7:
            store_result = await storage.store_memory(USER_ID, result)
            return {
                "status": "success",
                "type": result.type,
                "data": result.extracted_data,
                "confidence": result.confidence_score,
                "memory_id": store_result.get("memory_id")
            }
        return {
            "status": "low_confidence",
            "type": result.type,
            "data": result.extracted_data,
            "confidence": result.confidence_score,
            "flags": result.flags
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "error": str(e)})


@app.post("/api/image")
async def extract_image(file: UploadFile = File(...)):
    tmp_path = None
    try:
        suffix = os.path.splitext(file.filename)[1] or ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        result = await coordinator.handle_request(USER_ID, "upload_image", tmp_path)
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "error": str(e)})
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.post("/api/query")
async def query_memories(query: str = Form(...)):
    try:
        result = await coordinator.handle_request(USER_ID, "query", query)
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "error": str(e)})


@app.get("/api/memories")
async def list_memories():
    try:
        memories = db_session.execute(
            select(Memory).where(Memory.user_id == USER_ID).order_by(Memory.created_at.desc()).limit(20)
        ).scalars().all()

        items = []
        for m in memories:
            items.append({
                "id": m.id,
                "type": m.content_type,
                "category": m.category,
                "data": json.loads(m.extracted_data) if m.extracted_data else {},
                "tags": json.loads(m.tags) if m.tags else [],
                "confidence": m.extraction_confidence,
                "created_at": m.created_at.isoformat() if m.created_at else None
            })
        return {"memories": items}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "error": str(e)})
