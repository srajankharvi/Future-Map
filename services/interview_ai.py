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

MOCK_FEEDBACK_MAX_WORDS = 35
MOCK_REPLY_MAX_WORDS = 90

# Maximum number of recent history messages to send to the AI.
# Keeping this small prevents the model from "counting" past questions
# and deciding on its own that the interview should end.
MAX_HISTORY_MESSAGES = 6


def _format_mock_position_label(category, level):
    level_map = {
        'beginner': 'Beginner',
        'intermediate': 'Intermediate',
        'advanced': 'Advanced',
    }
    normalized = str(level or '').lower().strip()
    level_label = level_map.get(normalized, str(level).title() if level else 'Beginner')
    return f"{category} Position ({level_label} Level)"


def build_mock_interviewer_system_prompt(category, level, answers_completed, max_answers):
    """Shared system prompt for Gemini and Groq mock interview chat.

    IMPORTANT: The prompt deliberately omits exact progress numbers.
    Telling the model "you are on question 8 of 10" causes it to
    generate wrap-up language, summaries, and farewell messages.
    The backend — not the AI — decides when the interview ends.
    """
    position = _format_mock_position_label(category, level)

    return f"""You are a senior technical interviewer conducting a live mock interview for a "{position}" role.

You sound like a real human interviewer — calm, encouraging, and conversational. You are NOT a quiz app, chatbot, or textbook.

Your ONLY job on every turn is exactly two things:
1. Brief feedback (1-2 short sentences) on what the candidate just said.
2. One follow-up interview question.

That is ALL you do. Nothing else. Ever.

FEEDBACK GUIDELINES:
- Correct answer → affirm briefly ("Right — that's exactly how X works.")
- Partially correct → gently add one missing piece ("Close — you'd also want to mention Y.")
- Incorrect → correct kindly without lecturing ("Not quite — RAM is volatile, not static.")
- Vague → acknowledge and move on ("That's a start — let's keep going.")
- "I don't know" → be supportive ("No worries — that's a common gap.")

QUESTION GUIDELINES:
- Ask exactly ONE question per turn at {level} depth in {category}.
- Prefer follow-ups when their answer invites it; otherwise introduce a related new topic.
- Use natural interview phrasing: "Can you walk me through...", "How would you...", "What happens when..."
- Never number your questions (no "Question 3:", no "Q5.").
- Never answer your own question or give long explanations.

FORMAT (blank line between feedback and question):

[Brief feedback]

[One interview question ending with ?]

STRICT RULES — VIOLATING ANY OF THESE IS FORBIDDEN:
- Keep total reply under {MOCK_REPLY_MAX_WORDS} words.
- Do NOT say the interview is ending, wrapping up, concluding, or finishing.
- Do NOT say "final question", "last question", "one more question", or "concluding question".
- Do NOT say "last check", "check once", "let me check", "let me verify", or any phrase implying a final review before asking the next question.
- Do NOT mention question numbers, progress, or how many questions remain.
- Do NOT generate summaries, scores, ratings, strengths, weaknesses, or performance reviews.
- Do NOT say "good luck", "best of luck", "all the best", or any farewell.
- Do NOT say "interview complete", "that concludes", "we've covered", or "that wraps up".
- Do NOT generate any text that sounds like an interview is ending.
- The application controls when the interview ends. You NEVER decide this.
- Just give feedback and ask the next question. Always. On every single turn.
"""


def _truncate_words(text, max_words):
    words = str(text or "").split()
    if len(words) <= max_words:
        return " ".join(words)
    return " ".join(words[:max_words]).rstrip(".,;:!?")


def _truncate_question_words(question, max_words):
    words = str(question or "").split()
    if len(words) <= max_words:
        return " ".join(words)
    truncated = " ".join(words[:max_words]).rstrip(".,;:!")
    return truncated if truncated.endswith('?') else f"{truncated}?"


def _format_in_progress_reply(brief_ack, question):
    brief_ack = _truncate_words(brief_ack, MOCK_FEEDBACK_MAX_WORDS).strip()
    question = ' '.join(str(question or "").split()).strip()
    if not question:
        return None
    if not brief_ack:
        return _truncate_question_words(question, MOCK_REPLY_MAX_WORDS)

    ack_words = len(brief_ack.split())
    question_words = len(question.split())
    if ack_words + question_words <= MOCK_REPLY_MAX_WORDS:
        return f"{brief_ack}\n\n{question}"

    max_ack = min(MOCK_FEEDBACK_MAX_WORDS, MOCK_REPLY_MAX_WORDS - question_words)
    if max_ack >= 3:
        brief_ack = _truncate_words(brief_ack, max_ack)
        return f"{brief_ack}\n\n{question}"

    max_question_words = max(5, MOCK_REPLY_MAX_WORDS - len(brief_ack.split()))
    question = _truncate_question_words(question, max_question_words)
    return f"{brief_ack}\n\n{question}"


EARLY_WRAP_UP_MARKERS = (
    # Explicit question numbering / finality
    "this is the final question",
    "this is the last question",
    "this is question 10",
    "this is the 10th question",
    "10th question",
    "last question",
    "final question",
    "concluding question",
    "one more question",
    "one last question",
    # Post-interview language
    "after this i will provide",
    "after this, i will provide",
    "interview is complete",
    "interview is over",
    "interview has concluded",
    "end of our mock interview",
    "end of the mock interview",
    "end of interview",
    "that wraps up",
    "that concludes",
    "we've covered",
    "let me summarize",
    "to sum up",
    "to summarize",
    "in summary",
    "closing remarks",
    "wrap up",
    "wrapping up",
    "last check",
    "check once",
    "let me check",
    "let me verify",
    "one last check",
    "one more check",
    "before i continue",
    "before moving on",
    "before i ask",
    # Summaries and ratings
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
    # Farewells
    "good luck",
    "best of luck",
    "all the best",
    "wish you",
    "thank you for your time",
    "enjoyed interviewing",
    "it was great interviewing",
    "pleasure interviewing",
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
        question = question if question.endswith('?') else f"{question.rstrip('.')}?"
        brief_acks = (
            "Thanks — that's a fair answer, and you touched on the main idea.",
            "Good, I follow your reasoning there. That makes sense.",
            "Okay — you mentioned something useful. Let's build on that.",
            "Right, I see where you're going with that. Nice effort.",
        )
        ack = brief_acks[answers_completed % len(brief_acks)]
        return f"{ack}\n\n{question}"
    return f"What is one important concept in {category} that you can explain with an example?"


def _strip_meta_parentheticals(text):
    """Remove parenthetical meta about question count or upcoming feedback."""
    return re.sub(
        r'\([^)]*(?:question|final|summary|feedback|performance|10th|after this)[^)]*\)',
        '',
        text,
        flags=re.IGNORECASE,
    )


def _extract_question_sentence(text):
    """Return the final interview question sentence from a reply."""
    text = ' '.join(str(text).strip().split())
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
    question = re.sub(
        r'^(?:q(?:uestion)?\s*\d+\s*[:.)-]\s*)',
        '',
        question,
        flags=re.IGNORECASE,
    ).strip()
    return question if question.endswith('?') else None


def _is_valid_in_progress_reply(reply):
    if not reply or '?' not in reply:
        return False

    normalized = ' '.join(str(reply).lower().split())
    return not any(marker in normalized for marker in EARLY_WRAP_UP_MARKERS)


def _clean_in_progress_reply(reply):
    """Keep 1-2 feedback sentences plus the next question; block early wrap-up."""
    if not reply:
        return None

    text = _strip_meta_parentheticals(str(reply).strip())
    normalized = ' '.join(text.split())

    if not _is_valid_in_progress_reply(normalized):
        return None

    question_end = normalized.rfind('?')
    question = _extract_question_sentence(normalized)
    if not question:
        return None

    starts = [
        normalized.rfind('. ', 0, question_end),
        normalized.rfind('! ', 0, question_end),
        normalized.rfind('? ', 0, question_end),
    ]
    question_start = max(starts) + 1 if max(starts) >= 0 else 0
    acknowledgment = normalized[:question_start].strip()

    if acknowledgment:
        ack_sentences = re.split(r'(?<=[.!])\s+', acknowledgment)
        brief_ack = ' '.join(s.strip() for s in ack_sentences[:2] if s).strip()
        if brief_ack:
            return _format_in_progress_reply(brief_ack, question)

    return _truncate_question_words(question, MOCK_REPLY_MAX_WORDS)


def _clean_in_progress_question(reply):
    """Backward-compatible alias."""
    return _clean_in_progress_reply(reply)


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

    # Truncate history to prevent the AI from counting past questions
    # and deciding to end the interview on its own.
    truncated_history = list(history or [])[-MAX_HISTORY_MESSAGES:]

    logging.info(
        "[Mock Interview] turn | category=%s level=%s user_answer_count=%d "
        "backend_progress=%d/%d history_len=%d truncated_to=%d",
        category, level, answers_completed, answers_completed, max_answers,
        len(history or []), len(truncated_history)
    )

    # ── Step 1: Try Gemini ──────────────────────────────
    try:
        logging.info(f"[Mock Interview] Attempting Gemini chat for {category}...")
        reply = gemini_client.chat(
            category,
            ai_level,
            message,
            truncated_history,
            answers_completed=answers_completed,
            max_answers=max_answers
        )
        if reply:
            cleaned = _clean_in_progress_reply(reply)
            if cleaned:
                logging.info("[Mock Interview] Gemini reply accepted (answer %d/%d)", answers_completed, max_answers)
                return cleaned
            logging.warning(
                "[Mock Interview] Gemini attempted early wrap-up (answer %d/%d); "
                "blocked reply: %.200s",
                answers_completed, max_answers, reply
            )
    except Exception as e:
        logging.warning(f"[Mock Interview] Gemini chat crashed: {type(e).__name__}: {e}")

    # ── Step 2: Try Groq ────────────────────────────────
    try:
        logging.info(f"[Mock Interview] Trying Groq chat fallback...")
        reply = groq_client.chat(
            category,
            ai_level,
            message,
            truncated_history,
            answers_completed=answers_completed,
            max_answers=max_answers
        )
        if reply:
            cleaned = _clean_in_progress_reply(reply)
            if cleaned:
                logging.info("[Mock Interview] Groq reply accepted (answer %d/%d)", answers_completed, max_answers)
                return cleaned
            logging.warning(
                "[Mock Interview] Groq attempted early wrap-up (answer %d/%d); "
                "blocked reply: %.200s",
                answers_completed, max_answers, reply
            )
    except Exception as e:
        logging.warning(f"[Mock Interview] Groq chat crashed: {type(e).__name__}: {e}")

    logging.info(
        "[Mock Interview] Both AI providers failed/blocked; using fallback question "
        "(answer %d/%d)", answers_completed, max_answers
    )
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
