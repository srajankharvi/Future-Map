"""
Recommendation engine — skill-career/course scoring algorithm.
"""


# Skill-to-career mapping
SKILL_CAREER_MAP = {
    'analytical': ['Data Scientist', 'Financial Analyst', 'Cybersecurity Analyst'],
    'creative': ['UX/UI Designer', 'Architect', 'Web Developer'],
    'technical': ['Software Developer', 'Web Developer', 'Cybersecurity Analyst', 'Mechanical Engineer', 'Civil Engineer'],
    'communication': ['Product Manager', 'Teacher / Professor', 'Doctor (MBBS)'],
    'leadership': ['Product Manager', 'Teacher / Professor'],
    'problem-solving': ['Software Developer', 'Data Scientist', 'Mechanical Engineer', 'Civil Engineer'],
    'teamwork': ['Product Manager', 'Civil Engineer', 'Doctor (MBBS)'],
    'design': ['UX/UI Designer', 'Architect', 'Web Developer']
}

# Skill-to-course mapping
SKILL_COURSE_MAP = {
    'analytical': ['B.Tech (Computer Science)', 'B.Com (Commerce)', 'MBA (Business Administration)'],
    'creative': ['B.Arch (Architecture)', 'BCA (Bachelor of Computer Applications)'],
    'technical': ['B.Tech (Computer Science)', 'BCA (Bachelor of Computer Applications)', 'Diploma in Engineering'],
    'communication': ['MBA (Business Administration)', 'B.Ed (Education)'],
    'leadership': ['MBA (Business Administration)', 'B.Ed (Education)'],
    'problem-solving': ['B.Tech (Computer Science)', 'Diploma in Engineering'],
    'teamwork': ['MBA (Business Administration)', 'MBBS (Medicine)'],
    'design': ['B.Arch (Architecture)', 'BCA (Bachelor of Computer Applications)']
}


def compute_recommendations(marks, skills, all_careers, all_courses, education_level='SSLC'):
    """
    Score careers and courses based on user's marks, skills, and education level.
    Returns dict with 'careers' and 'courses' lists, sorted by score, top 5 each.
    """
    # CRITICAL: If marks are less than 30, provide no recommendations
    if marks < 30:
        return {
            'careers': [],
            'courses': []
        }

    # Level-based career filtering/bonus
    LEVEL_CAREER_SUITABILITY = {
        'SSLC': ['Teacher / Professor'],
        'PUC': ['Software Developer', 'Web Developer'],
        'Diploma': ['Software Developer', 'Web Developer', 'Mechanical Engineer', 'Civil Engineer'],
        'Degree': ['Software Developer', 'Data Scientist', 'Financial Analyst', 'UX/UI Designer', 'Architect', 'Cybersecurity Analyst', 'Product Manager', 'Teacher / Professor', 'Doctor (MBBS)'],
        'Masters': ['Data Scientist', 'Product Manager', 'Teacher / Professor', 'Doctor (MBBS)', 'Senior Research Scientist', 'PhD Researcher']
    }

    # Level-based course suitability
    LEVEL_COURSE_SUITABILITY = {
        'SSLC': ['PUC Science', 'PUC Commerce', 'Diploma in Engineering', 'Diploma in Arts'],
        'PUC': ['B.Tech (Computer Science)', 'BCA (Bachelor of Computer Applications)', 'B.Com (Commerce)', 'B.Arch (Architecture)', 'MBBS (Medicine)', 'B.Ed (Education)'],
        'Diploma': ['B.Tech (Lateral Entry)', 'BCA (Bachelor of Computer Applications)', 'Jobs / Apprenticeship'],
        'Degree': ['MBA (Business Administration)', 'M.Tech (Computer Science)', 'MCA (Computer Applications)', 'M.Sc (Data Science)', 'Specialization Course'],
        'Masters': ['PhD (Research)', 'Post-Doc Research', 'Executive MBA', 'Specialized Fellowship']
    }

    # Score careers
    career_scores = {}
    for skill in skills:
        matched_careers = SKILL_CAREER_MAP.get(skill, [])
        for career_name in matched_careers:
            career_scores[career_name] = career_scores.get(career_name, 0) + 1

    # Add marks-based impact (more granular)
    marks_impact = 0
    if marks >= 95:
        marks_impact = 30
    elif marks >= 85:
        marks_impact = 20
    elif marks >= 75:
        marks_impact = 15
    elif marks >= 60:
        marks_impact = 10
    elif marks >= 45:
        marks_impact = 5
    elif marks >= 35:
        marks_impact = -10
    else:
        marks_impact = -20

    # Build scored career list
    scored_careers = []
    suitable_careers = LEVEL_CAREER_SUITABILITY.get(education_level, [])
    
    for career in all_careers:
        raw_score = career_scores.get(career['name'], 0)
        level_bonus = 10 if career['name'] in suitable_careers else 0
        
        # Penalties for advanced roles if user has low education level
        if education_level in ['SSLC', 'PUC'] and career['name'] in ['Data Scientist', 'Product Manager', 'Doctor (MBBS)']:
            level_bonus = -30

        if raw_score > 0 or level_bonus > 0:
            skill_percent = min((raw_score / max(len(skills), 1)) * 60, 60)
            total_score = min(max(round(skill_percent + marks_impact + level_bonus), 0), 99)
            
            # Only add if score is reasonable (depends on marks)
            if total_score > 20:
                scored_careers.append({
                    'name': career['name'],
                    'category': career.get('category', ''),
                    'description': career.get('description', ''),
                    'salary': career.get('salary', 'N/A'),
                    'education': career.get('education', 'N/A'),
                    'score': total_score
                })

    # Score courses
    course_scores = {}
    for skill in skills:
        matched_courses = SKILL_COURSE_MAP.get(skill, [])
        for course_name in matched_courses:
            course_scores[course_name] = course_scores.get(course_name, 0) + 1

    scored_courses = []
    suitable_courses = LEVEL_COURSE_SUITABILITY.get(education_level, [])
    
    # High achiever bonus paths
    if marks >= 85:
        if education_level == 'SSLC':
            suitable_courses.extend(['PUC Science', 'Diploma in Engineering'])
        elif education_level == 'PUC':
            suitable_courses.extend(['B.Tech (Computer Science)', 'MBBS (Medicine)'])
        elif education_level == 'Degree':
            suitable_courses.extend(['MBA (Business Administration)', 'M.Tech (Computer Science)'])

    for course in all_courses:
        raw_score = course_scores.get(course['name'], 0)
        level_bonus = 20 if course['name'] in suitable_courses else 0
        
        if raw_score > 0 or level_bonus > 0:
            skill_percent = min((raw_score / max(len(skills), 1)) * 50, 50)
            total_score = min(max(round(skill_percent + marks_impact + level_bonus), 0), 99)
            
            if total_score > 15:
                scored_courses.append({
                    'name': course['name'],
                    'type': course.get('type', ''),
                    'description': course.get('description', ''),
                    'duration': course.get('duration', 'N/A'),
                    'score': total_score
                })

    # Fallback for low but passing marks
    if not scored_courses and marks >= 30:
        for course_name in suitable_courses[:3]:
            scored_courses.append({
                'name': course_name,
                'type': 'Foundation Path',
                'description': f'A recommended starting point for {education_level} graduates.',
                'duration': 'Varies',
                'score': 40 + marks_impact
            })

    # Sort and return top 5
    scored_careers.sort(key=lambda x: x['score'], reverse=True)
    scored_courses.sort(key=lambda x: x['score'], reverse=True)

    return {
        'careers': scored_careers[:5],
        'courses': scored_courses[:5]
    }
