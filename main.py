"""
Future Map — Entry Point
Creates the Flask app, applies config, extensions, blueprints, and error handlers.
"""

from flask import Flask
from flask_cors import CORS

from config import (
    SECRET_KEY,
    SESSION_COOKIE_HTTPONLY,
    SESSION_COOKIE_SECURE,
    SESSION_COOKIE_SAMESITE,
    PERMANENT_SESSION_LIFETIME,
)
from extensions import limiter
from database import init_db, DATABASE, DB_NAME
from routes import register_blueprints
from errors import register_error_handlers


def create_app():
    """Application factory."""
    app = Flask(__name__, static_folder='frontend', static_url_path='')

    # --- Core config ---
    app.secret_key = SECRET_KEY
    app.config['SESSION_COOKIE_HTTPONLY'] = SESSION_COOKIE_HTTPONLY
    app.config['SESSION_COOKIE_SECURE'] = SESSION_COOKIE_SECURE
    app.config['SESSION_COOKIE_SAMESITE'] = SESSION_COOKIE_SAMESITE
    app.config['PERMANENT_SESSION_LIFETIME'] = PERMANENT_SESSION_LIFETIME

    # --- Extensions ---
    CORS(app, supports_credentials=True)
    limiter.init_app(app)

    # --- Blueprints ---
    register_blueprints(app)

    # --- Error handlers ---
    register_error_handlers(app)

    # --- Database init ---
    init_db()

    return app


# --- Main ---
app = create_app()

if __name__ == '__main__':
    print("Starting Future Map Web Application...")
    print(f"SQLite Database: {DATABASE}")
    print(f"MongoDB: {DB_NAME}")
    print("Open http://127.0.0.1:5000")

    app.run(debug=True, use_reloader=False)

