"""
Fallback courses data used when MongoDB is unavailable or empty.
"""

FALLBACK_COURSES = [
    {
        'name': 'B.Tech (Computer Science)',
        'type': 'DEGREE',
        'category': 'Engineering',
        'description': 'Four-year undergraduate program focused on computer science and software engineering fundamentals.',
        'duration': '4 years',
        'requirements': '10+2 with PCM, JEE/State entrance exam',
        'scope': 'Software development, data science, AI/ML, cybersecurity, cloud computing',
        'details': 'B.Tech CS covers programming, data structures, algorithms, databases, networking, and software engineering.'
    },
    {
        'name': 'BCA (Bachelor of Computer Applications)',
        'type': 'DEGREE',
        'category': 'Computer',
        'description': 'Three-year undergraduate program covering computer applications and programming.',
        'duration': '3 years',
        'requirements': '10+2 with Mathematics',
        'scope': 'Web development, software testing, IT support, system administration',
        'details': 'BCA provides foundational knowledge in programming languages, web technologies, databases, and computer networks.'
    },
    {
        'name': 'MBBS (Medicine)',
        'type': 'MEDICAL',
        'category': 'Healthcare',
        'description': 'Five and a half year medical degree for aspiring doctors.',
        'duration': '5.5 years',
        'requirements': '10+2 with PCB, NEET qualification',
        'scope': 'General practice, specialization (MD/MS), research, hospital management',
        'details': 'MBBS covers human anatomy, physiology, pharmacology, pathology, and clinical rotations in various medical specialties.'
    },
    {
        'name': 'MBA (Business Administration)',
        'type': 'PROFESSIONAL',
        'category': 'Business',
        'description': 'Two-year postgraduate program in business management and administration.',
        'duration': '2 years',
        'requirements': 'Graduation + CAT/MAT/GMAT score',
        'scope': 'Management consulting, finance, marketing, operations, entrepreneurship',
        'details': 'MBA covers marketing, finance, HR, operations, strategy, and leadership with case-based learning.'
    },
    {
        'name': 'B.Arch (Architecture)',
        'type': 'DEGREE',
        'category': 'Architecture',
        'description': 'Five-year undergraduate program in architectural design and planning.',
        'duration': '5 years',
        'requirements': '10+2 with Mathematics, NATA/JEE Paper 2',
        'scope': 'Architecture firms, urban planning, interior design, construction management',
        'details': 'B.Arch covers building design, structural systems, urban planning, sustainability, and architectural history.'
    },
    {
        'name': 'Diploma in Engineering',
        'type': 'TECHNICAL',
        'category': 'Engineering',
        'description': 'Three-year polytechnic diploma in various engineering branches.',
        'duration': '3 years',
        'requirements': '10th pass with Mathematics and Science',
        'scope': 'Technical roles in manufacturing, maintenance, construction, and IT support',
        'details': 'Engineering diploma provides hands-on technical training in mechanical, electrical, civil, or computer engineering.'
    },
    {
        'name': 'B.Com (Commerce)',
        'type': 'DEGREE',
        'category': 'Business',
        'description': 'Three-year undergraduate program in commerce, accounting, and finance.',
        'duration': '3 years',
        'requirements': '10+2 with Commerce stream',
        'scope': 'Accounting, banking, taxation, financial analysis, CA/CMA preparation',
        'details': 'B.Com covers accounting principles, business law, economics, taxation, corporate finance, and auditing.'
    },
    {
        'name': 'B.Ed (Education)',
        'type': 'PROFESSIONAL',
        'category': 'Education',
        'description': 'Two-year professional degree for aspiring teachers.',
        'duration': '2 years',
        'requirements': 'Graduation with minimum 50% marks',
        'scope': 'Teaching in schools (government/private), education administration, curriculum development',
        'details': 'B.Ed covers pedagogy, educational psychology, teaching methods, assessment techniques, and classroom management.'
    }
]
