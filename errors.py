"""
Error handlers for the Flask application.
"""

import logging
from flask import jsonify, request
from werkzeug.exceptions import HTTPException
from utils import current_time


def register_error_handlers(app):
    """Register all error handlers on the app."""

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Resource not found',
            'code': 404,
            'type': 'NotFound',
            'path': request.path,
            'method': request.method,
            'timestamp': current_time()
        }), 404

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            'success': False,
            'error': 'Too many requests. Please wait before trying again.',
            'code': 429,
            'type': 'RateLimitExceeded',
            'timestamp': current_time()
        }), 429

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Handle HTTP errors (400, 401, 403, 500, etc.)
        if isinstance(e, HTTPException):
            return jsonify({
                'success': False,
                'error': e.description,
                'code': e.code,
                'type': e.__class__.__name__,
                'path': request.path,
                'method': request.method,
                'timestamp': current_time()
            }), e.code

        # Unexpected errors — don't leak internal info
        logging.exception(
            "Unhandled Exception at %s [%s]: %s",
            request.path,
            request.method,
            str(e)
        )

        return jsonify({
            'success': False,
            'error': 'An unexpected internal server error occurred',
            'code': 500,
            'type': 'InternalServerError',
            'path': request.path,
            'method': request.method,
            'timestamp': current_time()
        }), 500
