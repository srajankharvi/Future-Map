// ===== Your Path Page Logic =====

// ===== Data fetched from API (initialized empty) =====
let careerCourseMapping = {};
let roadmapTemplates = {};
let careerDetailedInfo = {};
let careerProjects = {};
let careerResources = {};

// Skill icons mapping — using SVG icon system from script.js
const skillIconMap = {
    "technical": "laptop",
    "analytical": "chart",
    "creative": "palette",
    "communication": "mic",
    "leadership": "users",
    "problem-solving": "puzzle",
    "teamwork": "handshake",
    "design": "sparkles",
    "strategic planning": "building"
};

/** Get skill icon SVG — uses Icons from script.js */
function getSkillIcon(skillName) {
    const key = skillIconMap[(skillName || '').toLowerCase()] || 'star';
    return (typeof icon === 'function') ? icon(key, 18) : '';
}

/** Load all yourpath reference data from the API */
async function loadYourPathData() {
    try {
        const res = await apiFetch(`${API_BASE}/yourpath-data`);
        if (res.success && res.data) {
            careerCourseMapping = res.data.careerCourseMapping || {};
            roadmapTemplates = res.data.roadmapTemplates || {};
            careerDetailedInfo = res.data.careerDetailedInfo || {};
            careerProjects = res.data.careerProjects || {};
            careerResources = res.data.careerResources || {};
        }
    } catch (err) {
        console.error('Failed to load yourpath data:', err);
    }
}

// Populate career dropdown
function populateCareerDropdown(filteredCareers = null) {
    const select = document.getElementById('careerSelect');
    if (!select) return;
    
    const careers = filteredCareers || careerData;
    select.innerHTML = '<option value="">-- Choose a Career --</option>';
    
    careers.forEach(career => {
        const option = document.createElement('option');
        option.value = career.name;
        option.textContent = `${career.name} — ${career.category}`;
        select.appendChild(option);
    });
    
    // Re-initialize custom dropdown
    if (typeof setupCustomSelects === 'function') {
        setupCustomSelects();
    }
}

// Populate course dropdown
function populateCourseDropdown(filteredCourses = null) {
    const select = document.getElementById('courseSelect');
    if (!select) return;
    
    const courses = filteredCourses || courseData;
    select.innerHTML = '<option value="">-- Choose a Course --</option>';
    
    courses.forEach(course => {
        const option = document.createElement('option');
        option.value = course.name;
        option.textContent = `${course.name} — ${course.type} (${course.duration})`;
        select.appendChild(option);
    });
    
    // Re-initialize custom dropdown
    if (typeof setupCustomSelects === 'function') {
        setupCustomSelects();
    }
}

// Filter career dropdown by category
function filterCareerOptions() {
    const category = document.getElementById('careerCategorySelect').value;
    const filtered = category 
        ? careerData.filter(c => c.category === category || c.category.includes(category))
        : careerData;
    populateCareerDropdown(filtered);
    
    // Hide preview if selection cleared
    hideElement('careerPreview');
    checkGenerateButton();
}

// Filter course dropdown by type
function filterCourseOptions() {
    const type = document.getElementById('courseTypeSelect').value;
    const filtered = type ? courseData.filter(c => c.type === type) : courseData;
    populateCourseDropdown(filtered);
    
    hideElement('coursePreview');
    checkGenerateButton();
}

// On career selected
function onCareerSelected() {
    const careerName = document.getElementById('careerSelect').value;
    const preview = document.getElementById('careerPreview');
    
    if (!careerName) {
        hideElement(preview);
        checkGenerateButton();
        return;
    }
    
    const career = careerData.find(c => c.name === careerName);
    if (!career) return;
    
    // Determine salary string
    let salaryText = '';
    if (typeof career.salary === 'object' && career.salary !== null) {
        salaryText = career.salary.fresher || career.salary.entry_level || 'Competitive';
    } else {
        salaryText = career.salary || 'Competitive';
    }

    // Determine requirements / education string
    let eduText = '';
    if (typeof career.requirements === 'object' && career.requirements !== null) {
        eduText = career.requirements.minimum_qualification || 'Degree/Diploma';
    } else {
        eduText = career.education || 'Degree/Diploma';
    }

    document.getElementById('careerPreviewName').textContent = career.name;
    document.getElementById('careerPreviewDesc').textContent = career.description;
    document.getElementById('careerPreviewEdu').textContent = eduText;
    document.getElementById('careerPreviewSalary').textContent = salaryText;
    showElement(preview);
    
    checkGenerateButton();
}

// On course selected
function onCourseSelected() {
    const courseName = document.getElementById('courseSelect').value;
    const preview = document.getElementById('coursePreview');
    
    if (!courseName) {
        hideElement(preview);
        checkGenerateButton();
        return;
    }
    
    const course = courseData.find(c => c.name === courseName);
    if (!course) return;
    
    document.getElementById('coursePreviewName').textContent = course.name;
    document.getElementById('coursePreviewDesc').textContent = course.description;
    document.getElementById('coursePreviewDuration').textContent = `${course.duration}`;
    document.getElementById('coursePreviewType').textContent = `${course.type}`;
    showElement(preview);
    
    checkGenerateButton();
}

// Show/hide generate button
function checkGenerateButton() {
    const careerId = document.getElementById('careerSelect').value;
    const courseId = document.getElementById('courseSelect').value;
    const wrapper = document.getElementById('generatePathWrapper');
    
    if (careerId && courseId) {
        showElement(wrapper);
    } else {
        hideElement(wrapper);
    }
}

// Helper formatting tools
function renderSubjectsInline(subjectsList) {
    if (!subjectsList || !Array.isArray(subjectsList) || subjectsList.length === 0) return 'Core curriculum';
    return subjectsList.slice(0, 4).map(s => `<strong>${escapeHTML(s)}</strong>`).join(', ');
}

function renderObjectivesShort(objectives) {
    if (!objectives) return 'develop solid technical foundations and practical capabilities.';
    if (Array.isArray(objectives)) {
        return objectives.slice(0, 2).map(o => escapeHTML(o).toLowerCase()).join(' and ');
    }
    return escapeHTML(objectives).toLowerCase();
}

function renderRecruitersInline(recruiters) {
    if (!recruiters || !Array.isArray(recruiters) || recruiters.length === 0) return 'top-tier industry firms and research institutes';
    return recruiters.slice(0, 3).map(r => `<strong>${escapeHTML(r)}</strong>`).join(', ');
}

function renderHigherStudiesInline(studies) {
    if (!studies || !Array.isArray(studies) || studies.length === 0) return 'post-graduate specifications or professional certifications';
    return studies.slice(0, 3).map(s => `<strong>${escapeHTML(s)}</strong>`).join(', ');
}

// Dynamic Project Generator
function generateProjectsForCareer(career) {
    const name = career.name.toLowerCase();
    const cat = (career.category || '').toLowerCase();
    
    // Default projects if no specific match
    let projects = [
        {
            title: `Professional Portfolio Showcase`,
            description: `Design and publish an online portfolio displaying key projects, research papers, and case studies related to ${career.name}.`,
            skills: ["Communication", "Design", "Technical"],
            difficulty: "Beginner",
            timeEstimate: "1-2 weeks"
        },
        {
            title: `${career.name} Case Study Analysis`,
            description: `Conduct a detailed audit or analysis of a leading company or research paper in the field of ${career.name}, presenting optimization recommendations.`,
            skills: ["Analytical", "Problem-Solving"],
            difficulty: "Intermediate",
            timeEstimate: "2-3 weeks"
        },
        {
            title: `Industry Prototype Simulation`,
            description: `Develop a simulated solution addressing a primary operational bottleneck in ${career.name} workflows.`,
            skills: ["Technical", "Innovation"],
            difficulty: "Advanced",
            timeEstimate: "4-6 weeks"
        }
    ];

    // Specialized project templates based on career name and categories
    if (name.includes("developer") || name.includes("programmer") || name.includes("engineer") && cat.includes("computer")) {
        projects = [
            {
                title: `Full-Stack Web/App Ecosystem`,
                description: `Build a secure, responsive application with a robust REST/GraphQL API backend, relational/NoSQL database storage, and a modern frontend UI.`,
                skills: ["Software Engineering", "Database Management", "UI/UX"],
                difficulty: "Advanced",
                timeEstimate: "4-6 weeks"
            },
            {
                title: `Algorithms & Data Structures Optimization`,
                description: `Create an open-source library that implements and visualizes complex graph traversals or sorting algorithms with speed benchmarks.`,
                skills: ["Problem-Solving", "Performance Tuning"],
                difficulty: "Intermediate",
                timeEstimate: "2-3 weeks"
            },
            {
                title: `Cloud Deployment & CI/CD Pipeline`,
                description: `Containerize an application using Docker and build an automated deployment pipeline using GitHub Actions to AWS or GCP.`,
                skills: ["DevOps", "Cloud Services"],
                difficulty: "Intermediate",
                timeEstimate: "2 weeks"
            }
        ];
    } else if (name.includes("data") || name.includes("analyst") || name.includes("scientist") || name.includes("machine learning")) {
        projects = [
            {
                title: `End-to-End Machine Learning Pipeline`,
                description: `Clean a complex public dataset, engineer features, train predictive models (like XGBoost or Random Forests), and deploy the model as a Flask/FastAPI service.`,
                skills: ["Data Science", "Python", "Predictive Modeling"],
                difficulty: "Advanced",
                timeEstimate: "4-5 weeks"
            },
            {
                title: `Interactive Business Intelligence Dashboard`,
                description: `Design a comprehensive dashboard using Tableau or PowerBI that visualizes key operational metrics, trends, and forecasts for stakeholder decision making.`,
                skills: ["Data Visualization", "SQL", "Business Analytics"],
                difficulty: "Intermediate",
                timeEstimate: "2 weeks"
            },
            {
                title: `Automated Web Scraper & ETL Pipeline`,
                description: `Write a script to extract unstructured web data daily, clean it, and load it into a structured database (SQL/NoSQL) with automated cron execution.`,
                skills: ["Python", "Database design", "ETL"],
                difficulty: "Intermediate",
                timeEstimate: "2-3 weeks"
            }
        ];
    } else if (cat.includes("aerospace") || cat.includes("aviation")) {
        projects = [
            {
                title: `Airfoil Lift & Aerodynamic Simulation`,
                description: `Utilize simulation software or mathematical programming (like MATLAB/Python) to model and optimize airfoil lift/drag characteristics under different angles of attack.`,
                skills: ["Fluid Dynamics", "Math Simulation"],
                difficulty: "Advanced",
                timeEstimate: "3-4 weeks"
            },
            {
                title: `Aircraft Structural Stress Analysis`,
                description: `Perform structural design and finite element analysis (FEA) of a wing section under varying flight load factors to ensure integrity.`,
                skills: ["CAD/FEA Modeling", "Material Science"],
                difficulty: "Advanced",
                timeEstimate: "4-5 weeks"
            },
            {
                title: `Drone Flight Stabilization Controller`,
                description: `Build or simulate a flight control loop utilizing PID controller algorithms for auto-stabilizing roll, pitch, and yaw on a quadcopter.`,
                skills: ["Control Systems", "Embedded Programming"],
                difficulty: "Advanced",
                timeEstimate: "4 weeks"
            }
        ];
    } else if (cat.includes("finance") || cat.includes("banking") || cat.includes("business") || cat.includes("commerce")) {
        projects = [
            {
                title: `Financial Valuation & Modeling Report`,
                description: `Build a comprehensive Discounted Cash Flow (DCF) model and comparable company analysis (CCA) for a publicly-traded corporation to evaluate investment potential.`,
                skills: ["Financial Analysis", "Excel Modeling", "Valuation"],
                difficulty: "Advanced",
                timeEstimate: "3 weeks"
            },
            {
                title: `Personal Wealth & Portfolio Allocator`,
                description: `Develop a rule-based algorithm that takes user risk profiles and dynamically optimizes asset allocations (stocks, bonds, gold, cash) using historical yield data.`,
                skills: ["Portfolio Management", "Statistical Analysis"],
                difficulty: "Intermediate",
                timeEstimate: "2-3 weeks"
            },
            {
                title: `Market Entry Strategy Analysis`,
                description: `Write a detailed business plan outlining market entry, competitive analysis, SWOT, operational logistics, and 5-year financial projections for a new startup.`,
                skills: ["Strategic Management", "Market Research"],
                difficulty: "Intermediate",
                timeEstimate: "2-3 weeks"
            }
        ];
    } else if (cat.includes("health") || cat.includes("medical")) {
        projects = [
            {
                title: `Clinical Case Study Review & Presentation`,
                description: `Analyze medical reports of a complex clinical diagnosis, detailing etiology, pathophysiology, diagnostic protocols, and multi-modal treatment outcomes.`,
                skills: ["Medical Diagnostics", "Scientific Literature"],
                difficulty: "Intermediate",
                timeEstimate: "3 weeks"
            },
            {
                title: `Public Health Awareness Campaign`,
                description: `Create an evidence-based preventive health campaign targeting local community wellness, detailing nutritional guidelines, screening schedules, and lifestyle modifications.`,
                skills: ["Community Medicine", "Communication"],
                difficulty: "Beginner",
                timeEstimate: "2 weeks"
            },
            {
                title: `Healthcare Operations & Quality Audit`,
                description: `Perform a detailed audit on patient wait-times, resource allocation, and hygiene protocols in a simulated clinic environment, proposing leaner workflow structures.`,
                skills: ["Healthcare Management", "Quality Assurance"],
                difficulty: "Advanced",
                timeEstimate: "4 weeks"
            }
        ];
    } else if (cat.includes("art") || cat.includes("design") || name.includes("designer") || name.includes("artist")) {
        projects = [
            {
                title: `Comprehensive Brand Identity System`,
                description: `Design a cohesive brand asset suite including logos, typography, corporate style guidelines, product packaging mockups, and marketing collateral.`,
                skills: ["Visual Design", "Adobe Illustrator", "Branding"],
                difficulty: "Advanced",
                timeEstimate: "3 weeks"
            },
            {
                title: `Interactive UI/UX Mobile App Prototype`,
                description: `Research user personas, map user flows, design high-fidelity wireframes, and compile a fully interactive screen prototype using Figma or Adobe XD.`,
                skills: ["Figma Wireframing", "Interaction Design", "User Testing"],
                difficulty: "Intermediate",
                timeEstimate: "2-3 weeks"
            },
            {
                title: `Digital Art & Storyboarding Campaign`,
                description: `Create a series of high-quality digital illustrations or storyboard panels narrating a commercial story concept for marketing campaigns.`,
                skills: ["Concept Art", "Digital Painting", "Visual Storytelling"],
                difficulty: "Intermediate",
                timeEstimate: "2-3 weeks"
            }
        ];
    } else if (cat.includes("agriculture")) {
        projects = [
            {
                title: `Smart Irrigation & Soil-Moisture System`,
                description: `Build a physical prototype or simulated system connecting soil moisture sensors to an automated water pump controller using Arduino or IoT modules.`,
                skills: ["IoT Automation", "Soil Science", "Hardware Programming"],
                difficulty: "Advanced",
                timeEstimate: "4 weeks"
            },
            {
                title: `Crop Rotation & Yield Optimization Model`,
                description: `Develop a mathematical model that optimizes crop sequencing based on soil nitrogen retention, seasonal water usage, and expected market prices.`,
                skills: ["Agronomy", "Analytical Modeling"],
                difficulty: "Intermediate",
                timeEstimate: "3 weeks"
            },
            {
                title: `Organic Pest Management Case Study`,
                description: `Evaluate biological pest control methods on a selected local crop, designing a detailed pesticide-free management protocol for farmers.`,
                skills: ["Entomology", "Sustainable Agriculture"],
                difficulty: "Beginner",
                timeEstimate: "2 weeks"
            }
        ];
    } else if (cat.includes("education") || name.includes("teacher") || name.includes("educator")) {
        projects = [
            {
                title: `Interactive Lesson Plan & Syllabus Suite`,
                description: `Design a complete 4-week digital curriculum syllabus for a STEM or Humanities topic, incorporating multimedia lessons, assessment rubrics, and feedback tools.`,
                skills: ["Pedagogical Design", "Content Creation"],
                difficulty: "Intermediate",
                timeEstimate: "2 weeks"
            },
            {
                title: `Gamified E-Learning Interactive Module`,
                description: `Create a web-based educational mini-game or interactive quiz module using HTML/JS or quiz builders to increase student engagement in difficult concepts.`,
                skills: ["Educational Technology", "UX Design"],
                difficulty: "Intermediate",
                timeEstimate: "2-3 weeks"
            },
            {
                title: `Special Education Accommodation Plan`,
                description: `Formulate a comprehensive IEP (Individualized Education Program) guide outlining specific instructional adaptations and assistive technology for diverse learners.`,
                skills: ["Special Education", "Inclusive Classrooms"],
                difficulty: "Advanced",
                timeEstimate: "3 weeks"
            }
        ];
    } else if (cat.includes("engineering") || cat.includes("automobile") || name.includes("engineer")) {
        projects = [
            {
                title: `Mechanical Parts CAD & Stress Model`,
                description: `Create detailed 3D CAD parts in SolidWorks or AutoCAD, simulating thermal load distribution and mechanical stress using Finite Element Analysis.`,
                skills: ["3D CAD Modeling", "FEA Analysis"],
                difficulty: "Advanced",
                timeEstimate: "3-4 weeks"
            },
            {
                title: `Renewable Energy System Design`,
                description: `Model and calculate the size, storage capacity, and electrical grid connection requirements for a solar microgrid powering a small residential complex.`,
                skills: ["Electrical Design", "Thermodynamics"],
                difficulty: "Advanced",
                timeEstimate: "4 weeks"
            },
            {
                title: `Automotive Engine Performance Analysis`,
                description: `Analyze internal combustion engine parameters or EV motor efficiency using diagnostic metrics, plotting torque-speed curves and energy losses.`,
                skills: ["Automotive Engineering", "Data Analysis"],
                difficulty: "Intermediate",
                timeEstimate: "3 weeks"
            }
        ];
    }

    return projects;
}

// Dynamic Tools & Resources Generator
function generateResourcesForCategory(category, careerName) {
    const cat = (category || '').toLowerCase();
    const name = (careerName || '').toLowerCase();
    
    let tools = ["MS Office Suite", "Slack / Zoom (Collaboration)", "Trello / Jira (Task Management)", "Google Analytics"];
    let certifications = ["Project Management Professional (PMP)", "Google Professional Certificate", "LinkedIn Learning Pathway"];
    let subjects = ["Principles of Management", "Professional Communication", "Ethics & Sustainability", "Statistical Analysis"];

    if (cat.includes("computer") || cat.includes("it") || name.includes("developer") || name.includes("programmer")) {
        tools = ["VS Code / JetBrains IDEs", "Git & GitHub Version Control", "Docker Containerization", "AWS / Google Cloud / Azure Platforms"];
        certifications = ["AWS Certified Solutions Architect", "Google Cloud Associate Engineer", "CompTIA Security+", "Microsoft Certified Azure Fundamentals"];
        subjects = ["Data Structures & Algorithms", "Relational & NoSQL Database Design", "Computer Networks & Security", "Operating Systems Architecture"];
    } else if (cat.includes("aerospace") || cat.includes("aviation")) {
        tools = ["MATLAB & Simulink", "ANSYS Fluent (CFD)", "SolidWorks / CATIA (CAD)", "Flight Simulation Toolkits"];
        certifications = ["DGCA Aircraft Maintenance Engineer (AME) License", "FAA Remote Pilot Certification", "Aviation Safety & Management Certificate"];
        subjects = ["Aerodynamics & Fluid Mechanics", "Propulsion & Jet Engines", "Aircraft Structural Mechanics", "Flight Dynamics & Controls"];
    } else if (cat.includes("finance") || cat.includes("banking") || cat.includes("business") || cat.includes("commerce")) {
        tools = ["Advanced Microsoft Excel (VBA/Macros)", "Bloomberg Terminal / Reuters", "Tableau / Microsoft PowerBI", "QuickBooks / Tally ERP"];
        certifications = ["Chartered Financial Analyst (CFA)", "Certified Public Accountant (CPA)", "FRM (Financial Risk Manager)", "NSE Academy Certifications"];
        subjects = ["Corporate Finance & Valuation", "Security Analysis & Portfolio Management", "Financial Accounting & Reporting", "Micro & Macroeconomics"];
    } else if (cat.includes("engineering") || cat.includes("automobile")) {
        tools = ["AutoCAD / Autodesk Inventor", "SolidWorks (3D CAD Modelling)", "MATLAB & Simulink", "ANSYS / Fusion 360 FEA"];
        certifications = ["Certified Quality Engineer (CQE)", "Autodesk Certified Professional", "Six Sigma Green Belt Certification"];
        subjects = ["Strength of Materials & FEA", "Thermodynamics & Heat Transfer", "Electrical Circuits & Machines", "Fluid Mechanics & Hydraulics"];
    } else if (cat.includes("health") || cat.includes("medical")) {
        tools = ["Electronic Health Records (EHR) Systems", "Stethoscope & Sphygmomanometer", "Medical Imaging Software (DICOM)", "Bio-statistical Analysis Tools"];
        certifications = ["Basic Life Support (BLS) Certification", "Advanced Cardiac Life Support (ACLS)", "Medical Licensing Exam (e.g. FMGE/NEXT)"];
        subjects = ["Human Anatomy & Physiology", "Pathology & Microbiology", "Pharmacology & Therapeutics", "Community Medicine & Hygiene"];
    } else if (cat.includes("art") || cat.includes("design") || name.includes("designer") || name.includes("artist")) {
        tools = ["Adobe Creative Cloud (Photoshop, Illustrator, InDesign)", "Figma / Adobe XD (UI/UX design)", "Blender / Maya (3D Modeling)", "Wacom Drawing Tablets"];
        certifications = ["Adobe Certified Professional (Creative Cloud)", "Figma UI/UX Design Specialist", "Google UX Design Certificate"];
        subjects = ["Typography & Color Theory", "Human-Centered Design (UX)", "Digital Illustration & Painting", "History of Art & Visual Culture"];
    } else if (cat.includes("agriculture")) {
        tools = ["GIS Mapping Software (ArcGIS/QGIS)", "IoT Soil-Moisture & Weather Sensors", "Agricultural Drone Analysis Software", "Hydroponics / Greenhouse Systems"];
        certifications = ["Certified Crop Adviser (CCA)", "Organic Agriculture Specialist Certificate", "Drone Pilot License for Ag-mapping"];
        subjects = ["Soil Science & Nutrient Management", "Agronomy & Crop Physiology", "Agricultural Entomology & Pathology", "Sustainable Farm Management"];
    } else if (cat.includes("education") || name.includes("teacher") || name.includes("educator")) {
        tools = ["Google Classroom & Moodle LMS", "Kahoot! & Quizizz Gamification", "Canva / Microsoft PowerPoint for Education", "Zoom / Teams for Remote Learning"];
        certifications = ["State Teacher Eligibility Test (TET / NET)", "Google Certified Educator (Level 1 & 2)", "TEFL/TESOL (English Teaching Certification)"];
        subjects = ["Educational Psychology & Learning Theories", "Curriculum Design & Lesson Planning", "Classroom Management Techniques", "Inclusive Education & Special Needs"];
    }

    return { tools, certifications, subjects };
}

// Generate the roadmap
function generatePath() {
    const careerName = document.getElementById('careerSelect').value;
    const courseName = document.getElementById('courseSelect').value;
    
    const career = careerData.find(c => c.name === careerName);
    const course = courseData.find(c => c.name === courseName);
    
    if (!career || !course) return;
    
    // Normalize and clean up variables
    const skillsList = career.skills_gained || career.skills || [];
    const categoryName = career.category || "General";
    const growthOutlook = career.industry_demand ? `${career.industry_demand} Demand` : 'High growth potential in modern industry';
    
    // Determine salary ranges
    let salaryText = '';
    let entrySalary = '';
    let experiencedSalary = '';
    if (typeof career.salary === 'object' && career.salary !== null) {
        entrySalary = career.salary.entry_level || career.salary.fresher || 'Competitive';
        experiencedSalary = career.salary.experienced || career.salary.mid_level || 'Premium';
        salaryText = `${entrySalary} - ${experiencedSalary}`;
    } else {
        salaryText = career.salary || 'Competitive';
        entrySalary = salaryText;
        experiencedSalary = 'Experienced Scale';
    }

    // Determine requirements / education
    let requirementsText = '';
    if (typeof career.requirements === 'object' && career.requirements !== null) {
        requirementsText = career.requirements.minimum_qualification || 'Degree/Diploma';
    } else {
        requirementsText = career.education || 'Degree/Diploma';
    }

    // 1. STITCH COMPREHENSIVE ROADMAP TIMELINE
    const steps = [
        {
            step: "Phase 1",
            title: `Academic Foundation & Enrollment`,
            desc: `Enroll in <strong>${escapeHTML(course.name)}</strong> (duration: ${escapeHTML(course.duration)}). Focus on meeting the entry requirements: ${typeof course.requirements === 'object' ? escapeHTML(course.requirements.minimum_qualification || '10+2') : escapeHTML(course.requirements || '10+2')}. Keep in mind the average fees structure: Government: ${escapeHTML(course.fees?.government_college || 'Moderate')} / Private: ${escapeHTML(course.fees?.private_college || 'Varies')}.`,
            duration: "Year 1"
        },
        {
            step: "Phase 2",
            title: `Core Coursework & Concepts`,
            desc: `Master the foundational curriculum of ${escapeHTML(course.name)}. Prioritize core subjects such as: ${renderSubjectsInline(course.subjects || career.subjects)}. Focus on the course objectives: ${renderObjectivesShort(course.course_objectives || career.course_objectives)}.`,
            duration: "Year 1-2"
        },
        {
            step: "Phase 3",
            title: `Advanced Skill Acquisition`,
            desc: `Bridge the academic-industry gap by mastering these key skills required for <strong>${escapeHTML(career.name)}</strong>: ${skillsList.slice(0, 5).map(s => `<span class="skill-mini-tag">${escapeHTML(s)}</span>`).join(' ')}. Utilize tools like: ${generateResourcesForCategory(categoryName, career.name).tools.slice(0, 2).map(t => `<strong>${escapeHTML(t)}</strong>`).join(', ')}.`,
            duration: "Year 2-3"
        },
        {
            step: "Phase 4",
            title: `Practical Projects & Portfolio`,
            desc: `Apply your knowledge by building domain-specific projects. We recommend creating an industry-focused prototype to showcase in your professional portfolio.`,
            duration: "Year 3"
        },
        {
            step: "Phase 5",
            title: `Internship & Placement Preparation`,
            desc: `Secure an internship to gain real-world exposure. Target top recruiters like: ${renderRecruitersInline(career.top_recruiters || course.top_recruiters)}. Prepare for placements with a placement rate of ${escapeHTML(career.placement_rate || '85%')}.`,
            duration: "Final Year"
        },
        {
            step: "Phase 6",
            title: `Career Entry & Job Roles`,
            desc: `Transition into the workforce as a professional. You will target job roles such as: ${(career.job_roles || career.career_options || ['Domain Associate', 'Specialist']).slice(0, 4).map(role => `<strong>${escapeHTML(role)}</strong>`).join(', ')}. Expect an entry-level salary of: <strong>${escapeHTML(entrySalary)}</strong>.`,
            duration: "Post Graduation"
        },
        {
            step: "Phase 7",
            title: `Professional Growth & Specialization`,
            desc: `Aim for long-term career advancement. Specialize further or pursue higher studies like: ${renderHigherStudiesInline(career.higher_studies || course.higher_studies)}. Scale your career to experienced levels with potential salaries up to <strong>${escapeHTML(experiencedSalary)}</strong>.`,
            duration: "1-5 Years Exp"
        }
    ];

    // Update header
    document.getElementById('roadmapTitle').textContent = `Your Path to ${career.name}`;
    document.getElementById('roadmapSubtitle').textContent = 
        `Through ${course.name} (${course.description}) — here's your step-by-step roadmap`;
    
    // Generate summary cards
    const summaryHtml = `
        <div class="summary-card">
            <div class="summary-icon">${icon('target', 24)}</div>
            <h4>Career Goal</h4>
            <div class="summary-value">${escapeHTML(career.name)}</div>
        </div>
        <div class="summary-card">
            <div class="summary-icon">${icon('book', 24)}</div>
            <h4>Course</h4>
            <div class="summary-value">${escapeHTML(course.name)}</div>
        </div>
        <div class="summary-card">
            <div class="summary-icon">${icon('clock', 24)}</div>
            <h4>Course Duration</h4>
            <div class="summary-value">${escapeHTML(course.duration)}</div>
        </div>
        <div class="summary-card">
            <div class="summary-icon">${icon('dollar', 24)}</div>
            <h4>Salary Potential</h4>
            <div class="summary-value">${escapeHTML(salaryText)}</div>
        </div>
    `;
    document.getElementById('roadmapSummary').innerHTML = summaryHtml;
    
    // Generate timeline
    const timelineHtml = steps.map((item, index) => `
        <div class="timeline-item">
            <div class="timeline-dot step-${(index % 7) + 1}">${index + 1}</div>
            <div class="timeline-card" style="border-left-color: ${getStepColor(index)}">
                <span class="timeline-step-label">${item.step} — ${item.duration}</span>
                <h3>${item.title}</h3>
                <p>${item.desc}</p>
            </div>
        </div>
    `).join('');
    document.getElementById('roadmapTimeline').innerHTML = timelineHtml;
    
    // Generate skills section with descriptions
    const allSkills = [...new Set(skillsList)];
    const skillsHtml = `
        <h3>${icon('wrench', 22)} Skills You'll Need</h3>
        <p class="skills-subtitle">Focus on developing these key skills along your journey</p>
        <div class="skills-grid-path">
            ${allSkills.map(skill => `
                <div class="skill-chip">
                    <div class="skill-chip-icon">${getSkillIcon(skill)}</div>
                    <span class="skill-chip-text">${escapeHTML(skill)}</span>
                </div>
            `).join('')}
        </div>
    `;
    document.getElementById('roadmapSkills').innerHTML = skillsHtml;
    
    // Generate Dynamic Skill Breakdown
    const colors = ["#3d6b6e", "#5a8f8a", "#2b5b63", "#4a7d86", "#3d6b6e"];
    const icons = ["laptop", "puzzle", "chart", "wrench", "mic", "sparkles", "users", "handshake"];
    const levels = ["Expert", "Advanced", "Intermediate", "Intermediate", "Basic"];
    const percentages = [90, 80, 75, 70, 60];
    
    const skillBreakdown = allSkills.slice(0, 5).map((skill, index) => {
        return {
            name: skill,
            icon: icons[index % icons.length],
            level: levels[index % levels.length],
            percentage: percentages[index % percentages.length],
            color: colors[index % colors.length],
            description: `Required competency in ${skill} for daily ${career.name} operations.`
        };
    });

    const careerDetailsHtml = `
        <div class="detail-block">
            <div class="detail-block-header">
                <span class="detail-block-icon">${icon('clipboard', 22)}</span>
                <h3>Career Details — ${escapeHTML(career.name)}</h3>
            </div>
            <div class="detail-block-body">
                <p class="detail-overview">${escapeHTML(career.details || career.description)}</p>
                
                <div class="detail-grid">
                    <div class="detail-item">
                        <div class="detail-item-icon">${icon('graduationCap', 20)}</div>
                        <div>
                            <h4>Education Required</h4>
                            <p>${escapeHTML(requirementsText)}</p>
                        </div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-item-icon">${icon('dollar', 20)}</div>
                        <div>
                            <h4>Entry Level Salary</h4>
                            <p>${escapeHTML(entrySalary)}</p>
                        </div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-item-icon">${icon('folder', 20)}</div>
                        <div>
                            <h4>Industry / Category</h4>
                            <p>${escapeHTML(categoryName)}</p>
                        </div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-item-icon">${icon('trendingUp', 20)}</div>
                        <div>
                            <h4>Growth Outlook</h4>
                            <p>${escapeHTML(growthOutlook)}</p>
                        </div>
                    </div>
                </div>

                <div class="skill-breakdown">
                    <h4>${icon('target', 18)} Skills Breakdown — What to Learn</h4>
                    <div class="skill-breakdown-list">
                        ${skillBreakdown.map(s => `
                            <div class="skill-breakdown-item">
                                <div class="skill-breakdown-header">
                                    <span class="sbi-icon">${icon(s.icon, 18)}</span>
                                    <span class="sbi-name">${escapeHTML(s.name)}</span>
                                    <span class="sbi-level">${escapeHTML(s.level)}</span>
                                </div>
                                <p class="sbi-desc">${escapeHTML(s.description)}</p>
                                <div class="sbi-bar-bg"><div class="sbi-bar-fill" style="width: ${Number(s.percentage) || 0}%; background: ${escapeHTML(s.color)}"></div></div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
    document.getElementById('careerDetailsSection').innerHTML = careerDetailsHtml;
    
    // Generate Projects Section dynamically
    const projectsData = generateProjectsForCareer(career);
    const projectsHtml = `
        <div class="detail-block">
            <div class="detail-block-header">
                <span class="detail-block-icon">${icon('rocket', 22)}</span>
                <h3>Recommended Projects to Build</h3>
            </div>
            <div class="detail-block-body">
                <p class="detail-overview">Working on real-world projects is the best way to develop skills and build your professional portfolio. Here are project ideas for your career path:</p>
                <div class="projects-grid">
                    ${projectsData.map((project, i) => `
                        <div class="project-card" style="animation-delay: ${i * 0.1}s">
                            <div class="project-card-top">
                                <span class="project-number">${i + 1}</span>
                                <span class="project-difficulty ${String(project.difficulty).toLowerCase().replace(/[^a-z0-9_-]/g, '')}">${escapeHTML(project.difficulty)}</span>
                            </div>
                            <h4 class="project-title">${escapeHTML(project.title)}</h4>
                            <p class="project-desc">${escapeHTML(project.description)}</p>
                            <div class="project-skills">
                                ${project.skills.map(s => `<span class="project-skill-tag">${escapeHTML(s)}</span>`).join('')}
                            </div>
                            <div class="project-time">
                                <span>${icon('clock', 14)}</span> ${escapeHTML(project.timeEstimate)}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    document.getElementById('projectsSection').innerHTML = projectsHtml;
    
    // Generate Resources Section dynamically
    const resourceData = generateResourcesForCategory(categoryName, career.name);
    const resourcesHtml = `
        <div class="detail-block">
            <div class="detail-block-header">
                <span class="detail-block-icon">${icon('bookOpen', 22)}</span>
                <h3>Tools & Resources to Master</h3>
            </div>
            <div class="detail-block-body">
                <div class="resources-grid">
                    <div class="resource-column">
                        <h4>${icon('wrench', 18)} Tools & Software</h4>
                        <ul class="detail-list">
                            ${resourceData.tools.map(t => `<li>${escapeHTML(t)}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="resource-column">
                        <h4>${icon('award', 18)} Certifications</h4>
                        <ul class="detail-list">
                            ${resourceData.certifications.map(c => `<li>${escapeHTML(c)}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="resource-column">
                        <h4>${icon('book', 18)} Subjects to Study</h4>
                        <ul class="detail-list">
                            ${resourceData.subjects.map(s => `<li>${escapeHTML(s)}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.getElementById('resourcesSection').innerHTML = resourcesHtml;
    
    // Show roadmap and scroll to it
    showElement('roadmapSection');
    setTimeout(() => {
        document.getElementById('roadmapSection').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 150);

    // Auto-save the roadmap
    saveRoadmapToServer(career, course);
}

function getStepColor(index) {
    const colors = ['#3d6b6e', '#5a8f8a', '#2b5b63', '#4a7d86', '#3d6b6e', '#5a8f8a', '#4a7d86'];
    return colors[index % colors.length];
}

// Reset path
function resetPath() {
    document.getElementById('careerSelect').value = '';
    document.getElementById('courseSelect').value = '';
    document.getElementById('careerCategorySelect').value = '';
    document.getElementById('courseTypeSelect').value = '';
    hideElement('careerPreview');
    hideElement('coursePreview');
    hideElement('generatePathWrapper');
    hideElement('roadmapSection');
    
    populateCareerDropdown();
    populateCourseDropdown();
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ===== Roadmap Persistence =====

/** Save the current roadmap to the server */
async function saveRoadmapToServer(career, course) {
    try {
        const result = await apiFetch(`${API_BASE}/roadmaps`, {
            method: 'POST',
            body: JSON.stringify({
                career_name: career.name,
                course_name: course.name,
                category: career.category,
                roadmap_data: {
                    career: career,
                    course: course,
                    generated_at: new Date().toISOString()
                }
            })
        });

        if (result.success) {
            showSaveNotification('Roadmap saved to your account!');
        }
    } catch (err) {
        // Silent fail — roadmap still visible, just not persisted
    }
}

/** Load saved roadmaps list */
async function loadSavedRoadmaps() {
    const container = document.getElementById('savedRoadmapsList');
    if (!container) return;

    try {
        const result = await apiFetch(`${API_BASE}/roadmaps`);
        if (result.success && result.data && result.data.length > 0) {
            container.innerHTML = result.data.map(r => `
                <div class="saved-roadmap-item" data-career="${escapeHTML(r.career_name)}" data-course="${escapeHTML(r.course_name)}">
                    <div class="saved-roadmap-info">
                        <strong>${escapeHTML(r.career_name)}</strong>
                        <span>via ${escapeHTML(r.course_name)}</span>
                    </div>
                    <div class="saved-roadmap-date">${new Date(r.updated_at).toLocaleDateString()}</div>
                    <button class="saved-roadmap-delete" data-roadmap-id="${escapeHTML(r._id)}" title="Delete">${icon('xCircle', 16)}</button>
                </div>
            `).join('');

            // Attach event listeners (no inline handlers)
            container.querySelectorAll('.saved-roadmap-item').forEach(item => {
                item.addEventListener('click', () => {
                    loadSavedRoadmap(item.dataset.career, item.dataset.course);
                });
            });
            container.querySelectorAll('.saved-roadmap-delete').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    deleteSavedRoadmap(btn.dataset.roadmapId);
                });
            });

            showElement(container.parentElement);
        } else {
            container.innerHTML = '<p class="text-muted-padded">No saved roadmaps yet. Generate one above!</p>';
        }
    } catch (err) {
        // Silent fail
    }
}

/** Load a saved roadmap by re-selecting the career and course */
function loadSavedRoadmap(careerName, courseName) {
    const careerSelect = document.getElementById('careerSelect');
    const courseSelect = document.getElementById('courseSelect');
    if (!careerSelect || !courseSelect) return;

    careerSelect.value = careerName;
    onCareerSelected();
    courseSelect.value = courseName;
    onCourseSelected();

    setTimeout(() => generatePath(), 300);
}

/** Delete a saved roadmap */
async function deleteSavedRoadmap(roadmapId) {
    try {
        const result = await apiFetch(`${API_BASE}/roadmaps/${roadmapId}`, { method: 'DELETE' });
        if (result.success) {
            loadSavedRoadmaps(); // Refresh list
        }
    } catch (err) {
        // Silent fail
    }
}

/** Show a brief save notification */
function showSaveNotification(message) {
    let notif = document.getElementById('roadmapSaveNotif');
    if (!notif) {
        notif = document.createElement('div');
        notif.id = 'roadmapSaveNotif';
        notif.className = 'save-notification hidden';
        document.body.appendChild(notif);
    }
    notif.innerHTML = `${icon('checkCircle', 16)} <span class="notif-icon-gap">${escapeHTML(message)}</span>`;
    notif.classList.remove('hidden');
    notif.classList.add('visible');
    setTimeout(() => { notif.classList.remove('visible'); }, 3000);
    setTimeout(() => { notif.classList.add('hidden'); }, 3400);
}

// Populate career category select dropdown dynamically
function populateCareerCategoryFilter() {
    const select = document.getElementById('careerCategorySelect');
    if (!select) return;
    
    const categories = [...new Set(careerData.map(c => c.category).filter(Boolean))].sort();
    select.innerHTML = '<option value="">All Categories</option>';
    categories.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat;
        option.textContent = cat;
        select.appendChild(option);
    });
}

// Populate course type select dropdown dynamically
function populateCourseTypeFilter() {
    const select = document.getElementById('courseTypeSelect');
    if (!select) return;
    
    const types = [...new Set(courseData.map(c => c.type).filter(Boolean))].sort();
    select.innerHTML = '<option value="">All Types</option>';
    types.forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = type.charAt(0) + type.slice(1).toLowerCase() + ' Programs';
        select.appendChild(option);
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async function() {
    if (document.getElementById('careerSelect')) {
        // Load yourpath reference data from API first
        await loadYourPathData();

        const initDropdowns = () => {
            populateCareerCategoryFilter();
            populateCourseTypeFilter();
            populateCareerDropdown();
            populateCourseDropdown();
            // Load saved roadmaps if container exists
            loadSavedRoadmaps();
        };

        if (careerData && careerData.length > 0) {
            initDropdowns();
        } else {
            document.addEventListener('app:data-loaded', initDropdowns, { once: true });
        }
    }

    // Setup select change listeners
    const careerCategorySelect = document.getElementById('careerCategorySelect');
    if (careerCategorySelect) {
        careerCategorySelect.addEventListener('change', filterCareerOptions);
    }

    const careerSelect = document.getElementById('careerSelect');
    if (careerSelect) {
        careerSelect.addEventListener('change', onCareerSelected);
    }

    const courseTypeSelect = document.getElementById('courseTypeSelect');
    if (courseTypeSelect) {
        courseTypeSelect.addEventListener('change', filterCourseOptions);
    }

    const courseSelect = document.getElementById('courseSelect');
    if (courseSelect) {
        courseSelect.addEventListener('change', onCourseSelected);
    }

    // Setup button listeners
    const generatePathBtn = document.querySelector('[data-action="generate-path"]');
    if (generatePathBtn) {
        generatePathBtn.addEventListener('click', generatePath);
    }

    const resetPathBtn = document.querySelector('[data-action="reset-path"]');
    if (resetPathBtn) {
        resetPathBtn.addEventListener('click', resetPath);
    }
});
