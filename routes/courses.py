"""
Courses route — serves course data from MongoDB with fallback.
"""

import logging
from flask import Blueprint, jsonify

from database import mongo_db
from data.courses import FALLBACK_COURSES

courses_bp = Blueprint('courses', __name__)


def fetch_courses():
    """Fetch courses data (callable by other modules without going through Flask)."""
    courses = []
    if mongo_db is not None:
        courses = list(mongo_db.courses.find({}, {'_id': 0}))

    if not courses:
        courses = FALLBACK_COURSES

    return courses


@courses_bp.route('/api/courses', methods=['GET'])
def get_courses():
    """Get all courses from MongoDB"""
    try:
        courses = fetch_courses()
        return jsonify({'success': True, 'data': courses, 'count': len(courses)}), 200

    except Exception as e:
        logging.exception("Courses fetch error")
        return jsonify({'success': False, 'error': 'Could not load courses'}), 500
