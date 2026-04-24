from groq import Groq
from typing import Dict, Any

from config import GROQ_API_KEY, GROQ_MODEL_NAME
from utils import setup_logger, get_optimized_prompt, extract_json_from_response

logger = setup_logger("GroqClient")

class GroqClient:
    def __init__(self):
        if not GROQ_API_KEY:
            logger.warning("GROQ_API_KEY is not set. API calls will fail.")
            
        # Initialize Groq client with timeout parameters
        self.client = Groq(
            api_key=GROQ_API_KEY,
            timeout=15.0, # 15 seconds timeout
            max_retries=2 # Built-in retry logic
        )
        self.model_name = GROQ_MODEL_NAME

    def generate_questions(self, role: str, experience: str, topic: str) -> Dict[str, Any]:
        """
        Calls the Groq API as a fallback to generate interview questions.
        """
        logger.info(f"Generating with Groq -> Role: {role}, Level: {experience}, Topic: {topic}")
        prompt = get_optimized_prompt(role, experience, topic)
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model_name,
                response_format={"type": "json_object"},
                temperature=0.7,
            )
            
            response_content = chat_completion.choices[0].message.content
            return extract_json_from_response(response_content)
            
        except Exception as e:
            logger.error(f"Groq API request failed: {str(e)}")
            raise e
