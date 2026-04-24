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

# --- SECRET KEY (REQUIRED) ---
# NOTE: For Vercel/Serverless, you MUST set SECRET_KEY in environment variables.
# If missing, we use a stable fallback to prevent the "Login Loop" issue.
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    # Stable fallback to prevent login loops on Vercel restarts
    SECRET_KEY = "futuremap-stable-fallback-secret-2026"
    if FLASK_ENV == 'production':
        logging.critical("!!! SECURITY WARNING: SECRET_KEY is not set in production. Using fallback. !!!")

# --- SESSION SECURITY ---
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = (FLASK_ENV == 'production')
SESSION_COOKIE_SAMESITE = 'Lax'  # More compatible than 'Strict' for some browser/redirect scenarios
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
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
