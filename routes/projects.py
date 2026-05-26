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
from bson.objectid import ObjectId
from flask import current_app

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
        user_id = session.get('user_id')

        project_data = {
            'username': username,
            'user_id': user_id,
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


@projects_bp.route('/api/projects/<project_id>', methods=['DELETE'])
@login_required
@csrf_protect
def delete_project(project_id):
    """Delete a project by id. Only the owner may delete their project."""
    try:
        if mongo_db is None:
            logging.warning('Delete attempted but DB not available')
            return jsonify({'success': False, 'message': 'Database not available'}), 503

        # Validate ObjectId
        if not project_id or not ObjectId.is_valid(project_id):
            logging.info('Delete attempted with invalid ObjectId: %s', project_id)
            return jsonify({'success': False, 'message': 'Invalid project id'}), 400

        pid = ObjectId(project_id)

        # Ensure project exists
        project = mongo_db.projects.find_one({'_id': pid})
        if not project:
            logging.info('Project not found for id: %s', project_id)
            return jsonify({'success': False, 'message': 'Project not found'}), 404

        # Verify ownership: prefer user_id, fall back to case-insensitive username match
        username = session.get('username')
        user_id = session.get('user_id')

        project_username = project.get('username')
        project_user_id = project.get('user_id')

        authorized_by_id = False
        authorized_by_username = False

        if user_id and project_user_id and str(user_id) == str(project_user_id):
            authorized_by_id = True
        elif project_username and username and str(project_username).lower() == str(username).lower():
            authorized_by_username = True

        if not (authorized_by_id or authorized_by_username):
            logging.warning('Unauthorized delete attempt. session.user_id=%s session.username=%s project.user_id=%s project.username=%s project_id=%s', user_id, username, project_user_id, project_username, project_id)
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403

        # Perform deletion using the strongest available check
        if authorized_by_id:
            result = mongo_db.projects.delete_one({'_id': pid, 'user_id': user_id})
        else:
            # Use the stored project username to avoid case issues
            result = mongo_db.projects.delete_one({'_id': pid, 'username': project_username})
        logging.info('Delete result for %s: deleted_count=%s', project_id, getattr(result, 'deleted_count', None))
        if result.deleted_count == 0:
            return jsonify({'success': False, 'message': 'Project not found or already deleted'}), 404

        resp = {'success': True, 'message': 'Project deleted successfully'}
        # Attach helpful debug info in non-production for troubleshooting
        if current_app and current_app.debug:
            resp['debug'] = {
                'project_id': project_id,
                'deleted_count': result.deleted_count,
                'session_username': username,
                'project_username': project.get('username')
            }

        return jsonify(resp), 200

    except Exception as e:
        logging.exception('Project deletion error')
        return jsonify({'success': False, 'message': 'Internal server error'}), 500
