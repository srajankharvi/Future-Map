"""
Authentication routes — register, login, logout, profile management using MongoDB.
"""

import logging
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

from config import USERNAME_REGEX, EMAIL_REGEX, PASSWORD_MIN, PASSWORD_MAX
from database import mongo_db
from utils import login_required
from extensions import limiter

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/register', methods=['POST'])
@limiter.limit("10 per minute")
def register():
    """Register a new user in MongoDB"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        if mongo_db is None:
            return jsonify({'success': False, 'error': 'Database not available'}), 503

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

        # Check if user already exists
        if mongo_db.users.find_one({'$or': [{'username': username}, {'email': email}]}):
            existing_user = mongo_db.users.find_one({'username': username})
            if existing_user:
                return jsonify({'success': False, 'error': 'Username already exists'}), 409
            return jsonify({'success': False, 'error': 'Email already exists'}), 409

        # Hash password
        password_hash = generate_password_hash(password)

        # Create user
        user_doc = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        result = mongo_db.users.insert_one(user_doc)
        user_id = str(result.inserted_id)

        # Create profile
        mongo_db.user_profiles.insert_one({
            'user_id': user_id,
            'username': username,
            'full_name': full_name,
            'bio': '',
            'birthday': '',
            'status': 'Online',
            'avatar_url': '',
            'created_at': datetime.now(timezone.utc).isoformat()
        })

        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': {
                'id': user_id,
                'username': username
            }
        }), 201

    except Exception as e:
        logging.exception("Registration error")
        return jsonify({'success': False, 'error': 'Registration failed. Please try again.'}), 500


@auth_bp.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """Login user with MongoDB Atlas"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        if mongo_db is None:
            return jsonify({'success': False, 'error': 'Database not available'}), 503

        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'}), 400

        user = mongo_db.users.find_one({'username': username})

        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({'success': False, 'error': 'Invalid username or password'}), 401

        # Create session
        session.permanent = True
        session['user_id'] = str(user['_id'])
        session['username'] = user['username']
        session['email'] = user['email']

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': str(user['_id']),
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
        return jsonify({'success': True, 'message': 'Logout successful'}), 200
    except Exception as e:
        logging.exception("Logout error")
        return jsonify({'success': False, 'error': 'Logout failed'}), 500


@auth_bp.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current logged-in user details from MongoDB"""
    try:
        user_id = session.get('user_id')
        username = session.get('username')

        if mongo_db is None:
            return jsonify({'success': False, 'error': 'Database not available'}), 503

        user = mongo_db.users.find_one({'_id': ObjectId(user_id)}, {'password_hash': 0})
        profile = mongo_db.user_profiles.find_one({'username': username})

        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        user_data = {
            'id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'created_at': user.get('created_at', '')
        }

        if profile:
            user_data.update({
                'full_name': profile.get('full_name', ''),
                'bio': profile.get('bio', ''),
                'avatar_url': profile.get('avatar_url', ''),
                'birthday': profile.get('birthday', ''),
                'status': profile.get('status', '')
            })

        return jsonify({
            'success': True,
            'user': user_data
        }), 200

    except Exception as e:
        logging.exception("Get current user error")
        return jsonify({'success': False, 'error': 'Could not fetch user data'}), 500


@auth_bp.route('/api/auth/update-profile', methods=['PUT'])
@login_required
def update_profile():
    """Update user profile in MongoDB"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        if mongo_db is None:
            return jsonify({'success': False, 'error': 'Database not available'}), 503

        username = session.get('username')

        # Whitelist allowed fields
        allowed_fields = ['full_name', 'bio', 'avatar_url', 'birthday', 'status']
        update_data = {field: data[field] for field in allowed_fields if field in data}

        if update_data:
            mongo_db.user_profiles.update_one(
                {'username': username},
                {'$set': update_data},
                upsert=True
            )

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
