"""
YourPath route — serves yourpath reference data from MongoDB with fallback.
"""

import logging
from flask import Blueprint, jsonify

from database import mongo_db
from data.yourpath import (
    FALLBACK_CAREER_COURSE_MAPPING,
    FALLBACK_ROADMAP_TEMPLATES,
    FALLBACK_CAREER_DETAILED_INFO,
    FALLBACK_CAREER_PROJECTS,
    FALLBACK_CAREER_RESOURCES,
)

yourpath_bp = Blueprint('yourpath', __name__)


def _fetch_yourpath_collection(collection_name, fallback):
    """Fetch a yourpath reference data collection from MongoDB with fallback."""
    if mongo_db is None:
        return fallback

    try:
        doc = mongo_db[collection_name].find_one({}, {'_id': 0})
        if doc and 'data' in doc:
            return doc['data']
    except Exception:
        pass

    return fallback


@yourpath_bp.route('/api/yourpath-data', methods=['GET'])
@yourpath_bp.route('/api/yourpath', methods=['GET'])
def get_yourpath_data():
    """Get all yourpath reference data (roadmaps, skills, projects, resources)"""
    try:
        data = {
            'careerCourseMapping': _fetch_yourpath_collection(
                'career_course_mapping', FALLBACK_CAREER_COURSE_MAPPING
            ),
            'roadmapTemplates': _fetch_yourpath_collection(
                'roadmap_templates', FALLBACK_ROADMAP_TEMPLATES
            ),
            'careerDetailedInfo': _fetch_yourpath_collection(
                'career_detailed_info', FALLBACK_CAREER_DETAILED_INFO
            ),
            'careerProjects': _fetch_yourpath_collection(
                'career_projects', FALLBACK_CAREER_PROJECTS
            ),
            'careerResources': _fetch_yourpath_collection(
                'career_resources', FALLBACK_CAREER_RESOURCES
            ),
        }

        return jsonify({'success': True, 'data': data}), 200

    except Exception as e:
        logging.exception("YourPath data fetch error")
        return jsonify({'success': False, 'error': 'Could not load yourpath data'}), 500
