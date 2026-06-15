from typing import Any, Dict, Optional
from uuid import UUID

class CoordinatorAgent:
    def __init__(self, extraction, storage, retrieval):
        self.extraction = extraction
        self.storage = storage
        self.retrieval = retrieval
    
    async def handle_request(self, user_id: UUID, 
                           request_type: str, content: Any) -> Dict[str, Any]:
        """Main coordinator logic"""
        
        if request_type in ["upload_image", "upload_video"]:
            # 1. Extract
            if request_type == "upload_image":
                result = self.extraction.extract_from_image(content)
            else:
                # Video extraction logic would go here
                # result = self.extraction.extract_from_video(content)
                return {"status": "error", "error": "Video extraction not yet implemented"}
            
            # 2. Check confidence
            if result.confidence_score < 0.7:
                return {
                    "status": "review_needed",
                    "data": result.extracted_data,
                    "confidence": result.confidence_score,
                    "message": "Extraction confidence is low. Please review and confirm."
                }
            
            # 3. Store
            storage_result = await self.storage.store_memory(
                user_id=user_id,
                extraction_result=result
            )
            
            if storage_result['status'] == 'success':
                return {
                    "status": "success",
                    "message": f"Successfully extracted and saved {result.type}!",
                    "memory_id": storage_result['memory_id']
                }
            else:
                return {"status": "error", "error": storage_result.get('error', 'Storage failed')}
        
        elif request_type == "query":
            return await self.retrieval.retrieve(str(user_id), content)
        
        else:
            return {"status": "error", "error": f"Unknown request type: {request_type}"}
