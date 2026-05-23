"""
Roadmaps routes — save, list, get, delete user roadmaps (MongoDB).
"""

import logging
import json
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request, session
from bson import ObjectId
from pydantic import ValidationError

from database import mongo_db
from schemas import RoadmapSchema
from utils import csrf_protect, login_required

roadmaps_bp = Blueprint('roadmaps', __name__)


@roadmaps_bp.route('/api/roadmaps', methods=['POST'])
@login_required
@csrf_protect
def save_roadmap():
    """Save a generated roadmap for the current user"""
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        try:
            schema = RoadmapSchema(**data)
        except ValidationError as e:
            msg = e.errors()[0]['msg']
            field = e.errors()[0]['loc'][0] if e.errors()[0].get('loc') else 'Field'
            return jsonify({'success': False, 'error': f'{field}: {msg}'}), 400

        roadmap_data_size = len(json.dumps(schema.roadmap_data, default=str))
        if roadmap_data_size > 50000:
            return jsonify({'success': False, 'error': 'Roadmap data is too large'}), 413

        if mongo_db is None:
            return jsonify({'success': False, 'error': 'Database not available'}), 503

        user_id = session.get('user_id')
        username = session.get('username', '')
        now = datetime.now(timezone.utc).isoformat()

        roadmap = {
            'user_id': user_id,
            'username': username,
            'career_name': schema.career_name,
            'course_name': schema.course_name,
            'category': schema.category,
            'roadmap_data': schema.roadmap_data,
            'updated_at': now
        }

        # Upsert: update if same user+career+course exists, else insert
        result = mongo_db.roadmaps.update_one(
            {'user_id': user_id, 'career_name': schema.career_name, 'course_name': schema.course_name},
            {'$set': roadmap, '$setOnInsert': {'created_at': now}},
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
@csrf_protect
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
