"""
Projects routes — community projects CRUD with MongoDB Atlas.
"""

import logging
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request, session

from database import mongo_db
from utils import login_required

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/api/projects', methods=['GET'])
def get_all_projects():
    """Get all community projects from MongoDB"""
    try:
        if mongo_db is None:
            return jsonify({'success': False, 'error': 'Database not available'}), 503

        projects = list(mongo_db.projects.find().sort('created_at', -1))
        for p in projects:
            p['_id'] = str(p['_id'])
            
        return jsonify({
            'success': True, 
            'data': projects if projects else []
        }), 200

    except Exception as e:
        logging.exception("Projects fetch error")
        return jsonify({'success': False, 'error': 'Could not load projects'}), 500


@projects_bp.route('/api/projects', methods=['POST'])
@login_required
def create_project():
    """Upload a new project to MongoDB Atlas"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        if mongo_db is None:
            return jsonify({'success': False, 'error': 'Database not available'}), 503

        username = session.get('username', '')
        title = data.get('title', '').strip()
        link = data.get('link', '').strip()
        description = data.get('description', '').strip()

        if not title or not link or not description:
            return jsonify({'success': False, 'error': 'All fields are required'}), 400

        project_data = {
            'username': username,
            'title': title,
            'link': link,
            'description': description,
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
        return jsonify({'success': False, 'error': f'Could not upload project: {str(e)}'}), 500


@projects_bp.route('/api/user/projects', methods=['GET'])
@login_required
def get_user_projects():
    """Get logged-in user's projects from MongoDB"""
    try:
        if mongo_db is None:
            return jsonify({'success': False, 'error': 'Database not available'}), 503

        username = session.get('username')
        projects = list(mongo_db.projects.find({'username': username}).sort('created_at', -1))
        
        for p in projects:
            p['_id'] = str(p['_id'])
            
        return jsonify({
            'success': True, 
            'data': projects
        }), 200

    except Exception as e:
        logging.exception("User projects fetch error")
        return jsonify({'success': False, 'error': 'Could not load your projects'}), 500
