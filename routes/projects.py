"""
Projects routes — community projects CRUD with MongoDB + SQLite fallback.
"""

import logging
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request, session

from database import get_db, mongo_db
from utils import login_required

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/api/projects', methods=['GET'])
def get_all_projects():
    """Get all community projects from MongoDB, or SQLite fallback"""
    try:
        if mongo_db is not None:
            # Try MongoDB first
            try:
                projects = list(mongo_db.projects.find().sort('created_at', -1))
                for p in projects:
                    p['_id'] = str(p['_id'])
                return jsonify({'success': True, 'data': projects, 'source': 'mongodb'}), 200
            except Exception as mongo_err:
                logging.warning(f"MongoDB fetch failed: {mongo_err}, falling back to SQLite")

        # SQLite fallback
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, title, description, link, created_at FROM projects ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()

        projects = []
        for row in rows:
            projects.append({
                '_id': str(row['id']),
                'username': row['username'],
                'title': row['title'],
                'description': row['description'],
                'link': row['link'],
                'created_at': row['created_at']
            })

        source = 'sqlite' if projects else 'demo'

        # Return demo projects only if no data at all
        if not projects:
            projects = [
                {
                    '_id': 'demo-1',
                    'username': 'Community',
                    'title': 'Demo: Build a Portfolio',
                    'link': 'https://example.com',
                    'description': 'Sample project to showcase skills',
                    'created_at': datetime.now(timezone.utc).isoformat()
                }
            ]

        return jsonify({'success': True, 'data': projects, 'source': source}), 200

    except Exception as e:
        logging.exception("Projects fetch error")
        return jsonify({'success': False, 'error': 'Could not load projects'}), 500


@projects_bp.route('/api/projects', methods=['POST'])
@login_required
def create_project():
    """Upload a new project to MongoDB or SQLite fallback"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        # Use session username instead of trusting client input
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

        project_id = None
        stored_in = 'sqlite'

        # Try MongoDB first
        if mongo_db is not None:
            try:
                result = mongo_db.projects.insert_one(project_data)
                project_id = str(result.inserted_id)
                stored_in = 'mongodb'
                logging.info(f"Project created in MongoDB: {project_id}")
            except Exception as mongo_err:
                logging.warning(f"MongoDB store failed: {mongo_err}, falling back to SQLite")
                stored_in = 'sqlite'

        # Store in SQLite as primary or fallback storage
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO projects (username, title, description, link, created_at, synced_to_mongodb)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, title, description, link, project_data['created_at'], 1 if stored_in == 'mongodb' else 0))
            conn.commit()
            project_id = str(cursor.lastrowid)
            logging.info(f"Project created in SQLite: {project_id}")
        finally:
            conn.close()

        return jsonify({
            'success': True,
            'message': f'Project uploaded successfully (stored in {stored_in})!',
            'project_id': project_id,
            'stored_in': stored_in
        }), 201

    except Exception as e:
        logging.exception("Project creation error")
        return jsonify({'success': False, 'error': f'Could not upload project: {str(e)}'}), 500


@projects_bp.route('/api/user/projects', methods=['GET'])
@login_required
def get_user_projects():
    """Get logged-in user's projects from MongoDB or SQLite fallback"""
    try:
        username = session.get('username')

        if mongo_db is not None:
            # Try MongoDB first
            try:
                projects = list(mongo_db.projects.find({'username': username}).sort('created_at', -1))
                for p in projects:
                    p['_id'] = str(p['_id'])
                return jsonify({'success': True, 'data': projects, 'source': 'mongodb'}), 200
            except Exception as mongo_err:
                logging.warning(f"MongoDB fetch failed: {mongo_err}, falling back to SQLite")

        # SQLite fallback
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, title, description, link, created_at FROM projects WHERE username = ? ORDER BY created_at DESC', (username,))
        rows = cursor.fetchall()
        conn.close()

        projects = []
        for row in rows:
            projects.append({
                '_id': str(row['id']),
                'username': row['username'],
                'title': row['title'],
                'description': row['description'],
                'link': row['link'],
                'created_at': row['created_at']
            })

        return jsonify({'success': True, 'data': projects, 'source': 'sqlite'}), 200

    except Exception as e:
        logging.exception("User projects fetch error")
        return jsonify({'success': False, 'error': 'Could not load your projects'}), 500
