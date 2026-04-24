"""
Authentication routes — register, login, logout, profile management.
"""

import sqlite3
import logging
from flask import Blueprint, jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash

from config import USERNAME_REGEX, EMAIL_REGEX, PASSWORD_MIN, PASSWORD_MAX
from database import get_db
from utils import login_required
from extensions import limiter

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/auth/register', methods=['POST'])
@limiter.limit("10 per minute")
def register():
    """Register a new user"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        full_name = data.get('full_name', '').strip()

        # Validation
        if not username or not USERNAME_REGEX.match(username):
            return jsonify({
                'success': False,
                'error': 'Username must be 3-30 characters (letters, numbers, underscore only)'
            }), 400

        if not email or not EMAIL_REGEX.match(email):
            return jsonify({'success': False, 'error': 'Invalid email format'}), 400

        if not password or len(password) < PASSWORD_MIN:
            return jsonify({'success': False, 'error': f'Password must be at least {PASSWORD_MIN} characters'}), 400

        if len(password) > PASSWORD_MAX:
            return jsonify({'success': False, 'error': f'Password must be at most {PASSWORD_MAX} characters'}), 400

        # Hash password
        password_hash = generate_password_hash(password)

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            user_id = cursor.lastrowid

            cursor.execute(
                'INSERT INTO user_profiles (user_id, full_name) VALUES (?, ?)',
                (user_id, full_name)
            )

            conn.commit()

            return jsonify({
                'success': True,
                'message': 'User registered successfully',
                'user': {
                    'id': user_id,
                    'username': username
                }
            }), 201

        except sqlite3.IntegrityError as e:
            conn.rollback()
            error_msg = str(e).lower()
            if 'username' in error_msg:
                return jsonify({'success': False, 'error': 'Username already exists'}), 409
            else:
                return jsonify({'success': False, 'error': 'Email already exists'}), 409
        finally:
            conn.close()

    except Exception as e:
        logging.exception("Registration error")
        return jsonify({'success': False, 'error': 'Registration failed. Please try again.'}), 500


@auth_bp.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """Login user — rate limited to 5 requests/minute"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'}), 400

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, password_hash FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({'success': False, 'error': 'Invalid username or password'}), 401

        # Create session
        session.permanent = True
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['email'] = user['email']

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }
        }), 200

    except Exception as e:
        logging.exception("Login error")
        return jsonify({'success': False, 'error': 'Login failed. Please try again.'}), 500


@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user — destroy session completely"""
    try:
        session.clear()
        resp = jsonify({'success': True, 'message': 'Logout successful'})
        return resp, 200
    except Exception as e:
        logging.exception("Logout error")
        return jsonify({'success': False, 'error': 'Logout failed'}), 500


@auth_bp.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current logged-in user"""
    try:
        user_id = session.get('user_id')

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.id, u.username, u.email, u.created_at,
                   p.full_name, p.bio, p.avatar_url, p.birthday, p.status
            FROM users u
            LEFT JOIN user_profiles p ON u.id = p.user_id
            WHERE u.id = ?
        ''', (user_id,))

        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name'],
                'bio': user['bio'],
                'avatar_url': user['avatar_url'],
                'birthday': user['birthday'],
                'status': user['status'],
                'created_at': user['created_at']
            }
        }), 200

    except Exception as e:
        logging.exception("Get current user error")
        return jsonify({'success': False, 'error': 'Could not fetch user data'}), 500


@auth_bp.route('/api/auth/update-profile', methods=['PUT'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        user_id = session.get('user_id')

        # Whitelist allowed fields
        allowed_fields = ['full_name', 'bio', 'avatar_url', 'birthday', 'status']

        conn = get_db()
        cursor = conn.cursor()

        updates = []
        values = []
        for field in allowed_fields:
            if field in data:
                updates.append(f'{field} = ?')
                values.append(data[field])

        if updates:
            values.append(user_id)
            cursor.execute(
                f'UPDATE user_profiles SET {", ".join(updates)} WHERE user_id = ?',
                values
            )
            conn.commit()

        conn.close()

        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        }), 200

    except Exception as e:
        logging.exception("Profile update error")
        return jsonify({'success': False, 'error': 'Could not update profile'}), 500


@auth_bp.route('/api/check-auth', methods=['GET'])
def check_auth():
    """Check if user is currently authenticated"""
    if 'user_id' in session:
        return jsonify({
            'success': True,
            'authenticated': True,
            'user': {
                'id': session.get('user_id'),
                'username': session.get('username'),
                'email': session.get('email')
            }
        }), 200
    return jsonify({
        'success': True,
        'authenticated': False
    }), 200
