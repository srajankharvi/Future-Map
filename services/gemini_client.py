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

    try:
        # Configure API key and create model
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Build optimized prompt
        prompt = _build_prompt(role, level, topic, count)

        logging.info(f"[Gemini] Generating {count} questions: role={role}, level={level}, topic={topic}")

        # Call the API with timeout settings
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,       # Balanced creativity vs consistency
                max_output_tokens=4096  # Enough for ~50 questions
            )
        )

        # Parse and clean response
        raw_text = _clean_response(response.text)
        questions = json.loads(raw_text)

        # Validate structure
        validated = _validate_questions(questions, count)
        if validated:
            logging.info(f"[Gemini] Successfully generated {len(validated)} questions")
            return validated, 'gemini'

        logging.warning("[Gemini] Response parsed but validation failed — no valid questions found")
        return None, None

    except json.JSONDecodeError as e:
        logging.warning(f"[Gemini] JSON parse error: {e}")
    except Exception as e:
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
        
        genai.configure(api_key=gemini_key)
        # Use system_instruction if available in this model version
        model = genai.GenerativeModel(
            'gemini-2.5-flash',
            system_instruction=system_prompt
        )

        # Convert history format
        contents = []
        for h in history:
            role = 'user' if h['role'] == 'user' else 'model'
            contents.append({'role': role, 'parts': [h['content']]})
        
        # Start chat with existing history
        chat_session = model.start_chat(history=contents)
        
        # Send current message
        response = chat_session.send_message(message)
        return response.text.strip()

    except Exception as e:
        logging.warning(f"[Gemini Chat] Error: {e}")
        return None
