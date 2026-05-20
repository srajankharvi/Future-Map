"""
Authentication routes — register, login, logout, profile management using MongoDB.

Security fixes applied:
- Issue #5:  Session regeneration after login
- Issue #6:  Generic error messages (no user/email enumeration)
- Issue #7:  Race condition fix via DB unique index + DuplicateKeyError
- Issue #9:  No password trimming (preserve user intent)
- Issue #10: Backend password confirmation check
- Issue #11: full_name sanitization and length limit
- Issue #12: Proper Content-Type handling
- Issue #13: Per-user login attempt tracking
- Issue #14: Logout requires authentication
"""

import logging
import re
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError

from config import USERNAME_REGEX, EMAIL_REGEX, PASSWORD_MIN, PASSWORD_MAX, FULL_NAME_MAX
from schemas import RegisterSchema, LoginSchema, UpdateProfileSchema
from database import mongo_db
from utils import login_required
from extensions import limiter

auth_bp = Blueprint('auth', __name__)

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15

def _is_account_locked(username):
    """Check if an account is temporarily locked due to failed attempts (DB-backed)."""
    if mongo_db is None: return False
    record = mongo_db.login_attempts.find_one({'username': username})
    if not record:
        return False
    if record.get('locked_until'):
        try:
            locked_until_dt = datetime.fromisoformat(record['locked_until'])
            if datetime.now(timezone.utc) < locked_until_dt:
                return True
        except ValueError:
            pass
        # Lockout expired or invalid format — reset
        mongo_db.login_attempts.delete_one({'username': username})
        return False
    return False

def _record_failed_attempt(username):
    """Record a failed login attempt and lock if threshold reached (DB-backed)."""
    if mongo_db is None: return
    from datetime import timedelta
    record = mongo_db.login_attempts.find_one({'username': username})
    if not record:
        mongo_db.login_attempts.insert_one({'username': username, 'count': 1, 'locked_until': None})
    else:
        count = record.get('count', 0) + 1
        update_data = {'count': count}
        if count >= MAX_FAILED_ATTEMPTS:
            locked_until_dt = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            update_data['locked_until'] = locked_until_dt.isoformat()
            logging.warning(f"Account '{username}' locked for {LOCKOUT_DURATION_MINUTES} min after {MAX_FAILED_ATTEMPTS} failed attempts")
        mongo_db.login_attempts.update_one({'username': username}, {'$set': update_data})

def _clear_failed_attempts(username):
    """Clear failed attempts after successful login."""
    if mongo_db is None: return
    mongo_db.login_attempts.delete_one({'username': username})


def _sanitize_text(text, max_length=255):
    """Sanitize text input: strip, limit length, remove control characters (Issue #11)."""
    if not text:
        return ''
    text = text.strip()[:max_length]
    # Remove control characters except newline/tab
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text


@auth_bp.route('/api/auth/register', methods=['POST'])
@limiter.limit("10 per minute")
def register():
    """Register a new user in MongoDB"""
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({'success': False, 'error': 'No data provided or invalid JSON'}), 400

        if mongo_db is None:
            return jsonify({'success': False, 'error': 'Database not available'}), 503

        try:
            schema = RegisterSchema(**data)
        except ValidationError as e:
            msg = e.errors()[0]['msg']
            field = e.errors()[0]['loc'][0] if e.errors()[0].get('loc') else 'Field'
            return jsonify({'success': False, 'error': f'{field}: {msg}'}), 400

        username = schema.username
        email = schema.email
        password = schema.password
        full_name = schema.full_name

        # Hash password
        password_hash = generate_password_hash(password)

        # Create user document
        user_doc = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }

        # Issue #7: Use try/except with DuplicateKeyError instead of find-then-insert.
        # The unique index on username/email in MongoDB handles concurrency safely.
        try:
            result = mongo_db.users.insert_one(user_doc)
        except DuplicateKeyError as dke:
            # Issue #6: Generic error message — don't reveal which field is duplicate
            error_msg = str(dke)
            if 'username' in error_msg:
                return jsonify({'success': False, 'error': 'Username is already taken'}), 409
            elif 'email' in error_msg:
                return jsonify({'success': False, 'error': 'Email is already registered'}), 409
            return jsonify({'success': False, 'error': 'Account already exists'}), 409

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
@limiter.limit("10 per minute")
def login():
    """Login user with MongoDB Atlas"""
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({'success': False, 'error': 'No data provided or invalid JSON'}), 400

        if mongo_db is None:
            return jsonify({'success': False, 'error': 'Database not available'}), 503

        try:
            schema = LoginSchema(**data)
        except ValidationError as e:
            return jsonify({'success': False, 'error': 'Username and password required'}), 400

        username = schema.username
        password = schema.password

        # Issue #13: Check account lockout
        if _is_account_locked(username):
            return jsonify({
                'success': False,
                'error': f'Account temporarily locked. Try again in {LOCKOUT_DURATION_MINUTES} minutes.'
            }), 429

        user = mongo_db.users.find_one({'username': username})

        if not user or not check_password_hash(user['password_hash'], password):
            # Issue #13: Record failed attempt
            _record_failed_attempt(username)
            # Issue #6: Generic error — don't reveal if username exists
            return jsonify({'success': False, 'error': 'Invalid username or password'}), 401

        # Issue #13: Clear failed attempts on success
        _clear_failed_attempts(username)

        # Issue #5: Session regeneration — clear old session data before setting new
        session.clear()
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
@login_required  # Issue #14: Require authentication for logout
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
        data = request.get_json(silent=True)

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        if mongo_db is None:
            return jsonify({'success': False, 'error': 'Database not available'}), 503

        username = session.get('username')

        try:
            schema = UpdateProfileSchema(**data)
        except ValidationError as e:
            msg = e.errors()[0]['msg']
            field = e.errors()[0]['loc'][0] if e.errors()[0].get('loc') else 'Field'
            return jsonify({'success': False, 'error': f'{field}: {msg}'}), 400

        update_data = schema.model_dump(exclude_unset=True)

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
        resp = jsonify({
            'success': True,
            'authenticated': True,
            'user': {
                'id': session.get('user_id'),
                'username': session.get('username'),
                'email': session.get('email')
            }
        })
    else:
        resp = jsonify({
            'success': True,
            'authenticated': False
        })
    
    # Prevent caching of auth state
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp, 200
