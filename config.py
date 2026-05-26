"""
Application configuration, environment variables, secrets, and logging setup.
"""

import os
import re
import logging
import secrets as secrets_module
from datetime import timedelta
from dotenv import load_dotenv

# Determine FLASK environment early so we only load .env in development.
# Avoid loading `.env` in production so the app doesn't unintentionally
# rely on a checked-in file for secrets.
FLASK_ENV = os.getenv('FLASK_ENV', 'development')

if FLASK_ENV != 'production':
    # Local development: load variables from .env (if present).
    load_dotenv()
else:
    # Production: do not load .env — rely on real environment variables.
    pass

# --- SECRET KEY (REQUIRED) ---
# NOTE: For Vercel/Serverless, you MUST set SECRET_KEY in environment variables.
# A random fallback will change on each restart, causing session invalidation.
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    if FLASK_ENV == 'production':
        raise ValueError("CRITICAL SECURITY ERROR: SECRET_KEY environment variable must be set in production!")
    # Generate a strong random key as fallback for development
    SECRET_KEY = secrets_module.token_hex(64)
    logging.warning("SECRET_KEY not set. Using random fallback for development.")

# --- CORS SECURITY ---
CORS_ORIGINS_ENV = os.getenv('CORS_ORIGINS')
if CORS_ORIGINS_ENV:
    CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS_ENV.split(',')]
else:
    CORS_ORIGINS = [
        'http://127.0.0.1:5500', 'http://localhost:5500',
        'http://127.0.0.1:5501', 'http://localhost:5501',
        'http://127.0.0.1:3000', 'http://localhost:3000',
        'http://127.0.0.1:5000', 'http://localhost:5000',
    ]


# --- SESSION SECURITY ---
SESSION_COOKIE_HTTPONLY = True
if FLASK_ENV == 'production':
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Lax'
else:
    # Development: Flask serves the frontend directly (same-origin), so
    # SameSite=Lax is correct and Secure=False is needed for plain HTTP.
    # NOTE: If using Live Server (cross-origin), access via Flask at
    # http://127.0.0.1:5000 instead to avoid cross-origin cookie issues.
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'Lax'
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

# --- INPUT VALIDATION ---
USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_]{3,30}$')
EMAIL_REGEX = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
PASSWORD_MIN = 6
PASSWORD_MAX = 128  # Prevent DoS via extremely long passwords
FULL_NAME_MAX = 100  # Issue #11: Limit full_name length

# --- STATIC FILE SERVING ---
ALLOWED_EXTENSIONS = {'html', 'css', 'js', 'png', 'jpg', 'jpeg', 'gif', 'svg', 'ico', 'woff', 'woff2', 'ttf'}

# --- AI API KEYS ---
# Primary: Google Gemini (best quality)
# Fallback: Groq (fast inference with open-source LLMs)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')

# --- LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
