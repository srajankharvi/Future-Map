import google as genai
from typing import Dict, Any

from config import GEMINI_API_KEY, GEMINI_MODEL_NAME
from utils import setup_logger, get_optimized_prompt, extract_json_from_response

logger = setup_logger("GeminiClient")

class GeminiClient:
    def __init__(self):
        if not GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY is not set. API calls will fail.")
        
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Using Gemini 1.5 with JSON output enabled
        self.model = genai.GenerativeModel(
            model_name=GEMINI_MODEL_NAME,
            generation_config={"response_mime_type": "application/json"}
        )

    def generate_questions(self, role: str, experience: str, topic: str) -> Dict[str, Any]:
        """
        Calls the Gemini API to generate interview questions.
        """
        logger.info(f"Generating with Gemini -> Role: {role}, Level: {experience}, Topic: {topic}")
        prompt = get_optimized_prompt(role, experience, topic)
        
        try:
            # We rely on the google-generativeai built-in behavior for requests.
            # Timeout/retries are handled deeply by google-api-core or can be overridden.
            response = self.model.generate_content(prompt)
            
            if response.text:
                return extract_json_from_response(response.text)
            else:
                raise ValueError("Received empty or blocked response from Gemini.")
                
        except Exception as e:
            logger.error(f"Gemini API request failed: {str(e)}")
            raise e
