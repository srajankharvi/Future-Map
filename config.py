"""
Application configuration, environment variables, secrets, and logging setup.
"""

import os
import re
import logging
import secrets as secrets_module
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# --- FLASK ENVIRONMENT ---
FLASK_ENV = os.getenv('FLASK_ENV', 'development')

# --- SECRET KEY (REQUIRED — no fallback in production) ---
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY or len(SECRET_KEY) < 10:
    if FLASK_ENV == 'production':
        raise ValueError(
            "SECRET_KEY is missing or too short in .env. "
            "Set a strong key: SECRET_KEY=your-secret-here (min 10 chars)"
        )
    else:
        SECRET_KEY = secrets_module.token_urlsafe(32)
        logging.warning("No valid SECRET_KEY found; using temporary development secret (not for production)")

# --- SESSION SECURITY ---
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = FLASK_ENV == 'production'
SESSION_COOKIE_SAMESITE = 'Strict'
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

# --- INPUT VALIDATION ---
USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_]{3,30}$')
EMAIL_REGEX = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
PASSWORD_MIN = 6
PASSWORD_MAX = 128  # Prevent DoS via extremely long passwords

# --- STATIC FILE SERVING ---
ALLOWED_EXTENSIONS = {'html', 'css', 'js', 'png', 'jpg', 'jpeg', 'gif', 'svg', 'ico', 'woff', 'woff2', 'ttf'}

# --- AI API KEYS ---
# Primary: Google Gemini (best quality)
# Fallback: Groq (fast inference with open-source LLMs)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')

# --- LOGGING ---
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
