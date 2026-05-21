"""
Fallback careers data — loaded from Careers.json.
Used when MongoDB is unavailable or the careers collection is empty.
"""

import json
import os
import logging

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CAREERS_JSON = os.path.join(_PROJECT_ROOT, 'Careers.json')

try:
    with open(_CAREERS_JSON, 'r', encoding='utf-8') as f:
        FALLBACK_CAREERS = json.load(f)
    logging.info(f"Loaded {len(FALLBACK_CAREERS)} careers from Careers.json")
except Exception as e:
    logging.warning(f"Could not load Careers.json: {e}. Using empty fallback.")
    FALLBACK_CAREERS = []
