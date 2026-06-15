import json
from google import genai
from google.genai import types
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class ExtractionResult:
    type: str
    extracted_data: dict
    confidence_score: float
    raw_data: str
    flags: Optional[List[str]] = None

class ExtractionAgent:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-flash-latest"
    
    def extract_from_image(self, image_path: str) -> ExtractionResult:
        """Extract structured data from image"""
        import PIL.Image
        
        img = PIL.Image.open(image_path)
        
        prompt = """
        Analyze this image and extract ALL visible information.
        Return as JSON with:
        - content_type: warranty|receipt|bill|other
        - extracted_fields: dict with all key-value pairs
        - confidence: float 0-1
        """
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=[prompt, img]
        )
        
        return self._parse_response(response.text, "image")
    
    def extract_from_text(self, text: str) -> ExtractionResult:
        """Extract from plain text"""
        prompt = f"""
        Extract structured information from this text:
        {text}
        
        Return JSON with extracted fields and confidence.
        """
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )
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
        except Exception as e:
            return ExtractionResult(
                type='unknown',
                extracted_data={},
                confidence_score=0.0,
                raw_data=text,
                flags=[f'Parsing error: {str(e)}']
            )
