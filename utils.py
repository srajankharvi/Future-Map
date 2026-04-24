"""
Shared utility helpers used across routes and services.
"""

import logging
from datetime import datetime, timezone
from functools import wraps
from flask import jsonify, session


def login_required(f):
    """Decorator to protect routes that require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Login required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def current_time():
    """Get current UTC time in ISO format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _extract_data_from_view_result(view_result, key='data'):
    """
    Safely extract a JSON 'key' from a Flask view function's return value.
    Handles cases where a view returns a `Response` or a `(Response, status)` tuple,
    or when a helper function accidentally returned a dict/list. Returns an empty
    list on failure to keep callers robust.
    """
    if view_result is None:
        return []
    try:
        # If view returned (response, status)
        if isinstance(view_result, tuple) and len(view_result) >= 1:
            resp = view_result[0]
        else:
            resp = view_result

        # If it's a Flask Response-like object
        if hasattr(resp, 'get_json'):
            json_data = resp.get_json()
            if isinstance(json_data, dict):
                return json_data.get(key, [])
            if isinstance(json_data, list):
                return json_data

        # If a plain dict/list was returned
        if isinstance(resp, dict):
            return resp.get(key, [])
        if isinstance(resp, list):
            return resp

    except Exception:
        logging.exception("Failed to extract data from view result")

    return []
