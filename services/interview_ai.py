"""
AI-powered interview question generation — orchestration layer.

Fallback chain: Gemini API → Groq API → Curated question bank.
This module coordinates the two AI clients and the static fallback.
"""

import random
import logging
import re
from data.interview import FALLBACK_AI_QUESTIONS
from services import gemini_client, groq_client


def count_user_answers(history):
    """
    Count the number of user answers in the interview history.
    
    Only counts items where:
    - role == "user"
    - content is non-empty after stripping whitespace
    
    Args:
        history: List of message dicts with 'role' and 'content' keys
        
    Returns:
        int: Count of user answers, capped at 10
    """
    count = 0
    for item in history:
        if not isinstance(item, dict):
            continue
        if item.get("role") == "user":
            content = str(item.get("content", "")).strip()
            if content:
                count += 1
    return min(count, 10)


def build_history_with_message(history, message):
    """Return history including the current user message (if not already present)."""
    full_history = list(history or [])
    msg = str(message or "").strip()
    if not msg:
        return full_history

    if full_history:
        last = full_history[-1]
        if (
            isinstance(last, dict)
            and last.get("role") == "user"
            and str(last.get("content", "")).strip() == msg
        ):
            return full_history

    full_history.append({"role": "user", "content": msg})
    return full_history


def count_user_answers_with_message(history, message):
    """Count user answers including the message submitted in the current turn."""
    return count_user_answers(build_history_with_message(history, message))

EARLY_WRAP_UP_MARKERS = (
    "this is the final question",
    "this is question 10",
    "this is the 10th question",
    "10th question",
    "after this i will provide",
    "after this, i will provide",
    "interview is complete",
    "end of our mock interview",
    "end of the mock interview",
    "brief summary",
    "summary of your performance",
    "your performance",
    "overall performance",
    "strengths",
    "weaknesses",
    "areas for improvement",
    "overall rating",
    "final rating",
    "recommendations",
    "well-prepared for a real",
)


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


def _fallback_mock_question(category, level, answers_completed):
    """Return a deterministic clean question when AI chat tries to wrap up early."""
    cat_questions = FALLBACK_AI_QUESTIONS.get(category, {})
    pool = list(cat_questions.get(level, []))
    if not pool:
        for level_questions in cat_questions.values():
            pool.extend(level_questions)
    if not pool:
        for category_questions in FALLBACK_AI_QUESTIONS.values():
            for level_questions in category_questions.values():
                pool.extend(level_questions)
    if pool:
        question = pool[answers_completed % len(pool)]['question'].strip()
        return question if question.endswith('?') else f"{question.rstrip('.')}?"
    return f"What is one important concept in {category} that you can explain with an example?"


def _is_valid_in_progress_reply(reply):
    if not reply or '?' not in reply:
        return False

    normalized = ' '.join(str(reply).lower().split())
    return not any(marker in normalized for marker in EARLY_WRAP_UP_MARKERS)


def _clean_in_progress_question(reply):
    """Reduce any in-progress AI reply to one unnumbered question only."""
    if not _is_valid_in_progress_reply(reply):
        return None

    text = ' '.join(str(reply).strip().split())
    question_end = text.rfind('?')
    if question_end < 0:
        return None

    starts = [
        text.rfind('. ', 0, question_end),
        text.rfind('! ', 0, question_end),
        text.rfind('? ', 0, question_end),
    ]
    question_start = max(starts) + 1 if max(starts) >= 0 else 0
    question = text[question_start:question_end + 1].strip()
    question = re.sub(r'^(?:q(?:uestion)?\s*\d+\s*[:.)-]\s*)', '', question, flags=re.IGNORECASE).strip()

    if not _is_valid_in_progress_reply(question):
        return None
    return question


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

    # ── Step 2: Try Groq (secondary fallback) ─────────────────────
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


def conduct_mock_interview(category, level, message, history, answers_completed=0, max_answers=10):
    """
    Conduct a chat-based mock interview turn.

    The application controls when the interview ends (after max_answers user answers).
    AI providers must only ask the next question — never generate the final report.

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
    answers_completed = min(max(int(answers_completed or 0), 0), max_answers)

    # ── Step 1: Try Gemini ──────────────────────────────
    try:
        logging.info(f"[Mock Interview] Attempting Gemini chat for {category}...")
        reply = gemini_client.chat(
            category,
            ai_level,
            message,
            history,
            answers_completed=answers_completed,
            max_answers=max_answers
        )
        logging.info(f"[Mock Interview] Gemini chat returned a reply for {category}")
        if reply:
            question = _clean_in_progress_question(reply)
            if question:
                return question
            logging.warning("[Mock Interview] Gemini attempted early wrap-up; using fallback question")
    except Exception as e:
        logging.warning(f"[Mock Interview] Gemini chat crashed: {type(e).__name__}: {e}")

    # ── Step 2: Try Groq ────────────────────────────────
    try:
        logging.info(f"[Mock Interview] Trying Groq chat fallback...")
        reply = groq_client.chat(
            category,
            ai_level,
            message,
            history,
            answers_completed=answers_completed,
            max_answers=max_answers
        )
        logging.info(f"[Mock Interview] Groq chat returned a reply for {category}")
        if reply:
            question = _clean_in_progress_question(reply)
            if question:
                return question
            logging.warning("[Mock Interview] Groq attempted early wrap-up; using fallback question")
    except Exception as e:
        logging.warning(f"[Mock Interview] Groq chat crashed: {type(e).__name__}: {e}")

    return _fallback_mock_question(category, level, answers_completed)


def generate_mock_interview_report(category, level, history):
    """
    Orchestrate generating the mock interview performance report.
    Fallback order: Gemini -> Groq -> static fallback report.
    """
    # Map level names for AI prompts
    level_map = {
        'beginner': 'Fresher',
        'intermediate': 'Mid-level (2-5 years)',
        'advanced': 'Senior (5+ years)'
    }
    ai_level = level_map.get(level, level.title())

    # 1. Try Gemini
    try:
        logging.info(f"[Interview Report] Attempting Gemini report for {category}...")
        report = gemini_client.generate_report(category, ai_level, history)
        if report:
            return report
    except Exception as e:
        logging.warning(f"[Interview Report] Gemini report crashed: {e}")

    # 2. Try Groq
    try:
        logging.info(f"[Interview Report] Trying Groq report fallback...")
        report = groq_client.generate_report(category, ai_level, history)
        if report:
            return report
    except Exception as e:
        logging.warning(f"[Interview Report] Groq report crashed: {e}")

    # 3. Offline static fallback report
    logging.info("[Interview Report] Using curated offline fallback report")
    # Quick heuristics to score
    ans_count = len([h for h in history if h.get('role') == 'user'])
    score = min(50 + ans_count * 4, 90)

    return {
        "overall_score": score,
        "detailed_evaluation": f"Thank you for completing the {category} mock interview at the {level} level! You demonstrated active engagement and successfully completed {ans_count} response turns during this practice session. Practicing mock interviews regularly builds high-pressure communication skills, structural thinking, and interview confidence.",
        "good_parts": [
            "Consistent participation and dedication throughout the 10-question practice flow.",
            "Structured responses showcasing practical familiarity with the career domain."
        ],
        "bad_parts": [
            "Answers could benefit from more detailed professional frameworks like the STAR method (Situation, Task, Action, Result).",
            "Theoretical concepts need stronger integration with hands-on project examples."
        ],
        "improvement_tips": [
            "Use the STAR method: explicitly outline the Situation, Task, Action you took, and final Result.",
            "Take 5-10 seconds to structure your thoughts before responding to technical questions.",
            "Complete core project roadmaps on Future Map to build stronger portfolio examples.",
            "Review static category questions in the prep panel to solidify core fundamentals."
        ]
    }
