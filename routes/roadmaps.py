"""
Roadmaps routes — save, list, get, delete user roadmaps (MongoDB).
"""

import logging
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request, session
from bson import ObjectId

from database import mongo_db
from utils import login_required

roadmaps_bp = Blueprint('roadmaps', __name__)


@roadmaps_bp.route('/api/roadmaps', methods=['POST'])
@login_required
def save_roadmap():
    """Save a generated roadmap for the current user"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        career_name = data.get('career_name', '').strip()
        course_name = data.get('course_name', '').strip()
        category = data.get('category', '').strip()
        roadmap_data = data.get('roadmap_data', {})

        if not career_name or not course_name:
            return jsonify({'success': False, 'error': 'Career and course names are required'}), 400

        if mongo_db is None:
            return jsonify({'success': False, 'error': 'Database not available'}), 503

        user_id = session.get('user_id')
        username = session.get('username', '')

        roadmap = {
            'user_id': user_id,
            'username': username,
            'career_name': career_name,
            'course_name': course_name,
            'category': category,
            'roadmap_data': roadmap_data,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }

        # Upsert: update if same user+career+course exists, else insert
        result = mongo_db.roadmaps.update_one(
            {'user_id': user_id, 'career_name': career_name, 'course_name': course_name},
            {'$set': roadmap},
            upsert=True
        )

        return jsonify({
            'success': True,
            'message': 'Roadmap saved successfully!',
            'roadmap_id': str(result.upserted_id) if result.upserted_id else 'updated'
        }), 201

    except Exception as e:
        logging.exception("Roadmap save error")
        return jsonify({'success': False, 'error': 'Could not save roadmap'}), 500


@roadmaps_bp.route('/api/roadmaps', methods=['GET'])
@login_required
def get_user_roadmaps():
    """Get all saved roadmaps for the current user"""
    try:
        if mongo_db is None:
            return jsonify({'success': True, 'data': []}), 200

        user_id = session.get('user_id')
        roadmaps = list(mongo_db.roadmaps.find(
            {'user_id': user_id},
            {'roadmap_data': 0}  # Exclude heavy data in list view
        ).sort('updated_at', -1))

        for r in roadmaps:
            r['_id'] = str(r['_id'])

        return jsonify({'success': True, 'data': roadmaps}), 200

    except Exception as e:
        logging.exception("Roadmaps fetch error")
        return jsonify({'success': False, 'error': 'Could not load roadmaps'}), 500


@roadmaps_bp.route('/api/roadmaps/<roadmap_id>', methods=['GET'])
@login_required
def get_roadmap(roadmap_id):
    """Get a specific saved roadmap with full data"""
    try:
        if mongo_db is None:
            return jsonify({'success': False, 'error': 'Database not available'}), 503

        user_id = session.get('user_id')

        try:
            oid = ObjectId(roadmap_id)
        except Exception:
            return jsonify({'success': False, 'error': 'Invalid roadmap ID'}), 400

        roadmap = mongo_db.roadmaps.find_one({'_id': oid, 'user_id': user_id})

        if not roadmap:
            return jsonify({'success': False, 'error': 'Roadmap not found'}), 404

        roadmap['_id'] = str(roadmap['_id'])
        return jsonify({'success': True, 'data': roadmap}), 200

    except Exception as e:
        logging.exception("Roadmap fetch error")
        return jsonify({'success': False, 'error': 'Could not load roadmap'}), 500


@roadmaps_bp.route('/api/roadmaps/<roadmap_id>', methods=['DELETE'])
@login_required
def delete_roadmap(roadmap_id):
    """Delete a saved roadmap"""
    try:
        if mongo_db is None:
            return jsonify({'success': False, 'error': 'Database not available'}), 503

        user_id = session.get('user_id')

        try:
            oid = ObjectId(roadmap_id)
        except Exception:
            return jsonify({'success': False, 'error': 'Invalid roadmap ID'}), 400

        result = mongo_db.roadmaps.delete_one({'_id': oid, 'user_id': user_id})

        if result.deleted_count == 0:
            return jsonify({'success': False, 'error': 'Roadmap not found'}), 404

        return jsonify({'success': True, 'message': 'Roadmap deleted successfully'}), 200

    except Exception as e:
        logging.exception("Roadmap delete error")
        return jsonify({'success': False, 'error': 'Could not delete roadmap'}), 500
