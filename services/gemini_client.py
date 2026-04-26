"""
Gemini API client for AI-powered interview question generation.

Uses Google's Generative AI SDK to generate structured interview questions.
Handles: API key validation, prompt construction, response parsing, timeouts.
"""

import os
import json
import logging

# Defensive import — Gemini SDK may not be installed
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("google-generativeai not installed — Gemini client disabled")

try:
    from google.api_core import exceptions as google_exceptions
except ImportError:
    google_exceptions = None


def _build_prompt(role, level, topic, count):
    """
    Build an optimized prompt for high-quality interview questions.
    Uses specific instructions to minimize hallucination and maximize relevance.
    """
    return f"""You are a senior technical interviewer at a top-tier company (Google, Amazon, Microsoft level).
Your job is to create realistic interview questions that would actually be asked in a real interview.

Generate exactly {count} high-quality interview questions for:
- Role: {role}
- Experience Level: {level}
- Topic / Focus Area: {topic}

STRICT RULES:
1. Every question MUST be unique — no duplicates or paraphrases
2. Tailor difficulty precisely to the experience level:
   - Fresher: Fundamentals, definitions, simple scenarios
   - Mid-level: Application, trade-offs, design decisions, debugging
   - Senior: Architecture, scalability, leadership, system design, mentoring
3. Include a realistic mix of question types:
   - "conceptual" → theory, definitions, comparisons
   - "scenario"   → real-world situations, debugging, decision-making
   - "problem"    → coding challenges, design problems, optimization
4. Each answer must be 3-6 sentences, technically accurate, and practical
5. Questions must feel like a real interview — not textbook exercises
6. For technical roles: include code-relevant examples where appropriate
7. For non-technical roles: include behavioral and situational questions

OUTPUT FORMAT — return ONLY a valid JSON array, no markdown, no explanation:
[
  {{
    "question": "Your question here",
    "answer": "Detailed, accurate answer here",
    "type": "conceptual" | "scenario" | "problem"
  }}
]

Return valid JSON only. No extra text before or after the array."""


def _clean_response(text):
    """
    Strip markdown code fences and language tags from API response.
    Gemini sometimes wraps JSON in ```json ... ``` blocks.
    """
    text = text.strip()
    # Remove leading ```json or ```
    if text.startswith('```'):
        text = text.split('\n', 1)[1] if '\n' in text else text[3:]
    # Remove trailing ```
    if text.endswith('```'):
        text = text[:-3].strip()
    # Remove bare "json" prefix
    if text.startswith('json'):
        text = text[4:].strip()
    return text


def _validate_questions(raw_questions, count):
    """
    Validate and normalize the parsed question list.
    Returns a clean list of dicts with guaranteed keys, or empty list on failure.
    """
    if not isinstance(raw_questions, list) or len(raw_questions) == 0:
        return []

    validated = []
    for q in raw_questions[:count]:
        if isinstance(q, dict) and 'question' in q and 'answer' in q:
            validated.append({
                'question': str(q['question']).strip(),
                'answer': str(q['answer']).strip(),
                'type': str(q.get('type', 'conceptual')).strip()
            })
    return validated


def generate(role, level, topic, count=5):
    """
    Generate interview questions using Google Gemini API.

    Args:
        role:  Target job role (e.g., "Frontend Developer")
        level: Experience level ("fresher", "mid", "senior")
        topic: Focus area (e.g., "DSA", "System Design", "HR")
        count: Number of questions to generate (1-50)

    Returns:
        tuple: (questions_list, "gemini") on success, (None, None) on failure
    """
    # --- Pre-flight checks ---
    gemini_key = os.getenv('GEMINI_API_KEY', '').strip()
    if not GEMINI_AVAILABLE:
        logging.info("Gemini SDK not available, skipping")
        return None, None
    if not gemini_key or gemini_key == 'your-gemini-api-key-here':
        logging.info("Gemini API key not configured, skipping")
        return None, None

    # List of models to try in order of preference
    models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']
    
    try:
        genai.configure(api_key=gemini_key)
        
        last_error = None
        for model_name in models_to_try:
            try:
                logging.info(f"[Gemini] Attempting generation with {model_name}...")
                model = genai.GenerativeModel(model_name)
                prompt = _build_prompt(role, level, topic, count)
                
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=4096
                    )
                )
                
                if not response or not response.text:
                    continue

                raw_text = _clean_response(response.text)
                questions = json.loads(raw_text)
                
                validated = _validate_questions(questions, count)
                if validated:
                    logging.info(f"[Gemini] Successfully generated with {model_name}")
                    return validated, 'gemini'
            
            except Exception as e:
                last_error = e
                logging.warning(f"[Gemini] Model {model_name} failed: {e}")
                continue
        
        if last_error:
            logging.error(f"[Gemini] All models failed. Last error: {last_error}")
        return None, None
    except Exception as e:
        logging.exception("Gemini total failure")
        return None, None

    except json.JSONDecodeError as e:
        logging.warning(f"[Gemini] JSON parse error: {e}")
    except Exception as e:
        if google_exceptions and isinstance(e, google_exceptions.ResourceExhausted):
            logging.warning(f"[Gemini] Quota exceeded or rate limited (ResourceExhausted). Falling back...")
        else:
            logging.warning(f"[Gemini] API call failed: {type(e).__name__}: {e}")

    return None, None


def chat(category, level, message, history):
    """
    Handle an interactive chat turn with Gemini.
    """
    gemini_key = os.getenv('GEMINI_API_KEY', '').strip()
    if not GEMINI_AVAILABLE or not gemini_key or gemini_key == 'your-gemini-api-key-here':
        return None

    try:
        # Construct a system-like prompt for the interview context
        system_prompt = f"""You are a professional technical interviewer for a {category} role.
Experience level of the candidate: {level}.
Your goal is to conduct a realistic mock interview.
- Be professional but encouraging.
- Ask one question at a time.
- Provide brief feedback if the candidate answers well or correct them if they are wrong.
- After feedback, move to the next logical question.
- Keep responses concise (2-4 sentences).
- After 10 questions, wrap up the interview and provide a brief summary of their performance.
- If the candidate says they are ready, start with the first technical question.
"""
        
        # List of models to try in order of preference
        models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']
        
        # Convert history format
        contents = []
        for h in history:
            role = 'user' if h['role'] == 'user' else 'model'
            contents.append({'role': role, 'parts': [h['content']]})
        
        # Gemini requires history to start with a 'user' message.
        while contents and contents[0]['role'] == 'model':
            contents.pop(0)

        genai.configure(api_key=gemini_key)
        
        last_error = None
        for model_name in models_to_try:
            try:
                logging.info(f"[Gemini Chat] Attempting with {model_name}...")
                model = genai.GenerativeModel(
                    model_name,
                    system_instruction=system_prompt
                )
                
                chat_session = model.start_chat(history=contents)
                response = chat_session.send_message(message)
                
                if response and response.text:
                    return response.text.strip()
            
            except Exception as e:
                last_error = e
                logging.warning(f"[Gemini Chat] Model {model_name} failed: {e}")
                continue
        
        if last_error:
            if google_exceptions and isinstance(last_error, google_exceptions.ResourceExhausted):
                logging.warning(f"[Gemini Chat] Quota exceeded. Falling back to Groq...")
            else:
                logging.error(f"[Gemini Chat] All models failed. Last error: {last_error}")
        return None

    except Exception as e:
        logging.exception("Gemini chat total failure")
        return None
