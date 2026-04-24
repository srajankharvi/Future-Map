import json
import logging
from typing import Dict, Any

def setup_logger(name: str) -> logging.Logger:
    """
    Sets up a simple console logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid adding duplicate handlers if the logger is instantiated multiple times
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

def get_optimized_prompt(role: str, experience: str, topic: str) -> str:
    """
    Generates a strict prompt that compels the LLMs to output purely JSON.
    """
    return f"""You are an expert technical interviewer. 
Your task is to generate exactly 5 interview questions for the specified role.

Requirements:
- Role: {role}
- Experience Level: {experience}
- Topic: {topic}
- Questions should challenge the candidate appropriately based on their experience level.

OUTPUT FORMAT:
You MUST respond with ONLY valid JSON in the exact structure shown below. 
Do not include any introductory text, markdown code blocks (like ```json), or concluding notes.
{{
  "questions": [
    "Insert question 1 here",
    "Insert question 2 here",
    "Insert question 3 here",
    "Insert question 4 here",
    "Insert question 5 here"
  ]
}}
"""

def extract_json_from_response(text: str) -> Dict[str, Any]:
    """
    Helper to cleanly parse a JSON string from an LLM response, handling markdown blocks if the LLM fails to omit them.
    """
    text = text.strip()
    
    # Remove markdown formatting if the LLM ignored our "no markdown" rule
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
        
    if text.endswith("```"):
        text = text[:-3]
        
    text = text.strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # We can add further logic to fix broken JSON if needed
        raise ValueError(f"Failed to parse JSON from AI response. String: {text} | Error: {str(e)}")
