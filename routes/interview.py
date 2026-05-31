"""
Interview routes — static questions + AI-powered question generation.
"""

import logging
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request, session
from bson import ObjectId
from pymongo import ReturnDocument
from pydantic import ValidationError

from database import mongo_db

from schemas import AIQuestionRequestSchema, MockInterviewRequestSchema, MockInterviewReportRequestSchema
from utils import csrf_protect, login_required
from extensions import limiter
from data.interview import FALLBACK_INTERVIEW_QUESTIONS, AI_INTERVIEW_CATEGORIES
from services.interview_ai import generate_questions

interview_bp = Blueprint('interview', __name__)

DAILY_INTERVIEW_LIMIT = 5
MAX_MOCK_QUESTIONS = 10


def _today_str():
    return datetime.now(timezone.utc).date().isoformat()


def _validation_error_summary(error):
    """Return validation errors without echoing user-provided input."""
    summary = []
    for item in error.errors():
        loc = item.get('loc') or ('Field',)
        summary.append({
            'field': '.'.join(str(part) for part in loc),
            'message': item.get('msg', 'Invalid value'),
            'type': item.get('type', 'validation_error')
        })
    return summary


def _estimate_mock_questions_asked(history):
    """Best-effort progress estimate for older clients that omit question_count."""
    question_count = -1
    for item in history:
        if not isinstance(item, dict):
            continue
        role = item.get('role')
        content = str(item.get('content', ''))
        if role not in {'ai', 'assistant', 'model'} or '?' not in content:
            continue
        if 'ready to begin' in content.lower():
            continue
        question_count += 1
    return min(question_count, MAX_MOCK_QUESTIONS)


def _increment_daily_counter(user_id, count_field, date_field, limit=DAILY_INTERVIEW_LIMIT):
    """Atomically increment a per-user daily counter if it is below the limit."""
    if mongo_db is None:
        return True, 0

    oid = ObjectId(user_id)
    current_date_str = _today_str()
    user = mongo_db.users.find_one({'_id': oid}, {count_field: 1, date_field: 1})
    if not user:
        return False, 0

    if user.get(date_field) != current_date_str:
        mongo_db.users.update_one(
            {'_id': oid},
            {'$set': {count_field: 0, date_field: current_date_str}}
        )

    updated = mongo_db.users.find_one_and_update(
        {
            '_id': oid,
            date_field: current_date_str,
            '$or': [
                {count_field: {'$lt': limit}},
                {count_field: {'$exists': False}}
            ]
        },
        {'$inc': {count_field: 1}},
        projection={count_field: 1},
        return_document=ReturnDocument.AFTER
    )

    if not updated:
        return False, limit
    return True, updated.get(count_field, 0)


@interview_bp.route('/api/interview-questions', methods=['GET'])
def get_interview_questions():
    """Get interview questions from MongoDB"""
    try:
        questions = []
        if mongo_db is not None:
            questions = list(mongo_db.interview_questions.find({}, {'_id': 0}))

        if not questions:
            questions = FALLBACK_INTERVIEW_QUESTIONS

        return jsonify({'success': True, 'data': questions}), 200

    except Exception as e:
        logging.exception("Interview questions fetch error")
        return jsonify({'success': False, 'error': 'Could not load interview questions'}), 500


@interview_bp.route('/api/generate-interview-questions', methods=['POST'])
@login_required
@limiter.limit("10 per minute")
@csrf_protect
def generate_interview_questions():
    """
    Generate AI-powered interview questions.

    Accepts both the original format (category + level) and the enhanced
    format (role + level + topic) for richer question generation.

    Fallback chain: Gemini → Groq → curated question bank.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        try:
            schema = AIQuestionRequestSchema(**data)
        except ValidationError as e:
            msg = e.errors()[0]['msg']
            field = e.errors()[0]['loc'][0] if e.errors()[0].get('loc') else 'Field'
            return jsonify({'success': False, 'error': f'{field}: {msg}'}), 400

        category = schema.category
        level = schema.level
        count = schema.count

        # Enhanced parameters (truncated for AI payload security)
        role = schema.role or None
        topic = schema.topic or None

        # --- Validate required inputs ---
        category_lookup = {c.lower().strip(): c for c in AI_INTERVIEW_CATEGORIES}
        normalized_cat = category.lower().strip() if category else ""
        if normalized_cat not in category_lookup:
            logging.warning(
                "Invalid interview category received: %r (normalized: %r). Allowed: %s",
                category, normalized_cat, AI_INTERVIEW_CATEGORIES
            )
            return jsonify({
                'success': False,
                'error': f'Invalid category. Choose from: {", ".join(AI_INTERVIEW_CATEGORIES)}'
            }), 400
        category = category_lookup[normalized_cat]

        if level not in ['beginner', 'intermediate', 'advanced']:
            return jsonify({
                'success': False,
                'error': 'Level must be beginner, intermediate, or advanced'
            }), 400

        # --- Check Daily Usage Limit ---
        if mongo_db is not None:
            user_id = session.get('user_id')
            allowed, _new_count = _increment_daily_counter(
                user_id,
                'interview_gen_count',
                'last_interview_gen_at'
            )
            if not allowed:
                return jsonify({
                    'success': False,
                    'error': 'Daily question generation limit reached (5 per day). Please come back tomorrow!'
                }), 403

        # --- Generate questions (Gemini -> Groq -> static bank) ---
        questions, source = generate_questions(
            category=category,
            level=level,
            count=count,
            role=role,
            topic=topic
        )

        return jsonify({
            'success': True,
            'data': questions,
            'source': source,
            'count': len(questions)
        }), 200

    except Exception as e:
        logging.exception("AI interview question generation error")
        return jsonify({'success': False, 'error': 'Could not generate interview questions'}), 500


@interview_bp.route('/api/interview/limits', methods=['GET'])
@login_required
def get_interview_limits():
    """Get all interview-related daily usage limits and current counts"""
    try:
        limits = {
            'mock': {'limit': 5, 'count': 0},
            'gen': {'limit': 5, 'count': 0}
        }
        
        if mongo_db is not None:
            user_id = session.get('user_id')
            user = mongo_db.users.find_one({'_id': ObjectId(user_id)})
            if user:
                current_date_str = datetime.now(timezone.utc).date().isoformat()
                
                # Mock Interviews
                mock_count = user.get('mock_interview_count', 0)
                mock_date = user.get('last_mock_interview_at')
                if mock_date != current_date_str:
                    mock_count = 0
                limits['mock']['count'] = mock_count
                
                # Question Generations
                gen_count = user.get('interview_gen_count', 0)
                gen_date = user.get('last_interview_gen_at')
                if gen_date != current_date_str:
                    gen_count = 0
                limits['gen']['count'] = gen_count
            
        return jsonify({
            'success': True,
            'limits': limits
        }), 200
    except Exception as e:
        logging.exception("Interview limits check error")
        return jsonify({'success': False, 'error': 'Could not check limits'}), 500


@interview_bp.route('/api/mock-interview/start', methods=['POST'])
@login_required
@csrf_protect
def start_mock_interview():
    """Explicitly start a mock interview and increment the daily count"""
    try:
        if mongo_db is None:
            return jsonify({'success': True}), 200

        user_id = session.get('user_id')
        allowed, new_count = _increment_daily_counter(
            user_id,
            'mock_interview_count',
            'last_mock_interview_at'
        )
        if not allowed:
            return jsonify({
                'success': False, 
                'error': 'Daily limit reached (5 per day). Please come back tomorrow!'
            }), 403

        session['mock_interview_active_date'] = _today_str()

        return jsonify({'success': True, 'new_count': new_count}), 200
    except Exception as e:
        logging.exception("Start mock interview error")
        return jsonify({'success': False, 'error': 'Could not start interview'}), 500


@interview_bp.route('/api/mock-interview', methods=['POST'])
@login_required
@limiter.limit("20 per minute")
@csrf_protect
def mock_interview_chat():
    """
    Handle an interactive mock interview turn.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        try:
            schema = MockInterviewRequestSchema(**data)
        except ValidationError as e:
            errors = _validation_error_summary(e)
            logging.warning("Mock interview validation failed: %s", errors)
            msg = errors[0]['message']
            field = errors[0]['field']
            return jsonify({'success': False, 'error': f'{field}: {msg}'}), 400

        user_id = session.get('user_id')
        category = schema.category
        level = schema.level

        # --- Validate and normalize category ---
        category_lookup = {c.lower().strip(): c for c in AI_INTERVIEW_CATEGORIES}
        normalized_cat = category.lower().strip() if category else ""
        if normalized_cat not in category_lookup:
            logging.warning(
                "Invalid mock interview category received: %r (normalized: %r). Allowed: %s",
                category, normalized_cat, AI_INTERVIEW_CATEGORIES
            )
            return jsonify({
                'success': False,
                'error': f'Invalid category. Choose from: {", ".join(AI_INTERVIEW_CATEGORIES)}'
            }), 400
        category = category_lookup[normalized_cat]

        message = schema.message
        history = schema.history

        # --- Check Daily Usage Limit ---
        if mongo_db is not None:
            user = mongo_db.users.find_one({'_id': ObjectId(user_id)})
            count = user.get('mock_interview_count', 0)
            last_date_str = user.get('last_mock_interview_at')
            current_date_str = _today_str()
            
            if last_date_str != current_date_str:
                # If date changed, count should be reset, but we don't increment here anymore
                # The start endpoint handles incrementing.
                count = 0

            if count <= 0 or session.get('mock_interview_active_date') != current_date_str:
                return jsonify({'success': False, 'error': 'Please start a mock interview first.'}), 403

            if count > DAILY_INTERVIEW_LIMIT:
                return jsonify({'success': False, 'error': 'Daily limit reached.'}), 403

        # --- Count user answers (include current message) ---
        from services.interview_ai import (
            conduct_mock_interview,
            count_user_answers_with_message,
            build_history_with_message,
            generate_mock_interview_report,
        )

        full_history = build_history_with_message(history, message)
        user_answer_count = count_user_answers_with_message(history, message)

        if user_answer_count >= MAX_MOCK_QUESTIONS:
            report = generate_mock_interview_report(category, level, full_history)
            if not report:
                report = {
                    "overall_score": 75,
                    "detailed_evaluation": "Thank you for completing the mock interview.",
                    "good_parts": ["Participated in the interview."],
                    "bad_parts": [],
                    "improvement_tips": ["Continue practicing interviews."]
                }

            return jsonify({
                'success': True,
                'reply': report,
                'isComplete': True,
                'answersCompleted': user_answer_count,
                'maxAnswers': MAX_MOCK_QUESTIONS
            }), 200

        reply = conduct_mock_interview(
            category,
            level,
            message,
            history,
            answers_completed=user_answer_count,
            max_answers=MAX_MOCK_QUESTIONS
        )

        # Check if reply contains a question
        is_question = '?' in reply

        return jsonify({
            'success': True,
            'reply': reply,
            'isQuestion': is_question,
            'isComplete': False,
            'answersCompleted': user_answer_count,
            'maxAnswers': MAX_MOCK_QUESTIONS
        }), 200


    except Exception as e:
        logging.exception("Mock interview chat error")
        return jsonify({'success': False, 'error': 'Could not process mock interview message'}), 500


@interview_bp.route('/api/mock-interview/report', methods=['POST'])
@login_required
@csrf_protect
def mock_interview_report():
    """
    Generate an AI performance feedback report for the completed mock interview session.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        try:
            schema = MockInterviewReportRequestSchema(**data)
        except ValidationError as e:
            errors = _validation_error_summary(e)
            msg = errors[0]['message']
            field = errors[0]['field']
            return jsonify({'success': False, 'error': f'{field}: {msg}'}), 400

        category = schema.category
        level = schema.level
        history = schema.history

        # Validate/normalize category
        category_lookup = {c.lower().strip(): c for c in AI_INTERVIEW_CATEGORIES}
        normalized_cat = category.lower().strip() if category else ""
        if normalized_cat not in category_lookup:
            return jsonify({
                'success': False,
                'error': f'Invalid category. Choose from: {", ".join(AI_INTERVIEW_CATEGORIES)}'
            }), 400
        category = category_lookup[normalized_cat]

        from services.interview_ai import generate_mock_interview_report
        report = generate_mock_interview_report(category, level, history)

        if not report:
            return jsonify({'success': False, 'error': 'Could not generate report'}), 500

        return jsonify({
            'success': True,
            'report': report
        }), 200

    except Exception as e:
        logging.exception("Mock interview report generation error")
        return jsonify({'success': False, 'error': 'Could not generate mock interview report'}), 500
