"""
Recommendations route — career + course recommendations based on marks and skills.
"""

import logging
from flask import Blueprint, jsonify, request

from routes.careers import fetch_careers
from routes.courses import fetch_courses
from services.recommendations import compute_recommendations

recommendations_bp = Blueprint('recommendations', __name__)


@recommendations_bp.route('/api/recommendation', methods=['GET', 'POST'])
@recommendations_bp.route('/api/recommendations', methods=['GET', 'POST'])
def get_recommendations():
    """Generate career and course recommendations based on marks and skills"""
    try:
        if request.method == 'GET':
            return jsonify({
                'success': True,
                'message': 'Recommendation API is running. Send a POST request with marks and skills to get recommendations.',
                'example_payload': {
                    'marks': 85,
                    'skills': ['Python', 'Data Analysis']
                }
            }), 200

        data = request.get_json(silent=True)

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        marks = data.get('marks', 0)
        skills = data.get('skills', [])
        education_level = data.get('education_level', 'SSLC')

        if not skills:
            return jsonify({'success': False, 'error': 'Please select at least one skill'}), 400

        # Fetch data directly (no need to go through Flask view functions)
        all_careers = fetch_careers()
        all_courses = fetch_courses()

        # Compute recommendations
        result = compute_recommendations(marks, skills, all_careers, all_courses, education_level)

        return jsonify({
            'success': True,
            'data': result
        }), 200

    except Exception as e:
        logging.exception("Recommendation error")
        return jsonify({'success': False, 'error': 'Could not generate recommendations'}), 500
