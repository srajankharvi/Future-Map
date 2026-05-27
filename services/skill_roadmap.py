"""
Career Skill Roadmap — build step-by-step learning paths from career data.
"""

import re
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Skill metadata (description + why learn)
# ---------------------------------------------------------------------------

def _meta(name: str, desc: str, why: str) -> Dict[str, str]:
    return {'name': name, 'description': desc, 'why_learn': why}


_SKILL_LIBRARY: Dict[str, Dict[str, str]] = {
    'html': _meta('HTML', 'Markup language for structuring web pages.', 'Foundation of every website — you need it before CSS or JavaScript.'),
    'css': _meta('CSS', 'Styles layouts, colors, and responsive design.', 'Makes interfaces usable and professional across devices.'),
    'javascript': _meta('JavaScript', 'Programming language for interactive web apps.', 'Core language of the web and gateway to frameworks like React.'),
    'git': _meta('Git', 'Version control system for tracking code changes.', 'Industry standard for collaboration and safe experimentation.'),
    'github': _meta('GitHub', 'Cloud platform for hosting Git repositories.', 'Where teams review code, ship features, and showcase portfolios.'),
    'vs code': _meta('VS Code', 'Popular code editor with extensions and debugging.', 'Boosts productivity with linting, Git integration, and AI helpers.'),
    'react': _meta('React', 'JavaScript library for building user interfaces.', 'Used widely for modern web development and job-ready portfolios.'),
    'responsive design': _meta('Responsive Design', 'Techniques to adapt layouts to all screen sizes.', 'Expected skill for any frontend or full-stack role.'),
    'node.js': _meta('Node.js', 'JavaScript runtime for server-side applications.', 'Lets you build APIs and backends with one language.'),
    'apis': _meta('APIs', 'Interfaces for apps to exchange data over HTTP.', 'Connects frontend, mobile, and third-party services.'),
    'authentication': _meta('Authentication', 'Login, sessions, JWT, and secure access control.', 'Required for real products that protect user data.'),
    'mongodb': _meta('MongoDB', 'Document database for flexible JSON-like data.', 'Common in Node stacks and rapid prototyping.'),
    'sql basics': _meta('SQL Basics', 'Querying relational databases with structured tables.', 'Still essential for analytics, backends, and enterprise systems.'),
    'portfolio website': _meta('Portfolio Website', 'Personal site showcasing projects and skills.', 'Proves ability to recruiters better than a resume alone.'),
    'chat application': _meta('Chat Application', 'Real-time messaging app with websockets or polling.', 'Demonstrates APIs, state management, and UX thinking.'),
    'e-commerce project': _meta('E-commerce Project', 'Online store with cart, checkout, and catalog.', 'Covers full-stack flows employers look for.'),
    'python': _meta('Python', 'Versatile language for web, data, and automation.', 'Top choice for data science, scripting, and backends.'),
    'data structures': _meta('Data Structures', 'Arrays, trees, graphs, and algorithmic thinking.', 'Foundation for technical interviews and efficient code.'),
    'algorithms': _meta('Algorithms', 'Problem-solving patterns and complexity analysis.', 'Core computer-science skill for software roles.'),
    'docker': _meta('Docker', 'Containerization for consistent dev and deploy environments.', 'Standard in DevOps and modern deployment pipelines.'),
    'cloud basics': _meta('Cloud Basics', 'Deploying apps on AWS, Azure, or GCP fundamentals.', 'Most production systems run in the cloud today.'),
    'testing': _meta('Testing', 'Unit, integration, and end-to-end test practices.', 'Keeps code reliable as projects grow.'),
    'agile': _meta('Agile', 'Iterative delivery with sprints and stand-ups.', 'How most tech teams plan and ship work.'),
}

# Lower = earlier in path (prerequisite order)
_ORDER_RANK: Dict[str, int] = {
    'html': 10, 'css': 20, 'javascript': 30, 'python': 25,
    'git': 40, 'github': 45, 'vs code': 42,
    'responsive design': 50, 'react': 55, 'node.js': 60,
    'apis': 65, 'authentication': 70, 'sql basics': 68, 'mongodb': 72,
    'data structures': 35, 'algorithms': 38,
    'docker': 80, 'cloud basics': 85, 'testing': 75, 'agile': 90,
    'portfolio website': 100, 'chat application': 105, 'e-commerce project': 110,
}

_TECH_NAME_PATTERNS = re.compile(
    r'(full\s*stack|software|web\s*dev|frontend|backend|data\s*science|'
    r'devops|cyber|cloud|programmer|developer|computer\s*science|it\s*support|'
    r'machine\s*learning|ai\s*engineer|mobile\s*app)',
    re.I,
)

_IT_CATEGORY = 'computer & it'

# Step templates for tech careers (merged with DB skills)
_TECH_STEP_TEMPLATES: List[Dict[str, Any]] = [
    {
        'title': 'Step 1: Foundations',
        'skill_keys': ['html', 'css', 'javascript'],
    },
    {
        'title': 'Step 2: Development Tools',
        'skill_keys': ['git', 'github', 'vs code'],
    },
    {
        'title': 'Step 3: Frontend',
        'skill_keys': ['react', 'responsive design'],
    },
    {
        'title': 'Step 4: Backend',
        'skill_keys': ['node.js', 'apis', 'authentication'],
    },
    {
        'title': 'Step 5: Database',
        'skill_keys': ['mongodb', 'sql basics'],
    },
    {
        'title': 'Step 6: Projects',
        'skill_keys': ['portfolio website', 'chat application', 'e-commerce project'],
    },
]

_DATA_STEP_TEMPLATE: List[Dict[str, Any]] = [
    {'title': 'Step 1: Programming Foundations', 'skill_keys': ['python', 'data structures', 'algorithms']},
    {'title': 'Step 2: Data & Analysis', 'skill_keys': ['sql basics', 'mongodb']},
    {'title': 'Step 3: Tools & Workflow', 'skill_keys': ['git', 'github', 'vs code']},
    {'title': 'Step 4: Deployment & Quality', 'skill_keys': ['testing', 'cloud basics', 'docker']},
    {'title': 'Step 5: Portfolio Projects', 'skill_keys': ['portfolio website', 'e-commerce project']},
]


def slugify_skill(name: str) -> str:
    """Normalized key for storage and lookup."""
    s = (name or '').strip().lower()
    s = re.sub(r'[^a-z0-9\s\-]', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s.replace(' ', '-') if ' ' not in s else s  # keep readable keys with spaces as single slug


def _skill_key(name: str) -> str:
    """Canonical key: lowercase trimmed name (matches completedSkills storage)."""
    return re.sub(r'\s+', ' ', (name or '').strip().lower())


def _is_tech_career(career: Dict[str, Any]) -> bool:
    category = (career.get('category') or '').strip().lower()
    name = career.get('name') or ''
    if category == _IT_CATEGORY:
        return True
    return bool(_TECH_NAME_PATTERNS.search(name))


def _pick_tech_template(career_name: str) -> List[Dict[str, Any]]:
    name = (career_name or '').lower()
    if any(k in name for k in ('data', 'analyst', 'science', 'machine', 'ai ')):
        return _DATA_STEP_TEMPLATE
    return _TECH_STEP_TEMPLATES


def _fallback_meta(name: str, career: Dict[str, Any]) -> Dict[str, str]:
    clean = name.strip()
    cat = career.get('category') or 'your field'
    return _meta(
        clean,
        f'Core competency for {career.get("name", "this career")} in {cat}.',
        f'Builds expertise employers expect in {cat} roles.',
    )


def _resolve_skill(name: str, career: Dict[str, Any]) -> Dict[str, str]:
    key = _skill_key(name)
    lib = _SKILL_LIBRARY.get(key)
    if lib:
        return {**lib, 'key': key}
    fb = _fallback_meta(name, career)
    return {**fb, 'key': key}


def _sort_skills(skills: List[Dict[str, str]]) -> List[Dict[str, str]]:
    def rank(s: Dict[str, str]) -> int:
        k = s.get('key', '')
        return _ORDER_RANK.get(k, _ORDER_RANK.get(s.get('name', '').lower(), 500))

    return sorted(skills, key=rank)


def _chunk_list(items: List[str], chunk_size: int = 5) -> List[List[str]]:
    if not items:
        return []
    chunks = []
    for i in range(0, len(items), chunk_size):
        chunks.append(items[i:i + chunk_size])
    return chunks


def _collect_career_skill_names(career: Dict[str, Any]) -> List[str]:
    """Gather skill strings from career database fields."""
    names: List[str] = []
    seen = set()

    def add(item: Any) -> None:
        if not item or not isinstance(item, str):
            return
        text = item.strip()
        if not text or len(text) > 120:
            return
        key = _skill_key(text)
        if key in seen:
            return
        seen.add(key)
        names.append(text)

    for field in ('skills_gained', 'skills', 'subjects'):
        val = career.get(field)
        if isinstance(val, list):
            for x in val:
                add(x)

    # Shorter job titles can act as milestone "skills" in projects step
    for field in ('job_roles',):
        val = career.get(field)
        if isinstance(val, list):
            for x in val[:5]:
                add(x)

    return names


def build_roadmap(career: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build step-by-step roadmap (no beginner/intermediate/advanced levels).
    Returns { career_name, category, steps: [{ title, skills: [...] }] }.
    """
    if not career:
        return {'career_name': '', 'category': '', 'steps': []}

    career_name = career.get('name') or ''
    category = career.get('category') or ''
    db_skills = _collect_career_skill_names(career)

    if _is_tech_career(career):
        steps_out = _build_tech_roadmap(career, career_name, db_skills)
    else:
        steps_out = _build_generic_roadmap(career, career_name, db_skills)

    return {
        'career_name': career_name,
        'category': category,
        'steps': steps_out,
    }


def _build_tech_roadmap(
    career: Dict[str, Any],
    career_name: str,
    db_skills: List[str],
) -> List[Dict[str, Any]]:
    template = _pick_tech_template(career_name)
    used_keys = set()
    steps_out: List[Dict[str, Any]] = []

    for step_def in template:
        skills = []
        for sk in step_def['skill_keys']:
            resolved = _resolve_skill(sk.replace('-', ' ') if '-' in sk else sk, career)
            if resolved['key'] not in used_keys:
                used_keys.add(resolved['key'])
                skills.append(resolved)
        if skills:
            steps_out.append({
                'title': step_def['title'],
                'skills': _sort_skills(skills),
            })

    # Career-specific skills from database (avoid duplicating template keys)
    domain_skills = []
    for name in db_skills:
        key = _skill_key(name)
        if key in used_keys:
            continue
        # Skip very long career option strings
        if len(name) > 60:
            continue
        used_keys.add(key)
        domain_skills.append(_resolve_skill(name, career))

    if domain_skills:
        steps_out.append({
            'title': f'Step {len(steps_out) + 1}: Career-Specific Skills',
            'skills': _sort_skills(domain_skills),
        })

    # Project milestones from career_options
    project_names = []
    for opt in (career.get('career_options') or [])[:4]:
        if isinstance(opt, str) and opt.strip():
            short = opt.split(' - ')[-1].strip() if ' - ' in opt else opt.strip()
            if len(short) <= 50:
                project_names.append(short)

    if project_names:
        proj_skills = []
        for pname in project_names:
            key = _skill_key(pname)
            if key not in used_keys:
                used_keys.add(key)
                proj_skills.append(_resolve_skill(pname, career))
        if proj_skills:
            steps_out.append({
                'title': f'Step {len(steps_out) + 1}: Career Milestones',
                'skills': proj_skills,
            })

    return steps_out


def _build_generic_roadmap(
    career: Dict[str, Any],
    career_name: str,
    db_skills: List[str],
) -> List[Dict[str, Any]]:
    if not db_skills:
        db_skills = ['Core domain knowledge', 'Professional communication', 'Practical application']

    # Keyword-based prerequisite ordering for generic skills
    def generic_rank(name: str) -> int:
        low = name.lower()
        if any(w in low for w in ('foundation', 'basic', 'introduction', 'fundamental')):
            return 10
        if any(w in low for w in ('communication', 'team', 'ethic', 'regulatory')):
            return 30
        if any(w in low for w in ('analytical', 'problem', 'critical', 'research')):
            return 40
        if any(w in low for w in ('advanced', 'strategic', 'leadership', 'management')):
            return 70
        if any(w in low for w in ('project', 'capstone', 'internship', 'practicum')):
            return 90
        return 50

    ordered = sorted(db_skills, key=generic_rank)
    chunks = _chunk_list(ordered, 5)
    step_titles = [
        'Step 1: Foundations',
        'Step 2: Core Competencies',
        'Step 3: Applied Skills',
        'Step 4: Advanced Practice',
        'Step 5: Professional Growth',
        'Step 6: Career Readiness',
    ]

    steps_out = []
    for i, chunk in enumerate(chunks):
        title = step_titles[i] if i < len(step_titles) else f'Step {i + 1}: Continue Learning'
        skills = [_resolve_skill(n, career) for n in chunk]
        steps_out.append({'title': title, 'skills': skills})

    return steps_out


def flatten_roadmap_skills(roadmap: Dict[str, Any]) -> List[str]:
    """All skill keys in order for progress calculation."""
    keys = []
    for step in roadmap.get('steps') or []:
        for sk in step.get('skills') or []:
            k = sk.get('key')
            if k and k not in keys:
                keys.append(k)
    return keys


def compute_progress(roadmap: Dict[str, Any], completed_skills: List[str]) -> Dict[str, Any]:
    all_keys = flatten_roadmap_skills(roadmap)
    completed_set = {_skill_key(s) for s in (completed_skills or [])}
    done = sum(1 for k in all_keys if k in completed_set)
    total = len(all_keys)
    percent = round((done / total) * 100) if total else 0
    return {
        'completed': done,
        'total': total,
        'percent': percent,
    }


def find_career_by_name(careers: List[Dict[str, Any]], name: str) -> Optional[Dict[str, Any]]:
    if not name:
        return None
    target = name.strip().lower()
    for c in careers:
        if (c.get('name') or '').strip().lower() == target:
            return c
    return None
