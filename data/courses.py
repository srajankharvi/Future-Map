"""
Fallback courses data — loaded from courses.json.
Used when MongoDB is unavailable or the courses collection is empty.
"""

import json
import os
import logging

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_COURSES_JSON = os.path.join(_PROJECT_ROOT, 'courses.json')

try:
    with open(_COURSES_JSON, 'r', encoding='utf-8') as f:
        FALLBACK_COURSES = json.load(f)
    logging.info(f"Loaded {len(FALLBACK_COURSES)} courses from courses.json")
except Exception as e:
    logging.warning(f"Could not load courses.json: {e}. Using empty fallback.")
    FALLBACK_COURSES = []
