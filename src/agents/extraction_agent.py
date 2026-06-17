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
        self.model_id = "gemini-2.5-flash"

    def extract_from_image(self, image_path: str) -> ExtractionResult:
        import PIL.Image

        img = PIL.Image.open(image_path)

        prompt = """Analyze this image and extract ALL visible information.
You MUST respond with ONLY a JSON object (no markdown, no code fences) in this exact format:
{
  "content_type": "warranty" or "receipt" or "bill" or "other",
  "extracted_fields": {"key": "value", ...},
  "confidence": 0.0 to 1.0
}"""

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=[prompt, img],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        return self._parse_response(response.text, "image")

    def extract_from_text(self, text: str) -> ExtractionResult:
        prompt = f"""Extract structured information from this text:
"{text}"

You MUST respond with ONLY a JSON object (no markdown, no code fences) in this exact format:
{{
  "content_type": "warranty" or "receipt" or "bill" or "other",
  "extracted_fields": {{"key": "value", ...}},
  "confidence": 0.0 to 1.0
}}"""

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return self._parse_response(response.text, "text")

    def _parse_response(self, text: str, source: str) -> ExtractionResult:
        try:
            data = json.loads(text)

            return ExtractionResult(
                type=data.get('content_type', 'unknown'),
                extracted_data=data.get('extracted_fields', {}),
                confidence_score=float(data.get('confidence', 0.0)),
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
