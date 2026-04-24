"""
Search route — search across careers and courses.
"""

import logging
from flask import Blueprint, jsonify, request

from routes.careers import fetch_careers
from routes.courses import fetch_courses

search_bp = Blueprint('search', __name__)


@search_bp.route('/api/search', methods=['GET'])
def search():
    """Search careers and courses"""
    try:
        query = request.args.get('q', '').lower()

        if not query or len(query) < 2:
            return jsonify({'success': False, 'error': 'Query must be at least 2 characters'}), 400

        all_careers = fetch_careers()
        all_courses = fetch_courses()

        matched_careers = [c for c in all_careers if query in c.get('name', '').lower() or query in c.get('description', '').lower()]
        matched_courses = [c for c in all_courses if query in c.get('name', '').lower() or query in c.get('description', '').lower()]

        return jsonify({
            'success': True,
            'data': {
                'careers': matched_careers,
                'courses': matched_courses
            },
            'total_count': len(matched_careers) + len(matched_courses)
        }), 200

    except Exception as e:
        logging.exception("Search error")
        return jsonify({'success': False, 'error': 'Search failed'}), 500
