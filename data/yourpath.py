"""
YourPath reference/fallback data — career-course mapping, roadmap templates,
detailed info, projects, and resources.
"""

FALLBACK_CAREER_COURSE_MAPPING = {
    "Aerospace & Aviation": ["B Tech", "Diploma in Engineering", "M Tech"],
    "Agriculture": ["B Sc", "M Tech", "Diploma in Engineering"],
    "Automobile": ["B Tech", "Diploma in Engineering", "M Tech"],
    "Banking/Finance": ["B Com", "MBA", "CA", "BBA"],
    "Beauty & Wellness": ["BA", "BBA"],
    "Computer": ["B Tech", "BCA", "MCA", "M Tech", "Diploma in IT"],
    "Engineering": ["B Tech", "M Tech", "Diploma in Engineering"],
    "Architecture": ["B Arch", "M Tech"],
    "Healthcare": ["MBBS", "B Sc Nursing", "B Pharma", "BDS", "Pharm D"],
    "Arts": ["BA", "BCA", "BBA"],
    "Business": ["BBA", "MBA", "B Com", "CA"],
    "Education": ["BA", "B Ed", "B Sc"]
}

FALLBACK_ROADMAP_TEMPLATES = {
    "Aerospace & Aviation": [
        {"step": "Foundation", "title": "Build Your Academic Base", "desc": "Complete your 10+2 with PCM scoring above 60%.", "duration": "2 years"},
        {"step": "Entrance Exams", "title": "Prepare for Entrance Tests", "desc": "Prepare and clear JEE, DGCA, or aviation academy tests.", "duration": "6-12 months"},
        {"step": "Education", "title": "Complete Your Degree/Training", "desc": "Enroll and complete your chosen course program.", "duration": "2-4 years"},
        {"step": "Certification", "title": "Get Industry Certifications", "desc": "Obtain CPL/ATPL, AME license, or DGCA approvals.", "duration": "6-12 months"},
        {"step": "Internship", "title": "Industry Internship & Training", "desc": "Complete internship at airlines or aerospace companies.", "duration": "6-12 months"},
        {"step": "Entry Level", "title": "Start Your Career", "desc": "Apply for entry-level positions in aerospace.", "duration": "1-2 years"},
        {"step": "Growth", "title": "Advance & Specialize", "desc": "Pursue advanced certifications and specialize.", "duration": "Ongoing"}
    ],
    "Computer": [
        {"step": "Foundation", "title": "Build Strong Foundations", "desc": "Complete 10+2 with PCM or CS. Learn programming basics.", "duration": "2 years"},
        {"step": "Entrance Exams", "title": "Clear Entrance Exams", "desc": "Prepare for JEE, CUET, or state-level exams.", "duration": "6-12 months"},
        {"step": "Education", "title": "Complete Your Degree", "desc": "Pursue B Tech CSE, BCA, or diploma.", "duration": "3-4 years"},
        {"step": "Projects & Skills", "title": "Build Projects & Skills", "desc": "Create projects, contribute to open source.", "duration": "6-12 months"},
        {"step": "Internship", "title": "Industry Internship", "desc": "Intern at tech companies or startups.", "duration": "3-6 months"},
        {"step": "Career Start", "title": "Start Your Tech Career", "desc": "Join as software developer or data analyst.", "duration": "1-2 years"},
        {"step": "Growth", "title": "Specialize & Lead", "desc": "Specialize in AI/ML, cloud, or cybersecurity.", "duration": "Ongoing"}
    ]
}

FALLBACK_CAREER_DETAILED_INFO = {
    "Computer": {
        "growthOutlook": "Very High - IT/Tech sector is the fastest growing globally",
        "skillBreakdown": [
            {"name": "Programming", "icon": "laptop", "level": "Expert", "percentage": 95, "color": "#667eea", "description": "Python, Java, JavaScript, C++"},
            {"name": "Problem Solving", "icon": "puzzle", "level": "Expert", "percentage": 90, "color": "#f093fb", "description": "Data structures, algorithms, debugging"},
            {"name": "Analytical Skills", "icon": "chart", "level": "Advanced", "percentage": 85, "color": "#4facfe", "description": "Data analysis, architecture decisions"},
            {"name": "Technical Tools", "icon": "wrench", "level": "Advanced", "percentage": 80, "color": "#10b981", "description": "Git, Docker, cloud platforms"},
            {"name": "Communication", "icon": "mic", "level": "Intermediate", "percentage": 65, "color": "#f59e0b", "description": "Code reviews, documentation"}
        ]
    }
}

FALLBACK_CAREER_PROJECTS = {
    "Computer": [
        {"title": "Portfolio Website", "description": "Build a responsive personal portfolio website.", "skills": ["Technical", "Design"], "difficulty": "Beginner", "timeEstimate": "1-2 weeks"},
        {"title": "To-Do App with Database", "description": "Create a full-stack to-do application.", "skills": ["Technical", "Problem-Solving"], "difficulty": "Intermediate", "timeEstimate": "3-4 weeks"},
        {"title": "API-Based Weather App", "description": "Build a weather forecast app using a public API.", "skills": ["Technical", "Design"], "difficulty": "Beginner", "timeEstimate": "1-2 weeks"}
    ]
}

FALLBACK_CAREER_RESOURCES = {
    "Computer": {
        "tools": ["VS Code / IntelliJ IDE", "Git & GitHub", "Docker / Kubernetes", "AWS / Azure / GCP Cloud"],
        "certifications": ["AWS Solutions Architect", "Google Cloud Professional", "CompTIA Security+"],
        "subjects": ["Data Structures & Algorithms", "Operating Systems", "Database Management (SQL)", "Computer Networks"]
    }
}
