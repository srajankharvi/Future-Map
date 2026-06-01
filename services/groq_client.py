"""
Groq API client for AI-powered interview question generation.

Groq provides ultra-fast inference on open-source LLMs (LLaMA, Mixtral).
Used as fallback when Gemini is unavailable, rate-limited, or times out.
"""

import os
import json
import logging
import requests

# Groq API endpoint (REST-based, no SDK needed)
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Default model — Groq's fastest and most capable model
GROQ_MODEL = "llama-3.3-70b-versatile"

# Request timeout in seconds
GROQ_TIMEOUT = 30


def _build_prompt(role, level, topic, count):
    """
    Build an optimized prompt for Groq (LLaMA-based models).
    Slightly more explicit than Gemini prompts since open-source models
    need clearer instructions for structured output.
    """
    return f"""You are a senior technical interviewer at a top company.
Generate exactly {count} realistic interview questions.

Details:
- Role: {role}
- Experience Level: {level}
- Topic: {topic}

Rules:
1. Each question must be unique
2. Difficulty must match the experience level:
   - Fresher = basics and fundamentals
   - Mid = application, trade-offs, debugging
   - Senior = architecture, scalability, leadership
3. Mix question types: conceptual, scenario-based, and problem-solving
4. Answers must be 3-6 sentences, accurate, and practical
5. Questions should feel like a real company interview

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "question": "...",
    "answer": "...",
    "type": "conceptual" or "scenario" or "problem"
  }}
]

IMPORTANT: Output ONLY the JSON array. No markdown fences. No explanation. No extra text."""


def _clean_response(text):
    """Strip markdown code fences if present in Groq response."""
    text = text.strip()
    if text.startswith('```'):
        text = text.split('\n', 1)[1] if '\n' in text else text[3:]
    if text.endswith('```'):
        text = text[:-3].strip()
    if text.startswith('json'):
        text = text[4:].strip()
    return text


def _validate_questions(raw_questions, count):
    """Validate and normalize parsed questions from Groq response."""
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
    Generate interview questions using Groq API (LLaMA-based).

    Uses the OpenAI-compatible REST API — no SDK required.

    Args:
        role:  Target job role (e.g., "Frontend Developer")
        level: Experience level ("fresher", "mid", "senior")
        topic: Focus area (e.g., "DSA", "System Design", "HR")
        count: Number of questions to generate (1-50)

    Returns:
        tuple: (questions_list, "groq") on success, (None, None) on failure
    """
    # --- Pre-flight checks ---
    groq_key = os.getenv('GROQ_API_KEY', '').strip()
    if not groq_key or groq_key == 'your-groq-api-key-here':
        logging.info("Groq API key not configured, skipping")
        return None, None

    try:
        # Build request payload (OpenAI-compatible format)
        prompt = _build_prompt(role, level, topic, count)

        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert interview question generator. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 4096,
            "stream": False
        }

        headers = {
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        }

        logging.info(f"[Groq] Generating {count} questions: role={role}, level={level}, topic={topic}")

        # Make the API call with timeout
        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=GROQ_TIMEOUT
        )

        # Check for HTTP errors
        if response.status_code != 200:
            logging.warning(f"[Groq] HTTP {response.status_code}: {response.text[:200]}")
            return None, None

        # Extract the assistant's message content
        data = response.json()
        choices = data.get('choices') or []
        if not choices:
            logging.warning("[Groq] Response missing choices")
            return None, None
        content = (choices[0].get('message') or {}).get('content')
        if not content:
            logging.warning("[Groq] Response missing message content")
            return None, None

        # Parse and clean response
        raw_text = _clean_response(content)
        questions = json.loads(raw_text)

        # Validate structure
        validated = _validate_questions(questions, count)
        if validated:
            logging.info(f"[Groq] Successfully generated {len(validated)} questions")
            return validated, 'groq'

        logging.warning("[Groq] Response parsed but validation failed — no valid questions found")
        return None, None

    except requests.exceptions.Timeout:
        logging.warning(f"[Groq] Request timed out after {GROQ_TIMEOUT}s")
    except requests.exceptions.ConnectionError:
        logging.warning("[Groq] Connection error — check internet connectivity")
    except json.JSONDecodeError as e:
        logging.warning(f"[Groq] JSON parse error: {e}")
    except Exception as e:
        logging.warning(f"[Groq] API call failed: {type(e).__name__}: {e}")

    return None, None


def chat(category, level, message, history, answers_completed=0, max_answers=10):
    """
    Handle an interactive chat turn with Groq.

    Note: question_count / max_questions params were removed to ensure
    a single source of truth for progress tracking (the backend route).
    """
    groq_key = os.getenv('GROQ_API_KEY', '').strip()
    if not groq_key or groq_key == 'your-groq-api-key-here':
        return None

    try:
        answers_completed = min(max(int(answers_completed or 0), 0), max_answers)
        from services.interview_ai import build_mock_interviewer_system_prompt, MAX_HISTORY_MESSAGES

        system_prompt = build_mock_interviewer_system_prompt(
            category, level, answers_completed, max_answers
        )

        # Truncate history to keep the AI focused and prevent it from
        # counting questions and deciding to end the interview.
        truncated = list(history or [])[-MAX_HISTORY_MESSAGES:]

        # Construct messages for OpenAI-style API
        messages = [{"role": "system", "content": system_prompt}]
        for h in truncated:
            if not isinstance(h, dict) or not h.get('content'):
                continue
            role = "assistant" if h.get('role') in {'ai', 'assistant', 'model'} else "user"
            messages.append({"role": role, "content": str(h.get('content'))[:1000]})

        messages.append({"role": "user", "content": message})

        payload = {
            "model": GROQ_MODEL,
            "messages": messages,
            "temperature": 0.5,
            "max_tokens": 200,
            "stream": False
        }

        headers = {
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=GROQ_TIMEOUT)

        if response.status_code == 200:
            data = response.json()
            choices = data.get('choices') or []
            if not choices:
                return None
            content = (choices[0].get('message') or {}).get('content')
            return content.strip() if content else None

        return None

    except Exception as e:
        logging.warning(f"[Groq Chat] Error: {e}")
        return None


def generate_report(category, level, history):
    """
    Generate a comprehensive feedback report on the completed mock interview session using Groq.
    """
    groq_key = os.getenv('GROQ_API_KEY', '').strip()
    if not groq_key or groq_key == 'your-groq-api-key-here':
        return None

    try:
        # Construct the history text
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

IMPORTANT: Output ONLY the JSON object. No extra text before or after the JSON object."""

        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional technical recruiter. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2048,
            "stream": False
        }

        headers = {
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        }

        logging.info(f"[Groq Report] Requesting performance report for {category}...")
        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=GROQ_TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()
            choices = data.get('choices') or []
            if not choices:
                return None
            content = (choices[0].get('message') or {}).get('content')
            if content:
                raw_text = _clean_response(content)
                report = json.loads(raw_text)
                if isinstance(report, dict) and 'overall_score' in report and 'good_parts' in report:
                    logging.info(f"[Groq Report] Successfully generated performance report")
                    return report
        return None
    except Exception as e:
        logging.warning(f"[Groq Report] Error: {e}")
        return None
