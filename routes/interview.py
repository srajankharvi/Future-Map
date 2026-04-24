"""
Interview routes — static questions + AI-powered question generation.
"""

import logging
from flask import Blueprint, jsonify, request

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
