# DailyBuddy: Code Templates & Configuration Files

## Project Setup Files

### 1. requirements.txt

```
google-generativeai>=0.10.0
google-cloud-run>=1.10.0
google-cloud-sql>=1.4.0
google-cloud-storage>=2.13.0
google-cloud-logging>=3.5.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
pinecone-client>=3.0.0
fastapi>=0.109.0
uvicorn>=0.27.0
pydantic>=2.5.0
python-dotenv>=1.0.0
requests>=2.31.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
```

### 2. .env.example

```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GEMINI_API_KEY=your-api-key
POSTGRES_URL=postgresql://user:password@host:5432/dailybuddy
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX=dailybuddy-memories
GCS_BUCKET=dailybuddy-storage
ENVIRONMENT=development
```

---

## Core Agent Implementation

### Extraction Agent (src/agents/extraction_agent.py)

```python
import json
import google.generativeai as genai
from dataclasses import dataclass

@dataclass
class ExtractionResult:
    type: str
    extracted_data: dict
    confidence_score: float
    raw_data: str
    flags: list = None

class ExtractionAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def extract_from_image(self, image_path: str) -> ExtractionResult:
        """Extract structured data from image"""
        import base64
        
        with open(image_path, 'rb') as f:
            image_data = base64.standard_b64encode(f.read()).decode('utf-8')
        
        prompt = """
        Analyze this image and extract ALL visible information.
        Return as JSON with:
        - content_type: warranty|receipt|bill|other
        - extracted_fields: dict with all key-value pairs
        - confidence: float 0-1
        """
        
        response = self.model.generate_content([
            {"mime_type": "image/jpeg", "data": image_data},
            prompt
        ])
        
        return self._parse_response(response.text, "image")
    
    def extract_from_text(self, text: str) -> ExtractionResult:
        """Extract from plain text"""
        prompt = f"""
        Extract structured information from this text:
        {text}
        
        Return JSON with extracted fields and confidence.
        """
        
        response = self.model.generate_content(prompt)
        return self._parse_response(response.text, "text")
    
    def _parse_response(self, text: str, source: str) -> ExtractionResult:
        """Parse Gemini response into structured format"""
        import re
        try:
            json_str = re.search(r'\{[\s\S]*\}', text).group(0)
            data = json.loads(json_str)
            
            return ExtractionResult(
                type=data.get('content_type', 'unknown'),
                extracted_data=data.get('extracted_fields', {}),
                confidence_score=data.get('confidence', 0.0),
                raw_data=text
            )
        except:
            return ExtractionResult(
                type='unknown',
                extracted_data={},
                confidence_score=0.0,
                raw_data=text,
                flags=['Parsing error']
            )
```

### Storage Agent (src/agents/storage_agent.py)

```python
import json
import pinecone
import google.generativeai as genai
from uuid import UUID
from sqlalchemy.orm import Session
from src.database.models import Memory, AuditLog

class StorageAgent:
    def __init__(self, db_session: Session, pinecone_key: str, 
                 pinecone_index: str, gemini_key: str):
        self.db = db_session
        pinecone.Pinecone(api_key=pinecone_key)
        self.pinecone_index = pinecone_index
        genai.configure(api_key=gemini_key)
    
    async def store_memory(self, user_id: UUID, extraction_result,
                          document_path: str = None) -> dict:
        """Store extracted data across all layers"""
        
        try:
            # 1. PostgreSQL insert
            memory = Memory(
                user_id=user_id,
                content_type=extraction_result.type,
                extracted_data=extraction_result.extracted_data,
                extraction_confidence=extraction_result.confidence_score,
                tags=self._generate_tags(extraction_result),
                category=self._categorize(extraction_result)
            )
            
            self.db.add(memory)
            self.db.flush()
            
            # 2. Create embeddings
            embedding_text = self._prepare_text(extraction_result)
            embedding = genai.embed_content(
                model="models/embedding-001",
                content=embedding_text
            )['embedding']
            
            memory.embedding_vector = json.dumps(embedding)
            
            # 3. Pinecone index
            index = pinecone.Index(self.pinecone_index)
            index.upsert(vectors=[
                (str(memory.id), embedding, {
                    "user_id": str(user_id),
                    "type": extraction_result.type,
                    "category": memory.category
                })
            ])
            
            # 4. Audit log
            audit = AuditLog(
                user_id=user_id,
                operation="CREATE",
                resource_type="memory",
                resource_id=memory.id,
                new_value=extraction_result.extracted_data
            )
            self.db.add(audit)
            self.db.commit()
            
            return {
                "status": "success",
                "memory_id": str(memory.id)
            }
        
        except Exception as e:
            self.db.rollback()
            return {"status": "error", "error": str(e)}
    
    def _generate_tags(self, result) -> list:
        tags = [result.type]
        for key, value in result.extracted_data.items():
            if isinstance(value, str) and len(value) < 50:
                tags.append(value.lower()[:20])
        return tags[:5]
    
    def _categorize(self, result) -> str:
        type_map = {
            "warranty": "appliances",
            "receipt": "purchases",
            "bill": "utilities"
        }
        return type_map.get(result.type, "general")
    
    def _prepare_text(self, result) -> str:
        parts = [result.type]
        parts.extend([f"{k}: {v}" for k, v in result.extracted_data.items()])
        return " ".join(str(p) for p in parts[:50])
```

### Retrieval Agent (src/agents/retrieval_agent.py)

```python
import json
import pinecone
import google.generativeai as genai
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.database.models import Memory

class RetrievalAgent:
    def __init__(self, db: Session, pinecone_key: str, 
                 pinecone_index: str, gemini_key: str):
        self.db = db
        pinecone.Pinecone(api_key=pinecone_key)
        self.pinecone_index = pinecone_index
        genai.configure(api_key=gemini_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    async def retrieve(self, user_id: str, query: str, limit: int = 5) -> dict:
        """Retrieve using hybrid search"""
        
        # Vector search
        query_embed = genai.embed_content(
            model="models/embedding-001",
            content=query
        )['embedding']
        
        index = pinecone.Index(self.pinecone_index)
        vector_results = index.query(
            vector=query_embed, top_k=limit,
            namespace="user_memories",
            filter={"user_id": user_id},
            include_metadata=True
        )
        
        # SQL search
        memories = self.db.execute(
            select(Memory).where(Memory.user_id == user_id)
        ).scalars().all()
        
        # Combine results
        combined = []
        for match in vector_results['matches']:
            combined.append({
                "id": match['id'],
                "score": match['score'],
                "metadata": match['metadata']
            })
        
        # Synthesize answer
        answer = await self._synthesize(query, combined)
        
        return {
            "answer": answer,
            "sources": combined[:3],
            "confidence": combined[0]['score'] if combined else 0.0
        }
    
    async def _synthesize(self, query: str, results: list) -> str:
        """Generate natural language answer"""
        context = "\n".join([
            json.dumps(r.get('metadata', {})) for r in results[:3]
        ])
        
        response = self.model.generate_content(f"""
        User asked: {query}
        
        Retrieved data:
        {context}
        
        Provide a clear, natural language answer.
        """)
        
        return response.text
```

### Coordinator Agent (src/agents/coordinator_agent.py)

```python
from typing import Optional

class CoordinatorAgent:
    def __init__(self, extraction, storage, retrieval):
        self.extraction = extraction
        self.storage = storage
        self.retrieval = retrieval
    
    async def handle_request(self, user_id: str, 
                           request_type: str, content: any) -> dict:
        """Main coordinator logic"""
        
        if request_type in ["upload_image", "upload_video"]:
            # 1. Extract
            if request_type == "upload_image":
                result = self.extraction.extract_from_image(content)
            else:
                result = self.extraction.extract_from_video(content)
            
            # 2. Check confidence
            if result.confidence_score < 0.7:
                return {
                    "status": "review_needed",
                    "data": result.extracted_data,
                    "confidence": result.confidence_score
                }
            
            # 3. Store
            storage_result = await self.storage.store_memory(
                user_id=user_id,
                extraction_result=result
            )
            
            return {
                "status": "success",
                "message": f"Saved {result.type}!"
            }
        
        elif request_type == "query":
            return await self.retrieval.retrieve(user_id, content)
        
        else:
            return {"status": "error", "error": "Unknown request type"}
```

---

## Database Models

### models.py (SQLAlchemy)

```python
from sqlalchemy import Column, String, DateTime, Float, JSON, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base
from datetime import datetime
from uuid import uuid4

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Memory(Base):
    __tablename__ = "memories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    content_type = Column(String(50), index=True)
    extracted_data = Column(JSONB)
    embedding_vector = Column(String)
    tags = Column(ARRAY(String))
    category = Column(String(100))
    extraction_confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    operation = Column(String(50))
    resource_type = Column(String(100))
    resource_id = Column(UUID)
    new_value = Column(JSONB)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
```

---

## Running Your First Agent

### Quick Start Script (main.py)

```python
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.agents.extraction_agent import ExtractionAgent
from src.agents.storage_agent import StorageAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.coordinator_agent import CoordinatorAgent

load_dotenv()

async def main():
    # Initialize database
    engine = create_engine(os.getenv("POSTGRES_URL"))
    db_session = Session(engine)
    
    # Initialize agents
    extraction = ExtractionAgent(api_key=os.getenv("GEMINI_API_KEY"))
    storage = StorageAgent(
        db_session=db_session,
        pinecone_key=os.getenv("PINECONE_API_KEY"),
        pinecone_index=os.getenv("PINECONE_INDEX"),
        gemini_key=os.getenv("GEMINI_API_KEY")
    )
    retrieval = RetrievalAgent(
        db=db_session,
        pinecone_key=os.getenv("PINECONE_API_KEY"),
        pinecone_index=os.getenv("PINECONE_INDEX"),
        gemini_key=os.getenv("GEMINI_API_KEY")
    )
    
    coordinator = CoordinatorAgent(extraction, storage, retrieval)
    
    # Example 1: Upload warranty
    result = await coordinator.handle_request(
        user_id="user@example.com",
        request_type="upload_image",
        content="./warranty.jpg"
    )
    print("Upload result:", result)
    
    # Example 2: Query
    result = await coordinator.handle_request(
        user_id="user@example.com",
        request_type="query",
        content="When does my warranty expire?"
    )
    print("Query result:", result)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Testing Template

```python
# tests/test_agents.py
import pytest
from unittest.mock import Mock, AsyncMock
from src.agents.extraction_agent import ExtractionAgent

@pytest.fixture
def extraction_agent():
    return ExtractionAgent(api_key="test-key")

def test_extract_from_image(extraction_agent):
    result = extraction_agent.extract_from_image("test_image.jpg")
    assert result.confidence_score >= 0
    assert isinstance(result.extracted_data, dict)

@pytest.mark.asyncio
async def test_storage_agent(storage_agent):
    mock_extraction = Mock()
    mock_extraction.type = "warranty"
    mock_extraction.extracted_data = {"product": "Cooler"}
    mock_extraction.confidence_score = 0.95
    
    result = await storage_agent.store_memory(
        user_id="test-user",
        extraction_result=mock_extraction
    )
    
    assert result['status'] == 'success'
    assert 'memory_id' in result
```

---

## Configuration Files

### agents.yaml

```yaml
coordinator:
  description: Routes requests to appropriate agents
  tools: [extraction, storage, retrieval]

extraction:
  description: Extracts structured data from images, video, text
  tools: [gemini_vision, ocr, entity_extraction]

storage:
  description: Persists and indexes information
  tools: [postgresql, pinecone, embeddings]

retrieval:
  description: Retrieves relevant information
  tools: [vector_search, sql_query, synthesis]
```

---

**Quick Reference:**
- Extract: `ExtractionAgent().extract_from_image(path)`
- Store: `await StorageAgent().store_memory(user_id, extraction)`
- Retrieve: `await RetrievalAgent().retrieve(user_id, query)`
- Coordinate: `await CoordinatorAgent().handle_request(user_id, type, content)`

