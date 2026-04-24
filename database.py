"""
Database connections and helpers for SQLite and MongoDB.
"""

import os
import sqlite3
import logging
from pymongo import MongoClient

# --- SQLite ---
# Vercel serverless has a read-only filesystem; use /tmp for SQLite
IS_VERCEL = os.getenv('VERCEL', False)
if IS_VERCEL:
    DATABASE = '/tmp/futuremap.db'
else:
    DATABASE = 'futuremap.db'


def init_db():
    """Create users, profiles, and projects tables if they don't exist."""
    try:
        conn = sqlite3.connect(DATABASE, timeout=10)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                full_name TEXT,
                bio TEXT,
                birthday TEXT,
                status TEXT,
                avatar_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                link TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                synced_to_mongodb INTEGER DEFAULT 0
            )
        ''')

        conn.commit()
        conn.close()
        print("[OK] SQLite database initialized successfully!")
    except Exception as e:
        logging.error(f"SQLite init failed (expected on serverless): {e}")


def get_db():
    """Get database connection with row factory."""
    conn = sqlite3.connect(DATABASE, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# --- MongoDB ---
MONGO_URI = os.getenv('MONGODB_URL') or os.getenv('MONGODB_URI')
DB_NAME = os.getenv('DATABASE_NAME', 'future_map')

mongo_db = None

if not MONGO_URI:
    logging.error("MongoDB disabled (no URI provided). Set MONGODB_URL or MONGODB_URI in environment or .env")
else:
    try:
        mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        mongo_client.server_info()  # Test connection
        mongo_db = mongo_client[DB_NAME]
        logging.info("MongoDB connected successfully")
    except Exception as e:
        logging.error(f"MongoDB connection failed: {type(e).__name__}: {str(e)}")
        logging.error("Check: 1) Internet connectivity, 2) MongoDB Atlas IP whitelist, 3) Credentials in .env")
        mongo_db = None
