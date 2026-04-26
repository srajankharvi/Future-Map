"""
AI-powered interview question generation — orchestration layer.

Fallback chain: Gemini API → Groq API → Curated question bank.
This module coordinates the two AI clients and the static fallback.
"""

import random
import logging
from data.interview import FALLBACK_AI_QUESTIONS
from services import gemini_client, groq_client


def _get_fallback_questions(category, level, count):
    """
    Get questions from the curated fallback question bank.
    Uses smart 3-phase selection to maximize coverage:
      Phase 1: Exact category + level match
      Phase 2: Same category, any level
      Phase 3: Any category, any level
    """
    cat_questions = FALLBACK_AI_QUESTIONS.get(category, {})

    pool = list(cat_questions.get(level, []))
    random.shuffle(pool)

    result = []

    # Phase 1: Try exact category + level pool
    while len(result) < count and pool:
        result.append(pool.pop(0))

    # Phase 2: If we need more, get from ALL levels in the SAME category
    if len(result) < count:
        other_pool = []
        for l in cat_questions:
            if l != level:
                other_pool.extend(cat_questions[l])
        random.shuffle(other_pool)
        while len(result) < count and other_pool:
            q = other_pool.pop(0)
            if q not in result:
                result.append(q)

    # Phase 3: If STILL need more, get from ANY category
    if len(result) < count:
        any_pool = []
        for c in FALLBACK_AI_QUESTIONS:
            if c != category:
                for l in FALLBACK_AI_QUESTIONS[c]:
                    any_pool.extend(FALLBACK_AI_QUESTIONS[c][l])
        random.shuffle(any_pool)
        while len(result) < count and any_pool:
            q = any_pool.pop(0)
            if q not in result:
                result.append(q)

    return result


def generate_questions(category, level, count, role=None, topic=None):
    """
    Generate interview questions with automatic fallback chain.

    Fallback order:
      1. Gemini API  (primary — best quality)
      2. Groq API    (secondary — fast inference, open-source LLMs)
      3. Static bank (final — curated offline questions)

    Args:
        category: Interview category (e.g., "Computer", "Engineering")
        level:    Difficulty level ("beginner", "intermediate", "advanced")
        count:    Number of questions (1-50)
        role:     Optional job role for more targeted questions
        topic:    Optional specific topic focus

    Returns:
        tuple: (questions_list, source_string)
               source is "gemini", "groq", or "bank"
    """
    # Use role/topic for AI generation, fall back to category for the prompt
    ai_role = role or category
    ai_topic = topic or category

    # Map level names for AI prompts
    level_map = {
        'beginner': 'Fresher',
        'intermediate': 'Mid-level (2-5 years)',
        'advanced': 'Senior (5+ years)'
    }
    ai_level = level_map.get(level, level.title())

    # ── Step 1: Try Gemini (primary) ──────────────────────────────
    try:
        logging.info(f"[Interview AI] Attempting Gemini for {count} questions...")
        questions, source = gemini_client.generate(ai_role, ai_level, ai_topic, count)
        logging.info(f"[Interview AI] Gemini returned {len(questions) if questions else 0} questions")
        if questions:
            return questions, source
    except Exception as e:
        logging.warning(f"[Interview AI] Gemini client crashed: {type(e).__name__}: {e}")

    # ── Step 2: Try Groq (secondary fallback) ─────────────────────
    try:
        logging.info(f"[Interview AI] Trying Groq fallback...")
        questions, source = groq_client.generate(ai_role, ai_level, ai_topic, count)
        logging.info(f"[Interview AI] Groq returned {len(questions) if questions else 0} questions")
        if questions:
            return questions, source
    except Exception as e:
        logging.warning(f"[Interview AI] Groq client crashed: {type(e).__name__}: {e}")

    # ── Step 3: Static question bank (final fallback) ─────────────
    logging.info(f"[Interview AI] Both APIs unavailable, using curated question bank")
    questions = _get_fallback_questions(category, level, count)

    # If even the bank returned nothing, provide a minimal fallback
    if not questions:
        logging.warning(f"[Interview AI] Fallback bank empty for category={category}, level={level}")
        questions = [{
            'question': f'Tell me about your experience with {category}.',
            'answer': 'This is a general question to assess overall familiarity with the field. A good answer covers relevant experience, key skills, and notable projects or achievements.',
            'type': 'conceptual'
        }]

    return questions, 'bank'


def conduct_mock_interview(category, level, message, history):
    """
    Conduct a chat-based mock interview.
    
    Fallback order:
      1. Gemini Chat
      2. Groq Chat
      3. Basic fallback reply
    """
    # Map level names for AI prompts
    level_map = {
        'beginner': 'Fresher',
        'intermediate': 'Mid-level (2-5 years)',
        'advanced': 'Senior (5+ years)'
    }
    ai_level = level_map.get(level, level.title())

    # ── Step 1: Try Gemini ──────────────────────────────
    try:
        logging.info(f"[Mock Interview] Attempting Gemini chat for {category}...")
        reply = gemini_client.chat(category, ai_level, message, history)
        logging.info(f"[Mock Interview] Gemini chat returned a reply for {category}")
        if reply:
            return reply
    except Exception as e:
        logging.warning(f"[Mock Interview] Gemini chat crashed: {type(e).__name__}: {e}")

    # ── Step 2: Try Groq ────────────────────────────────
    try:
        logging.info(f"[Mock Interview] Trying Groq chat fallback...")
        reply = groq_client.chat(category, ai_level, message, history)
        logging.info(f"[Mock Interview] Groq chat returned a reply for {category}")
        if reply:
            return reply
    except Exception as e:
        logging.warning(f"[Mock Interview] Groq chat crashed: {type(e).__name__}: {e}")

    # ── Step 3: Basic Fallback ──────────────────────────
    logging.warning("[Mock Interview] All AI providers failed, using static fallback")
    return "I apologize, but I'm having trouble connecting right now. Please try again in a moment, or reset the interview to start fresh."
