"""
Interview routes — static questions + AI-powered question generation.
"""

import logging
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request, session
from bson import ObjectId

from database import mongo_db

from utils import login_required
from extensions import limiter
from data.interview import FALLBACK_INTERVIEW_QUESTIONS, AI_INTERVIEW_CATEGORIES
from services.interview_ai import generate_questions

interview_bp = Blueprint('interview', __name__)


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
def generate_interview_questions():
    """
    Generate AI-powered interview questions.

    Accepts both the original format (category + level) and the enhanced
    format (role + level + topic) for richer question generation.

    Fallback chain: Gemini → Groq → curated question bank.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        # --- Parse inputs (support both original and enhanced format) ---
        category = data.get('category', '').strip()
        level = data.get('level', '').strip().lower()
        count = data.get('count', 5)

        # --- Check Daily Usage Limit ---
        if mongo_db is not None:
            user_id = session.get('user_id')
            user = mongo_db.users.find_one({'_id': ObjectId(user_id)})
            if user:
                gen_count = user.get('interview_gen_count', 0)
                last_date_str = user.get('last_interview_gen_at')
                current_date_str = datetime.now(timezone.utc).date().isoformat()
                
                # Reset if new day
                if last_date_str != current_date_str:
                    gen_count = 0
                    mongo_db.users.update_one(
                        {'_id': ObjectId(user_id)},
                        {'$set': {'interview_gen_count': 0, 'last_interview_gen_at': current_date_str}}
                    )

                if gen_count >= 5:
                    return jsonify({
                        'success': False, 
                        'error': 'Daily question generation limit reached (5 per day). Please come back tomorrow!'
                    }), 403
                
                # Increment
                mongo_db.users.update_one(
                    {'_id': ObjectId(user_id)},
                    {
                        '$inc': {'interview_gen_count': 1},
                        '$set': {'last_interview_gen_at': current_date_str}
                    }
                )

        # Enhanced parameters (optional — used for more targeted AI prompts)
        role = data.get('role', '').strip() or None
        topic = data.get('topic', '').strip() or None


        # --- Validate required inputs ---
        if category not in AI_INTERVIEW_CATEGORIES:
            return jsonify({
                'success': False,
                'error': f'Invalid category. Choose from: {", ".join(AI_INTERVIEW_CATEGORIES)}'
            }), 400

        if level not in ['beginner', 'intermediate', 'advanced']:
            return jsonify({
                'success': False,
                'error': 'Level must be beginner, intermediate, or advanced'
            }), 400

        try:
            count = int(count)
            count = max(1, min(count, 50))
        except (ValueError, TypeError):
            count = 5

        # --- Generate questions (Gemini → Groq → static bank) ---
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


@interview_bp.route('/api/mock-interview', methods=['POST'])
@login_required
@limiter.limit("20 per minute")
def mock_interview_chat():
    """
    Handle an interactive mock interview turn.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        user_id = session.get('user_id')
        category = data.get('category', '').strip()
        level = data.get('level', 'beginner').strip().lower()
        message = data.get('message', '').strip()
        history = data.get('history', [])
        
        if not category or not message:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        # --- Check Daily Usage Limit ---
        if mongo_db is not None:
            user = mongo_db.users.find_one({'_id': ObjectId(user_id)})
            if user:
                mock_count = user.get('mock_interview_count', 0)
                last_date_str = user.get('last_mock_interview_at')
                
                # Get current date in ISO format (YYYY-MM-DD)
                current_date_str = datetime.now(timezone.utc).date().isoformat()
                
                # Reset count if it's a new day
                if last_date_str != current_date_str:
                    mock_count = 0
                    mongo_db.users.update_one(
                        {'_id': ObjectId(user_id)},
                        {'$set': {'mock_interview_count': 0, 'last_mock_interview_at': current_date_str}}
                    )

                # If starting a NEW interview (history only contains the AI greeting)
                if len(history) <= 1:
                    if mock_count >= 5:
                        return jsonify({
                            'success': False, 
                            'error': 'Daily limit reached (5 per day). Please come back tomorrow!'
                        }), 403
                    
                    # Increment count and update timestamp
                    mongo_db.users.update_one(
                        {'_id': ObjectId(user_id)},
                        {
                            '$inc': {'mock_interview_count': 1},
                            '$set': {'last_mock_interview_at': current_date_str}
                        }
                    )
                # For ongoing interviews, just check if they are already over the limit 
                elif mock_count > 5:
                     return jsonify({'success': False, 'error': 'Daily limit reached.'}), 403


        from services.interview_ai import conduct_mock_interview
        reply = conduct_mock_interview(category, level, message, history)

        # Heuristic to check if the reply contains a new question
        is_question = '?' in reply

        return jsonify({
            'success': True,
            'reply': reply,
            'isQuestion': is_question
        }), 200


    except Exception as e:
        logging.exception("Mock interview chat error")
        return jsonify({'success': False, 'error': 'Could not process mock interview message'}), 500
