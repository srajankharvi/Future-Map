"""
Static file serving and page routes.
"""

from flask import Blueprint, jsonify, send_from_directory, session

from config import ALLOWED_EXTENSIONS

static_bp = Blueprint('static_pages', __name__)


@static_bp.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files with path traversal protection"""
    # Block path traversal
    if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
        return jsonify({'error': 'Access denied'}), 403

    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({'error': 'File type not allowed'}), 403

    return send_from_directory('frontend', filename)


@static_bp.route('/')
def serve_index():
    """Root route — redirect to login if not authenticated"""
    if 'user_id' not in session:
        return send_from_directory('frontend', 'login.html')
    return send_from_directory('frontend', 'index.html')

