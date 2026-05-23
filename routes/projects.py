"""
Projects routes — community projects CRUD with MongoDB Atlas.
"""

import logging
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request, session
from pydantic import ValidationError

from database import mongo_db
from schemas import ProjectSchema
from utils import csrf_protect, login_required

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/api/projects', methods=['GET'])
def get_all_projects():
    """Get all community projects from MongoDB"""
    try:
        if mongo_db is None:
            return jsonify({'success': False, 'error': 'Database not available'}), 503

        try:
            page = max(1, int(request.args.get('page', 1)))
            limit = min(100, max(1, int(request.args.get('limit', 50))))
        except (TypeError, ValueError):
            page = 1
            limit = 50

        skip = (page - 1) * limit
        projects = list(mongo_db.projects.find().sort('created_at', -1).skip(skip).limit(limit))
        for p in projects:
            p['_id'] = str(p['_id'])
            
        return jsonify({
            'success': True, 
            'data': projects if projects else [],
            'page': page,
            'limit': limit
        }), 200

    except Exception as e:
        logging.exception("Projects fetch error")
        return jsonify({'success': False, 'error': 'Could not load projects'}), 500


@projects_bp.route('/api/projects', methods=['POST'])
@login_required
@csrf_protect
def create_project():
    """Upload a new project to MongoDB Atlas"""
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        if mongo_db is None:
            return jsonify({'success': False, 'error': 'Database not available'}), 503

        try:
            schema = ProjectSchema(**data)
        except ValidationError as e:
            msg = e.errors()[0]['msg']
            field = e.errors()[0]['loc'][0] if e.errors()[0].get('loc') else 'Field'
            return jsonify({'success': False, 'error': f'{field}: {msg}'}), 400

        username = session.get('username', '')

        project_data = {
            'username': username,
            'title': schema.title,
            'link': schema.link,
            'description': schema.description,
            'created_at': datetime.now(timezone.utc).isoformat()
        }

        result = mongo_db.projects.insert_one(project_data)
        
        return jsonify({
            'success': True,
            'message': 'Project uploaded successfully!',
            'project_id': str(result.inserted_id)
        }), 201

    except Exception as e:
        logging.exception("Project creation error")
        return jsonify({'success': False, 'error': 'Could not upload project due to an internal error'}), 500


@projects_bp.route('/api/user/projects', methods=['GET'])
@login_required
def get_user_projects():
    """Get logged-in user's projects from MongoDB"""
    try:
        if mongo_db is None:
            return jsonify({'success': False, 'error': 'Database not available'}), 503

        username = session.get('username')
        projects = list(mongo_db.projects.find({'username': username}).sort('created_at', -1).limit(100))
        
        for p in projects:
            p['_id'] = str(p['_id'])
            
        return jsonify({
            'success': True, 
            'data': projects
        }), 200

    except Exception as e:
        logging.exception("User projects fetch error")
        return jsonify({'success': False, 'error': 'Could not load your projects'}), 500
