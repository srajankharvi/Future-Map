"""
Fallback careers data used when MongoDB is unavailable or empty.
"""

FALLBACK_CAREERS = [
    {
        'name': 'Software Developer',
        'category': 'Computer',
        'description': 'Build and maintain software applications using programming languages and frameworks.',
        'salary': '4-12 LPA',
        'education': 'B.Tech/BCA in CS/IT',
        'skills': ['Python', 'JavaScript', 'Problem Solving', 'Data Structures'],
        'details': 'Software developers design, code, test, and maintain software systems. They work across web, mobile, and desktop platforms.'
    },
    {
        'name': 'Data Scientist',
        'category': 'Computer',
        'description': 'Analyze complex data sets to derive meaningful business insights using ML and statistics.',
        'salary': '6-15 LPA',
        'education': 'B.Tech/M.Tech + Data Science specialization',
        'skills': ['Python', 'SQL', 'Statistics', 'Machine Learning'],
        'details': 'Data scientists collect, clean, and analyze large datasets to find patterns, build predictive models, and drive data-driven decisions.'
    },
    {
        'name': 'Web Developer',
        'category': 'Computer',
        'description': 'Create and maintain websites and web applications using modern technologies.',
        'salary': '3-10 LPA',
        'education': 'BCA/B.Tech in CS/IT',
        'skills': ['HTML', 'CSS', 'JavaScript', 'React/Angular'],
        'details': 'Web developers build responsive, interactive websites. They handle front-end user interfaces and back-end server logic.'
    },
    {
        'name': 'Product Manager',
        'category': 'Business',
        'description': 'Lead product strategy, roadmap, and cross-functional teams to deliver successful products.',
        'salary': '8-20 LPA',
        'education': 'MBA or B.Tech with management experience',
        'skills': ['Leadership', 'Communication', 'Analytics', 'Strategy'],
        'details': 'Product managers define the vision for a product, prioritize features, work with engineering and design teams, and ensure products meet market needs.'
    },
    {
        'name': 'UX/UI Designer',
        'category': 'Arts',
        'description': 'Design intuitive and visually appealing user interfaces and experiences.',
        'salary': '4-12 LPA',
        'education': 'B.Des/BCA with design portfolio',
        'skills': ['Figma', 'Adobe XD', 'User Research', 'Prototyping'],
        'details': 'UX/UI designers research user needs, create wireframes and prototypes, and design beautiful interfaces that enhance user satisfaction.'
    },
    {
        'name': 'Cybersecurity Analyst',
        'category': 'Computer',
        'description': 'Protect organizations from cyber threats and ensure information security.',
        'salary': '5-15 LPA',
        'education': 'B.Tech in CS/IT + security certifications',
        'skills': ['Network Security', 'Ethical Hacking', 'Cryptography', 'Risk Assessment'],
        'details': 'Cybersecurity analysts monitor networks for threats, implement security measures, respond to incidents, and ensure compliance with security standards.'
    },
    {
        'name': 'Mechanical Engineer',
        'category': 'Engineering',
        'description': 'Design, develop, and test mechanical devices and systems.',
        'salary': '4-10 LPA',
        'education': 'B.Tech in Mechanical Engineering',
        'skills': ['CAD', 'Thermodynamics', 'Manufacturing', 'Problem Solving'],
        'details': 'Mechanical engineers apply principles of physics and materials science to design and manufacture everything from small components to large machines.'
    },
    {
        'name': 'Doctor (MBBS)',
        'category': 'Healthcare',
        'description': 'Diagnose and treat illnesses, prescribe medications, and promote health.',
        'salary': '6-20 LPA',
        'education': 'MBBS + Specialization',
        'skills': ['Medical Knowledge', 'Communication', 'Empathy', 'Critical Thinking'],
        'details': 'Doctors examine patients, diagnose medical conditions, prescribe treatments, and guide patients toward healthy lifestyles.'
    },
    {
        'name': 'Civil Engineer',
        'category': 'Engineering',
        'description': 'Plan, design, and oversee construction of infrastructure projects.',
        'salary': '4-12 LPA',
        'education': 'B.Tech in Civil Engineering',
        'skills': ['Structural Analysis', 'AutoCAD', 'Project Management', 'Surveying'],
        'details': 'Civil engineers design and supervise the construction of roads, bridges, buildings, and water systems. They ensure structures are safe, sustainable, and functional.'
    },
    {
        'name': 'Financial Analyst',
        'category': 'Banking/Finance',
        'description': 'Analyze financial data and provide investment recommendations.',
        'salary': '5-15 LPA',
        'education': 'B.Com/MBA Finance/CA',
        'skills': ['Financial Modeling', 'Excel', 'Accounting', 'Data Analysis'],
        'details': 'Financial analysts evaluate investment opportunities, analyze financial statements, create forecasts, and advise businesses on financial decisions.'
    },
    {
        'name': 'Teacher / Professor',
        'category': 'Education',
        'description': 'Educate and inspire students in academic institutions.',
        'salary': '3-10 LPA',
        'education': 'B.Ed/M.Ed + Subject expertise',
        'skills': ['Communication', 'Patience', 'Subject Knowledge', 'Leadership'],
        'details': 'Teachers plan lessons, deliver instruction, assess student progress, and create supportive learning environments in schools and universities.'
    },
    {
        'name': 'Architect',
        'category': 'Architecture',
        'description': 'Design buildings and spaces that are functional, aesthetic, and sustainable.',
        'salary': '4-15 LPA',
        'education': 'B.Arch (5 years)',
        'skills': ['AutoCAD', '3D Modeling', 'Creative Design', 'Structural Knowledge'],
        'details': 'Architects create detailed plans for buildings and structures, considering aesthetics, safety, functionality, and environmental impact.'
    },
    {
        'name': 'Airline Pilot',
        'category': 'Aerospace & Aviation',
        'description': 'Operate and navigate commercial aircraft safely across domestic and international routes.',
        'salary': '10-60 LPA',
        'education': 'Commercial Pilot License (CPL) + Training',
        'skills': ['Technical Knowledge', 'Analytical Skills', 'Leadership', 'Decision Making'],
        'details': 'Airline pilots are responsible for flying aircraft, ensuring passenger safety, managing flight systems, and handling emergency situations with precision and confidence.'
    },
    {
        'name': 'Commercial Pilot',
        'category': 'Aerospace & Aviation',
        'description': 'Operate charter, cargo, and private flights.',
        'salary': '10-80 LPA',
        'education': 'Commercial Pilot License (CPL)',
        'skills': ['Technical Knowledge', 'Decision-Making', 'Navigation'],
        'details': 'Commercial pilots fly aircraft for commercial purposes such as transporting passengers or cargo, ensuring safety, navigation accuracy, and compliance with aviation regulations.'
    },
    {
        'name': 'Aerospace Materials Specialist',
        'category': 'Aerospace & Aviation',
        'description': 'Develop and test aerospace materials.',
        'salary': '5 LPA (Approx)',
        'education': 'Graduate Degree',
        'skills': ['Research', 'Technical', 'Analytical'],
        'details': 'Aerospace Materials Specialists research, develop, and test materials used in aircraft and spacecraft to ensure strength, durability, and performance under extreme conditions.'
    },
    {
        'name': 'Air Traffic Controller',
        'category': 'Aerospace & Aviation',
        'description': 'Manage aircraft movements and ensure safety.',
        'salary': '5 LPA (approx)',
        'education': 'Diploma',
        'skills': ['Communication', 'Decision-Making', 'Analytical'],
        'details': 'Air Traffic Controllers coordinate aircraft movements on the ground and in the air, ensuring safe distances between planes and managing takeoffs, landings, and flight paths efficiently.'
    },
    {
        'name': 'Aircraft Maintenance Technician',
        'category': 'Aerospace & Aviation',
        'description': 'Inspect and repair aircraft systems.',
        'salary': '3-8 LPA',
        'education': 'Diploma in Aircraft Maintenance Engineering',
        'skills': ['Mechanical', 'Problem-Solving', 'Technical'],
        'details': 'Aircraft Maintenance Technicians inspect, maintain, and repair aircraft systems to ensure safety, functionality, and compliance with aviation regulations.'
    },
    {
        'name': 'Cabin Crew / Flight Attendant',
        'category': 'Aerospace & Aviation',
        'description': 'Ensure passenger safety and provide excellent in-flight customer service.',
        'salary': '3-10 LPA',
        'education': '12th Pass + Cabin Crew Training',
        'skills': ['Communication', 'Customer Service', 'Management'],
        'details': 'Cabin crew members are responsible for ensuring the safety, comfort, and well-being of passengers during flights. They handle emergencies, provide service, and maintain a positive travel experience.'
    },
    {
        'name': 'Airport Security Executive',
        'category': 'Aerospace & Aviation',
        'description': 'Oversee airport security operations and ensure safety protocols are followed.',
        'salary': '3-8 LPA',
        'education': 'High School / Diploma',
        'skills': ['Management', 'Observation', 'Decision-making'],
        'details': 'Airport Security Executives monitor and manage security operations at airports, ensuring passenger safety, screening procedures, and compliance with aviation regulations.'
    },
    {
        'name': 'Terminal Operations Manager',
        'category': 'Aerospace & Aviation',
        'description': 'Manage terminal operations efficiently, ensuring smooth coordination of airport activities and services.',
        'salary': '5-12 LPA',
        'education': 'Graduate Degree (Aviation / Management preferred)',
        'skills': ['Management', 'Coordination', 'Leadership'],
        'details': 'Terminal Operations Managers oversee daily airport terminal functions, coordinate staff and services, ensure passenger safety and satisfaction, and manage operational efficiency.'
    },
    {
        'name': 'Reservation & Ticketing Agent',
        'category': 'Aerospace & Aviation',
        'description': 'Handle bookings and ticketing for passengers, ensuring smooth travel arrangements.',
        'salary': '2-6 LPA',
        'education': '12th Pass / Diploma in Travel & Tourism',
        'skills': ['Customer Service', 'Communication', 'Organization'],
        'details': 'Reservation & Ticketing Agents manage flight bookings, cancellations, and customer queries while ensuring accurate ticketing and smooth travel coordination.'
    },
    {
        'name': 'Ramp Service Agent',
        'category': 'Aerospace & Aviation',
        'description': 'Load and unload cargo',
        'salary': '3 LPA (approx)',
        'education': 'School Level',
        'skills': ['Manual Work', 'Coordination', 'Teamwork'],
        'details': 'Ramp Service Agents handle loading and unloading of cargo, assist in aircraft ground operations, and ensure smooth coordination between ground crew and flight staff.'
    },
    {
        'name': 'Aircraft Cleaner',
        'category': 'Aerospace & Aviation',
        'description': 'Maintain aircraft interiors by ensuring cleanliness and hygiene standards.',
        'salary': '2-5 LPA',
        'education': 'School Level',
        'skills': ['Manual Work', 'Attention to Detail', 'Cleaning'],
        'details': 'Aircraft cleaners are responsible for cleaning and maintaining the interior of aircraft, including seats, floors, and cabins, ensuring a safe and hygienic environment for passengers and crew.'
    },
    {
        'name': 'Biological Scientist',
        'category': 'Agriculture & Allied Fields',
        'description': 'Research biological systems.',
        'salary': '5 LPA (approx)',
        'education': 'Doctorate',
        'skills': ['Research', 'Analytical', 'Technical'],
        'details': 'Biological scientists study living organisms and systems, conducting research to advance knowledge in areas like agriculture, medicine, and environmental science.'
    },
    {
        'name': 'Environmental Scientist',
        'category': 'Agriculture & Allied Fields',
        'description': 'Study environmental systems',
        'salary': '5 LPA (approx)',
        'education': 'Postgraduate degree',
        'skills': ['Analytical', 'Research', 'Problem-solving'],
        'details': 'Environmental scientists analyze environmental systems, conduct research, and develop solutions to environmental problems such as pollution, climate change, and resource management.'
    },
    {
        'name': 'Food Technologist',
        'category': 'Agriculture & Allied Fields',
        'description': 'Develop and test food products.',
        'salary': '5 LPA (approx)',
        'education': 'Graduate degree (Food Technology or related field)',
        'skills': ['Innovation', 'Analytical', 'Technical'],
        'details': 'Food Technologists work on developing, testing, and improving food products. They ensure quality, safety, and compliance with standards while innovating new food solutions.'
    },
    {
        'name': 'Geologist',
        'category': 'Agriculture & Allied Fields',
        'description': 'Study earth materials.',
        'salary': '5 LPA (approx)',
        'education': 'Graduate degree in Geology or related field',
        'skills': ['Fieldwork', 'Analytical Skills', 'Research'],
        'details': 'Geologists study the Earth\'s materials, structure, and processes through fieldwork and laboratory research to understand natural resources and environmental changes.'
    },
    {
        'name': 'Crop Farmer',
        'category': 'Agriculture & Allied Fields',
        'description': 'Cultivate crops for food, raw materials, and other agricultural products.',
        'salary': '2-8 LPA',
        'education': 'School Level Education',
        'skills': ['Manual Work', 'Management', 'Technical Knowledge'],
        'details': 'Crop farmers are responsible for planting, cultivating, and harvesting crops. They manage soil health, irrigation, and pest control while ensuring efficient production and sustainability.'
    },
    {
        'name': 'Gardener',
        'category': 'Agriculture & Allied Fields',
        'description': 'Maintain gardens and ensure healthy growth of plants.',
        'salary': '2-5 LPA',
        'education': 'School Level',
        'skills': ['Manual Work', 'Maintenance', 'Plant Care'],
        'details': 'Gardeners are responsible for planting, watering, pruning, and maintaining gardens, lawns, and landscapes to keep them healthy and visually appealing.'
    },
]
