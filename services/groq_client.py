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
        content = data['choices'][0]['message']['content']

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
