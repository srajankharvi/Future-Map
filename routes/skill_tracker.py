"""
Career Skill Roadmap Tracker — persist career choice and skill completion per user.
"""

import logging
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request, session
from pydantic import ValidationError

from database import mongo_db
from routes.careers import fetch_careers
from schemas import SkillTrackerCareerSchema, SkillTrackerToggleSchema
from services.skill_roadmap import (
    build_roadmap,
    compute_progress,
    find_career_by_name,
    flatten_roadmap_skills,
    _skill_key,
)
from utils import csrf_protect, login_required

skill_tracker_bp = Blueprint('skill_tracker', __name__)

COLLECTION = 'career_skill_progress'


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_progress_doc(user_id: str):
    if mongo_db is None:
        return None
    return mongo_db[COLLECTION].find_one({'user_id': user_id})


def _career_names_list() -> list:
    careers = fetch_careers()
    return sorted({(c.get('name') or '').strip() for c in careers if c.get('name')})


@skill_tracker_bp.route('/api/skill-tracker/careers', methods=['GET'])
@login_required
def list_career_options():
    """Career names for the account-page selector."""
    try:
        return jsonify({'success': True, 'data': _career_names_list()}), 200
    except Exception:
        logging.exception('Skill tracker careers list error')
        return jsonify({'success': False, 'error': 'Could not load careers'}), 500


@skill_tracker_bp.route('/api/skill-tracker', methods=['GET'])
@login_required
def get_skill_tracker():
    """Load selected career, roadmap, completed skills, and progress."""
    try:
        if mongo_db is None:
            return jsonify({'success': False, 'error': 'Database not available'}), 503

        user_id = session.get('user_id')
        doc = _get_progress_doc(user_id) or {}
        selected = doc.get('selected_career') or ''
        completed = doc.get('completed_skills') or []

        roadmap = None
        progress = {'completed': 0, 'total': 0, 'percent': 0}

        if selected:
            career = find_career_by_name(fetch_careers(), selected)
            if career:
                roadmap = build_roadmap(career)
                progress = compute_progress(roadmap, completed)
            else:
                selected = ''

        return jsonify({
            'success': True,
            'selected_career': selected,
            'completed_skills': completed,
            'roadmap': roadmap,
            'progress': progress,
        }), 200

    except Exception:
        logging.exception('Skill tracker GET error')
        return jsonify({'success': False, 'error': 'Could not load skill tracker'}), 500


@skill_tracker_bp.route('/api/skill-tracker/career', methods=['PUT'])
@login_required
@csrf_protect
def set_selected_career():
    """Save user's career choice (keeps completed skills for skills that still exist)."""
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        try:
            schema = SkillTrackerCareerSchema(**data)
        except ValidationError as e:
            msg = e.errors()[0]['msg']
            field = e.errors()[0]['loc'][0] if e.errors()[0].get('loc') else 'Field'
            return jsonify({'success': False, 'error': f'{field}: {msg}'}), 400

        if mongo_db is None:
            return jsonify({'success': False, 'error': 'Database not available'}), 503

        career = find_career_by_name(fetch_careers(), schema.career_name)
        if not career:
            return jsonify({'success': False, 'error': 'Career not found'}), 404

        user_id = session.get('user_id')
        username = session.get('username', '')
        now = _now_iso()

        existing = _get_progress_doc(user_id) or {}
        old_completed = existing.get('completed_skills') or []

        roadmap = build_roadmap(career)
        valid_keys = set(flatten_roadmap_skills(roadmap))
        completed = [s for s in old_completed if _skill_key(s) in valid_keys]

        mongo_db[COLLECTION].update_one(
            {'user_id': user_id},
            {
                '$set': {
                    'user_id': user_id,
                    'username': username,
                    'selected_career': schema.career_name,
                    'completed_skills': completed,
                    'updated_at': now,
                },
                '$setOnInsert': {'created_at': now},
            },
            upsert=True,
        )

        progress = compute_progress(roadmap, completed)

        return jsonify({
            'success': True,
            'message': 'Career saved successfully',
            'selected_career': schema.career_name,
            'completed_skills': completed,
            'roadmap': roadmap,
            'progress': progress,
        }), 200

    except Exception:
        logging.exception('Skill tracker set career error')
        return jsonify({'success': False, 'error': 'Could not save career'}), 500


@skill_tracker_bp.route('/api/skill-tracker/skills', methods=['PATCH'])
@login_required
@csrf_protect
def toggle_skill_completion():
    """Mark a skill complete or incomplete."""
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        try:
            schema = SkillTrackerToggleSchema(**data)
        except ValidationError as e:
            msg = e.errors()[0]['msg']
            field = e.errors()[0]['loc'][0] if e.errors()[0].get('loc') else 'Field'
            return jsonify({'success': False, 'error': f'{field}: {msg}'}), 400

        if mongo_db is None:
            return jsonify({'success': False, 'error': 'Database not available'}), 503

        user_id = session.get('user_id')
        doc = _get_progress_doc(user_id)
        if not doc or not doc.get('selected_career'):
            return jsonify({'success': False, 'error': 'Select a career first'}), 400

        career = find_career_by_name(fetch_careers(), doc['selected_career'])
        if not career:
            return jsonify({'success': False, 'error': 'Career not found'}), 404

        roadmap = build_roadmap(career)
        valid_keys = set(flatten_roadmap_skills(roadmap))
        skill_key = _skill_key(schema.skill_key)

        if skill_key not in valid_keys:
            return jsonify({'success': False, 'error': 'Invalid skill for this career'}), 400

        completed = list(doc.get('completed_skills') or [])
        completed_set = {_skill_key(s) for s in completed}

        if schema.completed:
            completed_set.add(skill_key)
        else:
            completed_set.discard(skill_key)

        completed = sorted(completed_set)
        now = _now_iso()

        mongo_db[COLLECTION].update_one(
            {'user_id': user_id},
            {'$set': {'completed_skills': completed, 'updated_at': now}},
        )

        progress = compute_progress(roadmap, completed)

        return jsonify({
            'success': True,
            'completed_skills': completed,
            'progress': progress,
        }), 200

    except Exception:
        logging.exception('Skill tracker toggle error')
        return jsonify({'success': False, 'error': 'Could not update skill'}), 500
