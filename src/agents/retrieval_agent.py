import json
from google import genai
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from src.database.models import Memory

class RetrievalAgent:
    def __init__(self, db: Session, gemini_key: str,
                 pinecone_key: str = None, pinecone_index: str = None):
        self.db = db
        self.client = genai.Client(api_key=gemini_key)
        self.model_id = "gemini-2.5-flash"
        self.use_pinecone = False
        if pinecone_key and pinecone_index:
            try:
                from pinecone import Pinecone
                self.pc = Pinecone(api_key=pinecone_key)
                self.pinecone_index = pinecone_index
                self.use_pinecone = True
            except ImportError:
                pass

    async def retrieve(self, user_id: str, query: str, limit: int = 5) -> dict:
        combined = []
        seen_ids = set()

        if self.use_pinecone:
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

            for match in vector_results['matches']:
                combined.append({
                    "id": match['id'],
                    "score": match['score'],
                    "metadata": match['metadata'],
                    "source": "vector"
                })
                seen_ids.add(match['id'])

        keywords = [w for w in query.lower().split() if len(w) > 2]
        filters = []
        for kw in keywords:
            filters.append(Memory.extracted_data.ilike(f"%{kw}%"))
            filters.append(Memory.tags.ilike(f"%{kw}%"))
            filters.append(Memory.category.ilike(f"%{kw}%"))
            filters.append(Memory.content_type.ilike(f"%{kw}%"))

        if not filters:
            sql_results = self.db.execute(
                select(Memory).where(Memory.user_id == user_id).limit(limit)
            ).scalars().all()
        else:
            sql_results = self.db.execute(
                select(Memory).where(
                    Memory.user_id == user_id,
                    or_(*filters)
                ).limit(limit)
            ).scalars().all()

        for mem in sql_results:
            if str(mem.id) not in seen_ids:
                extracted = json.loads(mem.extracted_data) if mem.extracted_data else {}
                tags = json.loads(mem.tags) if mem.tags else []
                combined.append({
                    "id": str(mem.id),
                    "score": 1.0,
                    "metadata": {
                        "type": mem.content_type,
                        "category": mem.category,
                        "tags": tags,
                        "extracted_data": extracted
                    },
                    "source": "sql"
                })

        answer = await self._synthesize(query, combined)

        return {
            "answer": answer,
            "sources": combined[:3],
            "confidence": combined[0]['score'] if combined else 0.0
        }

    async def _synthesize(self, query: str, results: list) -> str:
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
