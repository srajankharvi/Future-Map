import json
from typing import Dict, Any

from utils import setup_logger
from gemini_client import GeminiClient
from groq_client import GroqClient

logger = setup_logger("Main")

class InterviewQuestionGenerator:
    """
    Main orchestration class that coordinates the generation of interview questions.
    It handles calling the primary provider (Gemini) and falling back gracefully to Groq.
    """
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.groq_client = GroqClient()

    def generate(self, role: str, experience: str, topic: str) -> Dict[str, Any]:
        """
        Executes the question generation pipeline with fallback.
        Returns a dict conforming to the {"questions": [...]} schema.
        """
        # 1. Primary Attempt: Gemini API
        try:
            logger.info("--- Attempting Primary Provider (Gemini) ---")
            return self.gemini_client.generate_questions(role, experience, topic)
        except Exception as gemini_err:
            # We catch any Exception here (Timeout, RateLimit, APIError)
            logger.warning(f"Primary provider failed: {str(gemini_err)}. Initiating fallback...")
            
            # 2. Fallback Attempt: Groq API
            try:
                logger.info("--- Attempting Fallback Provider (Groq) ---")
                return self.groq_client.generate_questions(role, experience, topic)
            except Exception as groq_err:
                logger.error(f"Fallback provider also failed: {str(groq_err)}")
                
                # 3. Complete Failure: Return safe fallback JSON payload
                return {
                    "error": "Both primary and fallback AI generation failed. Please try again later.",
                    "questions": []
                }

if __name__ == "__main__":
    # Example usage for testing locally
    print("Initializing Interview Question Generator...\n")
    
    generator = InterviewQuestionGenerator()
    
    test_role = "Backend Developer"
    test_experience = "Mid-Level"
    test_topic = "Python, System Architecture, and Databases"
    
    print(f"Generating questions for: {test_experience} {test_role} in {test_topic}...")
    
    result = generator.generate(test_role, test_experience, test_topic)
    
    # Prettify the output
    print("\n--- RESULTS ---")
    print(json.dumps(result, indent=2))
