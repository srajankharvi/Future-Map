"""
Recommendation engine — skill-career/course scoring algorithm.
"""


# Skill-to-career mapping
SKILL_CAREER_MAP = {
    'analytical': ['Data Science', 'Machine Learning', 'Artificial Intelligence', 'Financial Planning', 'Banking and Finance', 'Chartered Accountancy (CA)', 'Cyber Security', 'Computer Science'],
    'creative': ['UI/UX Design', 'Graphic Design', 'Game Design', 'Product Design', 'Interior Design', 'Fashion Design', 'Visual Communication', 'Animation and Multimedia'],
    'technical': ['Software Engineering', 'Full Stack Development', 'Web Development', 'Mobile App Development', 'Cloud Computing', 'Computer Science', 'Machine Learning', 'Artificial Intelligence', 'Mechanical Engineering', 'Civil Engineering', 'Electrical Engineering', 'Robotics Engineering'],
    'communication': ['Human Resource Management', 'Marketing Management', 'Aviation Management', 'Public Health', 'Bachelor of Education (B.Ed)', 'Special Education', 'Cabin Crew & Aviation Hospitality'],
    'leadership': ['Master of Business Administration (MBA)', 'Bachelor of Business Administration (BBA)', 'Agribusiness Management', 'Supply Chain Management', 'Airport Operations Management', 'Aviation Management', 'Human Resource Management'],
    'problem-solving': ['Software Engineering', 'Full Stack Development', 'Data Science', 'Machine Learning', 'Artificial Intelligence', 'Cyber Security', 'Robotics Engineering', 'Mechanical Engineering', 'Civil Engineering', 'Chemical Engineering'],
    'teamwork': ['Master of Business Administration (MBA)', 'Bachelor of Business Administration (BBA)', 'MBBS', 'BDS', 'B.Sc Nursing', 'Cabin Crew & Aviation Hospitality', 'Aviation Management'],
    'design': ['UI/UX Design', 'Product Design', 'Graphic Design', 'Fashion Design', 'Interior Design', 'Landscape Architecture', 'Bachelor of Architecture (B.Arch)', 'Auto CAD Design']
}

# Skill-to-course mapping
SKILL_COURSE_MAP = {
    'analytical': ['Computer Science Engineering (CSE)', 'Data Science', 'Bachelor of Commerce (B.Com)', 'Master of Commerce (M.Com)', 'Chartered Accountancy (CA)', 'Cyber Security'],
    'creative': ['Bachelor of Design (B.Des)', 'Bachelor of Fine Arts (BFA)', 'Digital Marketing', 'Bachelor of Computer Applications (BCA)'],
    'technical': ['Computer Science Engineering (CSE)', 'Bachelor of Computer Applications (BCA)', 'Software Engineering', 'Robotics Engineering', 'Cloud Computing', 'Internet of Things (IoT)', 'Mechanical Engineering', 'Civil Engineering', 'Electrical Engineering', 'Electronics and Communication Engineering (ECE)'],
    'communication': ['Bachelor of Arts (B.A)', 'Master of Arts (M.A)', 'Digital Marketing', 'Public Relations Management', 'Bachelor of Education (B.Ed)', 'Hotel Management'],
    'leadership': ['Master of Business Administration (MBA)', 'Bachelor of Business Administration (BBA)', 'Supply Chain Management', 'Human Resource Management', 'Financial Management', 'Aviation Management'],
    'problem-solving': ['Computer Science Engineering (CSE)', 'Software Engineering', 'Robotics Engineering', 'Data Science', 'Cyber Security', 'Mechanical Engineering', 'Civil Engineering', 'Electrical Engineering'],
    'teamwork': ['Master of Business Administration (MBA)', 'Bachelor of Business Administration (BBA)', 'MBBS', 'BDS', 'B.Sc Nursing', 'Hotel Management', 'Event Management'],
    'design': ['Bachelor of Design (B.Des)', 'Bachelor of Fine Arts (BFA)', 'Digital Marketing', 'Bachelor of Computer Applications (BCA)']
}


def _education_from_requirements(item):
    requirements = item.get('requirements')
    if isinstance(requirements, dict):
        return requirements.get('minimum_qualification') or requirements.get('qualification') or ''
    if isinstance(requirements, str):
        return requirements
    return item.get('education', '')


def _with_score(item, score):
    result = dict(item)
    result['score'] = score
    result['education'] = _education_from_requirements(result) or 'Not specified'
    return result


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
        'SSLC': ['Beauty Therapy', 'Cosmetology', 'Makeup Artistry', 'Nail Art Technology', 'Hair Styling and Care', 'Spa and Wellness Management', 'Vehicle Maintenance Technology'],
        'PUC': ['Cabin Crew & Aviation Hospitality', 'Web Development', 'Graphic Design', 'Animation and Multimedia', 'Visual Communication'],
        'Diploma': ['Mechanical Engineering', 'Civil Engineering', 'Electrical Engineering', 'Electronics Engineering', 'Automobile Engineering', 'Auto CAD Design', 'Web Development', 'Mobile App Development'],
        'Degree': ['Software Engineering', 'Full Stack Development', 'UI/UX Design', 'Data Science', 'Cyber Security', 'Investment Banking', 'Chartered Accountancy (CA)', 'MBBS', 'BDS', 'Bachelor of Architecture (B.Arch)', 'Mechanical Engineering', 'Civil Engineering'],
        'Masters': ['Master of Business Administration (MBA)', 'Master of Education (M.Ed)', 'Data Science', 'Machine Learning', 'Artificial Intelligence', 'Robotics Engineering', 'Special Education']
    }

    # Level-based course suitability
    LEVEL_COURSE_SUITABILITY = {
        'SSLC': ['Bachelor of Science (B.Sc)', 'Bachelor of Commerce (B.Com)', 'Bachelor of Arts (B.A)', 'General Nursing and Midwifery (GNM)'],
        'PUC': ['Computer Science Engineering (CSE)', 'Bachelor of Computer Applications (BCA)', 'Bachelor of Business Administration (BBA)', 'Bachelor of Commerce (B.Com)', 'Bachelor of Arts (B.A)', 'Bachelor of Design (B.Des)', 'MBBS', 'BDS', 'Bachelor of Education (B.Ed)', 'Bachelor of Pharmacy (B.Pharm)', 'BPT', 'B.Sc Nursing'],
        'Diploma': ['Computer Science Engineering (CSE)', 'Mechanical Engineering', 'Civil Engineering', 'Electrical Engineering', 'Electronics and Communication Engineering (ECE)', 'Bachelor of Computer Applications (BCA)'],
        'Degree': ['Master of Business Administration (MBA)', 'Master of Computer Applications (MCA)', 'Master of Science (M.Sc)', 'Master of Arts (M.A)', 'Chartered Accountancy (CA)', 'Company Secretary (CS)', 'Cost and Management Accounting (CMA)'],
        'Masters': ['MD', 'Master of Education (M.Ed)', 'Master of Business Administration (MBA)', 'Supply Chain Management', 'Human Resource Management']
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
        if education_level in ['SSLC', 'PUC'] and career['name'] in ['Data Science', 'Machine Learning', 'Artificial Intelligence', 'MBBS', 'BDS', 'Software Engineering']:
            level_bonus = -30

        if raw_score > 0 or level_bonus > 0:
            skill_percent = min((raw_score / max(len(skills), 1)) * 60, 60)
            total_score = min(max(round(skill_percent + marks_impact + level_bonus), 0), 99)
            
            # Only add if score is reasonable (depends on marks)
            if total_score > 20:
                scored_careers.append(_with_score(career, total_score))

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
            suitable_courses.extend(['Computer Science Engineering (CSE)', 'Bachelor of Science (B.Sc)'])
        elif education_level == 'PUC':
            suitable_courses.extend(['Computer Science Engineering (CSE)', 'MBBS', 'Software Engineering'])
        elif education_level == 'Degree':
            suitable_courses.extend(['Master of Business Administration (MBA)', 'Master of Computer Applications (MCA)'])

    for course in all_courses:
        raw_score = course_scores.get(course['name'], 0)
        level_bonus = 20 if course['name'] in suitable_courses else 0
        
        if raw_score > 0 or level_bonus > 0:
            skill_percent = min((raw_score / max(len(skills), 1)) * 50, 50)
            total_score = min(max(round(skill_percent + marks_impact + level_bonus), 0), 99)
            
            if total_score > 15:
                scored_courses.append(_with_score(course, total_score))

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
