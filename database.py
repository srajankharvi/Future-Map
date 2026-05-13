"""
Database connection for MongoDB Atlas.
Includes unique index creation for username and email fields.
"""

import os
import logging
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure

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

        # --- Ensure unique indexes exist (Issue #8: DB-level uniqueness) ---
        # These indexes prevent duplicate usernames/emails at the database level,
        # even under concurrent request conditions (fixes race condition Issue #7).
        try:
            mongo_db.users.create_index(
                [('username', ASCENDING)],
                unique=True,
                name='unique_username'
            )
            mongo_db.users.create_index(
                [('email', ASCENDING)],
                unique=True,
                name='unique_email'
            )
            logging.info("MongoDB unique indexes ensured for users collection")
        except Exception as idx_err:
            logging.warning(f"Index creation note: {idx_err}")

    except ConnectionFailure as e:
        logging.error(f"MongoDB connection failed: {type(e).__name__}: {str(e)}")
        logging.error("Check: 1) Internet connectivity, 2) MongoDB Atlas IP whitelist, 3) Credentials in .env")
        mongo_db = None
    except Exception as e:
        logging.error(f"MongoDB connection failed: {type(e).__name__}: {str(e)}")
        logging.error("Check: 1) Internet connectivity, 2) MongoDB Atlas IP whitelist, 3) Credentials in .env")
        mongo_db = None


# For backward compatibility if any file calls init_db()
def init_db():
    pass
