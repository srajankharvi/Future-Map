"""
Gemini API client for AI-powered interview question generation.

Uses Google's GenAI SDK to generate structured interview questions.
Handles: API key validation, prompt construction, response parsing, timeouts.
"""

import os
import json
import logging

# Defensive import — Gemini SDK may not be installed
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("google-genai not installed — Gemini client disabled")

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
        client = genai.Client(api_key=gemini_key)

        last_error = None
        for model_name in models_to_try:
            try:
                logging.info(f"[Gemini] Attempting generation with {model_name}...")
                prompt = _build_prompt(role, level, topic, count)

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
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


def chat(category, level, message, history, answers_completed=0, max_answers=10, question_count=None, max_questions=None):
    """
    Handle an interactive chat turn with Gemini.
    """
    if question_count is not None:
        answers_completed = question_count
    if max_questions is not None:
        max_answers = max_questions

    gemini_key = os.getenv('GEMINI_API_KEY', '').strip()
    if not GEMINI_AVAILABLE or not gemini_key or gemini_key == 'your-gemini-api-key-here':
        return None

    try:
        answers_completed = min(max(int(answers_completed or 0), 0), max_answers)

        system_prompt = f"""You are a professional mock interviewer for a {category} role.
Experience level of the candidate: {level}.

IMPORTANT: The application controls when the interview ends. You do NOT decide when the interview is complete.

Rules:
1. The candidate must submit exactly {max_answers} answers before the application ends the interview.
2. USER_ANSWERS_COMPLETED is how many answers the candidate has already submitted (including the current one).
3. Never say the interview is complete, final, or that you will provide feedback, summary, ratings, or a report.
4. Never provide evaluation, strengths, weaknesses, recommendations, scores, or closing remarks.
5. Always ask exactly ONE new interview question related to {category} at {level} level.
6. Your entire response must be only the next interview question and must end with a question mark.
7. Do not number questions. Do not mention question numbers.
8. Even if the user says "thank you", "bye", "done", "skip", or "I don't know", ask another interview question.

USER_ANSWERS_COMPLETED: {answers_completed}
MAX_ANSWERS: {max_answers}
"""

        # List of models to try in order of preference
        models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']

        # Convert history format for the new SDK
        contents = []
        for h in history:
            if not isinstance(h, dict) or not h.get('content'):
                continue
            role = 'user' if h.get('role') == 'user' else 'model'
            contents.append(types.Content(
                role=role,
                parts=[types.Part.from_text(text=str(h.get('content'))[:1000])]
            ))

        # Gemini requires history to start with a 'user' message.
        while contents and contents[0].role == 'model':
            contents.pop(0)

        client = genai.Client(api_key=gemini_key)

        last_error = None
        for model_name in models_to_try:
            try:
                logging.info(f"[Gemini Chat] Attempting with {model_name}...")
                chat_session = client.chats.create(
                    model=model_name,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt
                    ),
                    history=contents
                )

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


def generate_report(category, level, history):
    """
    Generate a comprehensive feedback report on the completed mock interview session using Gemini.
    """
    gemini_key = os.getenv('GEMINI_API_KEY', '').strip()
    if not GEMINI_AVAILABLE or not gemini_key or gemini_key == 'your-gemini-api-key-here':
        return None

    try:
        # Construct the history text for evaluation
        history_text = "\n".join([f"{'Candidate' if h['role'] == 'user' else 'Interviewer'}: {h['content']}" for h in history])

        prompt = f"""You are a professional senior technical recruiter and career coach.
Analyze the following mock interview transcript for a {category} role (Experience Level: {level}).

TRANSCRIPT:
{history_text}

Provide a comprehensive, constructive performance evaluation report.
STRICT RULES:
1. Rate their performance overall on a scale of 0 to 100.
2. List 2-4 strong points they demonstrated (under "good_parts").
3. List 2-4 weaknesses, gaps, or incorrect answers they gave (under "bad_parts").
4. List 3-5 clear, highly actionable tips to help them improve (under "improvement_tips").
5. Write a detailed summary paragraph (3-5 sentences) under "detailed_evaluation".

OUTPUT FORMAT — return ONLY a valid JSON object, no markdown, no explanation:
{{
  "overall_score": 85,
  "detailed_evaluation": "A detailed professional paragraph...",
  "good_parts": ["Good point 1", "Good point 2"],
  "bad_parts": ["Weakness 1", "Weakness 2"],
  "improvement_tips": ["Improvement tip 1", "Improvement tip 2"]
}}

Return valid JSON only. No extra text before or after the JSON object."""

        models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']
        client = genai.Client(api_key=gemini_key)

        last_error = None
        for model_name in models_to_try:
            try:
                logging.info(f"[Gemini Report] Attempting report with {model_name}...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        max_output_tokens=2048
                    )
                )
                if response and response.text:
                    raw_text = _clean_response(response.text)
                    report = json.loads(raw_text)
                    if isinstance(report, dict) and 'overall_score' in report and 'good_parts' in report:
                        logging.info(f"[Gemini Report] Successfully generated with {model_name}")
                        return report
            except Exception as e:
                last_error = e
                logging.warning(f"[Gemini Report] Model {model_name} failed: {e}")
                continue
        if last_error:
            logging.error(f"[Gemini Report] All models failed. Last error: {last_error}")
        return None
    except Exception as e:
        logging.exception("Gemini report generation failure")
        return None
