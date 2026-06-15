import json
from pinecone import Pinecone
from google import genai
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.database.models import Memory

class RetrievalAgent:
    def __init__(self, db: Session, pinecone_key: str, 
                 pinecone_index: str, gemini_key: str):
        self.db = db
        self.pc = Pinecone(api_key=pinecone_key)
        self.pinecone_index = pinecone_index
        self.client = genai.Client(api_key=gemini_key)
        self.model_id = "gemini-flash-latest"
    
    async def retrieve(self, user_id: str, query: str, limit: int = 5) -> dict:
        """Retrieve using hybrid search"""
        
        # 1. Vector search (Semantic)
        query_embed_response = self.client.models.embed_content(
            model="gemini-embedding-2",
            contents=query
        )
        query_embed = query_embed_response.embeddings[0].values
        
        index = self.pc.Index(self.pinecone_index)
        vector_results = index.query(
            vector=query_embed, 
            top_k=limit,
            filter={"user_id": user_id},
            include_metadata=True
        )
        
        # 2. SQL search (Keyword/Exact)
        sql_results = self.db.execute(
            select(Memory).where(
                Memory.user_id == user_id,
                (Memory.tags.any(query.lower())) | 
                (Memory.category.ilike(f"%{query}%"))
            ).limit(limit)
        ).scalars().all()
        
        # 3. Combine and Deduplicate
        combined = []
        seen_ids = set()
        
        for match in vector_results['matches']:
            combined.append({
                "id": match['id'],
                "score": match['score'],
                "metadata": match['metadata'],
                "source": "vector"
            })
            seen_ids.add(match['id'])
        
        for mem in sql_results:
            if str(mem.id) not in seen_ids:
                combined.append({
                    "id": str(mem.id),
                    "score": 1.0,
                    "metadata": {
                        "type": mem.content_type,
                        "category": mem.category,
                        "tags": mem.tags,
                        "extracted_data": mem.extracted_data
                    },
                    "source": "sql"
                })
        
        # 4. Synthesize answer
        answer = await self._synthesize(query, combined)
        
        return {
            "answer": answer,
            "sources": combined[:3],
            "confidence": combined[0]['score'] if combined else 0.0
        }
    
    async def _synthesize(self, query: str, results: list) -> str:
        """Generate natural language answer"""
        if not results:
            return "I couldn't find any information related to your query."
            
        context = "\n".join([
            json.dumps(r.get('metadata', {})) for r in results[:3]
        ])
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=f"""
            User asked: {query}
            
            Retrieved data:
            {context}
            
            Provide a clear, natural language answer based ONLY on the retrieved data.
            """
        )
        
        return response.text
