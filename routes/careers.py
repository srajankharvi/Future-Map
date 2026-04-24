"""
Careers route — serves career data from MongoDB with fallback.
"""

import logging
from flask import Blueprint, jsonify

from database import mongo_db
from data.careers import FALLBACK_CAREERS

careers_bp = Blueprint('careers', __name__)


def fetch_careers():
    """Fetch careers data (callable by other modules without going through Flask)."""
    careers = []
    if mongo_db is not None:
        careers = list(mongo_db.careers.find({}, {'_id': 0}))

    if not careers:
        careers = FALLBACK_CAREERS

    return careers


@careers_bp.route('/api/careers', methods=['GET'])
def get_careers():
    """Get all careers from MongoDB"""
    try:
        careers = fetch_careers()
        return jsonify({'success': True, 'data': careers, 'count': len(careers)}), 200

    except Exception as e:
        logging.exception("Careers fetch error")
        return jsonify({'success': False, 'error': 'Could not load careers'}), 500
