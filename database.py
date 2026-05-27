"""
Database connection for MongoDB Atlas.
Includes unique index creation for username and email fields.
"""

import os
import logging
from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from pymongo.errors import ConnectionFailure, OperationFailure

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
        indexes_to_create = [
            (mongo_db.users, [('username', ASCENDING)], {'unique': True, 'name': 'unique_username'}),
            (mongo_db.users, [('email', ASCENDING)], {'unique': True, 'name': 'unique_email'}),
            (mongo_db.user_profiles, [('username', ASCENDING)], {'unique': True, 'name': 'unique_user_profile_username'}),
            (mongo_db.login_attempts, [('username', ASCENDING)], {'unique': True, 'name': 'unique_login_attempt_username'}),
            (mongo_db.projects, [('created_at', DESCENDING)], {'name': 'projects_created_at_desc'}),
            (mongo_db.projects, [('username', ASCENDING), ('created_at', DESCENDING)], {'name': 'projects_username_created_at'}),
            (mongo_db.roadmaps, [('user_id', ASCENDING), ('updated_at', DESCENDING)], {'name': 'roadmaps_user_updated_at'}),
            (mongo_db.roadmaps, [('user_id', ASCENDING), ('career_name', ASCENDING), ('course_name', ASCENDING)], {'unique': True, 'name': 'unique_user_career_course_roadmap'}),
            (mongo_db.career_skill_progress, [('user_id', ASCENDING)], {'unique': True, 'name': 'unique_user_skill_progress'}),
            (mongo_db.careers, [('name', TEXT), ('description', TEXT), ('category', TEXT)], {'name': 'careers_text_search'}),
            (mongo_db.courses, [('name', TEXT), ('description', TEXT), ('category', TEXT)], {'name': 'courses_text_search'}),
        ]

        for collection, keys, kwargs in indexes_to_create:
            try:
                collection.create_index(keys, **kwargs)
            except OperationFailure as e:
                # 85 is IndexOptionsConflict
                if e.code == 85:
                    logging.warning(f"Index conflict for {collection.name}, dropping conflicting index.")
                    try:
                        # Drop any existing index with the same keys
                        for index_name, index_info in collection.index_information().items():
                            if index_info['key'] == keys and index_name != kwargs.get('name'):
                                collection.drop_index(index_name)
                                collection.create_index(keys, **kwargs)
                                break
                    except Exception as drop_err:
                        logging.error(f"Failed to resolve index conflict on {collection.name}: {drop_err}")
                else:
                    logging.warning(f"Index creation failed for {collection.name}: {e}")
            except Exception as e:
                logging.warning(f"Index creation failed for {collection.name}: {e}")
                
        logging.info("MongoDB indexes ensured for users, attempts, projects, roadmaps, careers, and courses")

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
