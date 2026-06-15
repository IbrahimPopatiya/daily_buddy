import json
import os
import shutil
from pinecone import Pinecone
from google import genai
from uuid import UUID
from sqlalchemy.orm import Session
from src.database.models import Memory, AuditLog

class StorageAgent:
    def __init__(self, db_session: Session, pinecone_key: str, 
                 pinecone_index: str, gemini_key: str, 
                 local_storage_path: str = "storage"):
        self.db = db_session
        self.pc = Pinecone(api_key=pinecone_key)
        self.pinecone_index = pinecone_index
        self.local_storage_path = local_storage_path
        self.client = genai.Client(api_key=gemini_key)
        
        # Ensure local storage path exists
        if not os.path.exists(self.local_storage_path):
            os.makedirs(self.local_storage_path)
    
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
            
            # 2. Local File Storage
            if document_path and os.path.exists(document_path):
                file_ext = os.path.splitext(document_path)[1]
                dest_path = os.path.join(self.local_storage_path, f"{memory.id}{file_ext}")
                shutil.copy2(document_path, dest_path)
            
            # 3. Create embeddings
            embedding_text = self._prepare_text(extraction_result)
            embedding_response = self.client.models.embed_content(
                model="gemini-embedding-2",
                contents=embedding_text
            )
            embedding = embedding_response.embeddings[0].values
            
            memory.embedding_vector = json.dumps(embedding)
            
            # 4. Pinecone index
            index = self.pc.Index(self.pinecone_index)
            index.upsert(vectors=[
                (str(memory.id), embedding, {
                    "user_id": str(user_id),
                    "type": extraction_result.type,
                    "category": memory.category
                })
            ])
            
            # 5. Audit log
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
        return list(set(tags[:5]))
    
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
