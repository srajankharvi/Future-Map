# Future Map - Career & Course Guidance System

## Overview
Future Map is a modern, AI-powered career and educational guidance website designed to help students discover their perfect career path and suitable educational programs based on their skills and academic performance.

## 🔐 Security Notice
⚠️ **Important**: The `.env` file contains sensitive credentials (API keys, database passwords) and is **NOT** committed to GitHub. Create your own `.env` file locally with your credentials.

## ⚙️ Setup & Installation

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd "Future ORG"
```

### 2. Create `.env` Configuration File
Create a `.env` file in the project root with your credentials:
```env
MONGODB_URL=mongodb+srv://your_username:your_password@your_cluster.mongodb.net/?appName=YourApp
DATABASE_NAME=future_map
FLASK_PORT=5000
FLASK_DEBUG=False
FLASK_ENV=production
SECRET_KEY=your_secret_key_here_min_10_chars
GEMINI_API_KEY=your_gemini_api_key_here
```

**Get your values from:**
- **MONGODB_URL**: [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) → Connect
- **SECRET_KEY**: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- **GEMINI_API_KEY**: [Google AI Studio](https://aistudio.google.com/app/apikey)

### 3. Install Dependencies
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 4. Run Application
```bash
python app.py
```
Visit `http://127.0.0.1:5000`

## Files Structure
- **index.html** - Main home page with career overview, career sections, courses, and interview preparation
- **recommendation.html** - Dedicated recommendation assessment page
- **styles.css** - Complete styling for all pages with responsive design
- **script.js** - JavaScript logic for recommendations, filtering, and interactions

## Features

### 1. **Home Page (index.html)**
- Hero section with welcoming message
- **Student Career & Course Recommendation Overview**
  - AI-Powered Analysis explanation
  - Personalized Matches description
  - Career Planning information
  - How It Works (4-step process)
  - What You'll Get (benefits listing)
  - Assessment Factors breakdown
- Career Options section with search and filter
- Educational Programs section with search and filter
- Interview Preparation section by category
- Responsive footer with credit

### 2. **Recommendation Page (recommendation.html)**
- Professional page header
- Introduction cards highlighting key features
- **Comprehensive Assessment Form**
  - Student name input (optional)
  - Academic marks slider with visual percentage display (0-100)
  - 8 skill selection options with descriptions:
    - Analytical (📈 Data analysis & reasoning)
    - Creative (🎨 Design & innovation)
    - Technical (💻 Technology & coding)
    - Communication (🗣️ Speaking & writing)
    - Leadership (👥 Team management)
    - Problem-Solving (🧩 Critical thinking)
    - Teamwork (🤝 Collaboration)
    - Design (✨ Visual creation)
- Smart matching algorithm
- Results display with match scores
- Tabbed interface for careers and courses
- Material Design inspired UI

### 3. **Career Data**
21 careers across categories:
- Computer & IT (Software Developer, Data Scientist, Web Developer)
- Engineering (Mechanical, Civil, Electrical Engineers)
- Healthcare (Doctors, Nurses, Pharmacists)
- Arts & Design (Graphic Designer, UI/UX Designer)
- Business & Finance (Financial Analyst, Manager, Accountant)
- Education (Teachers, Professors)

Each career includes:
- Overview and responsibilities
- Required skills (mapped to input skills)
- Education requirements
- Salary ranges
- Career prospects

### 4. **Course Data**
20 educational programs:
- **Degree Programs**: B Tech, B Sc, B Com, BA, B Arch, BCA, BBA 
- **Medical Programs**: MBBS, B Sc Nursing, B Pharma, BDS, Pharm D
- **Professional Programs**: MBA, B Ed, LLB, CA, BBA
- **Technical Programs**: BCA, MCA, M Tech, Diplomas

Each course includes:
- Full description
- Duration
- Admission requirements
- Career scope
- Program type and category

### 5. **Interview Questions**
Categorized interview questions for:
- Computer & IT (5 questions)
- Healthcare (5 questions)
- Engineering (5 questions)
- Business & Finance (5 questions)
- Design (5 questions)
- Education (5 questions)

Each question includes helpful tips for answering.

### 6. **Smart Matching Algorithm**
The recommendation system calculates match scores based on:
- **Academic Marks** (50% weight): 0-100 range converted to 0-50 points
- **Selected Skills** (50% weight): Each skill worth points

The formula: `Score = (Marks ÷ 2) + (Skills Count × 6.25)`
Maximum possible score: 100%

## How to Use

### On Home Page:
1. View overview of the recommendation system
2. Understand how the AI matching works
3. Click "Start Career Assessment" to go to recommendation page
4. Explore careers and courses in dedicated sections
5. Practice with interview questions

### On Recommendation Page:
1. Enter your name (optional)
2. Set your academic marks using the slider
3. Select your key skills (minimum 1 skill required)
4. Click "Get My Recommendations"
5. View top 5 matching careers and courses with match percentages
6. Click on any career or course for detailed information
7. Use "Modify Profile" to adjust and regenerate recommendations

## Design Features
- **Modern Gradient UI**: Purple, pink, and blue color schemes
- **Responsive Design**: Works on mobile, tablet, and desktop
- **Smooth Animations**: Transitions and effects throughout
- **Professional Layout**: Clean, organized, and user-friendly
- **Accessibility**: Clear labels, proper contrast, semantic HTML
- **Interactive Elements**: Modals, tabs, filters, and search

## Technical Details
- **HTML5**: Semantic structure
- **CSS3**: Flexbox, Grid, animations, gradients
- **Vanilla JavaScript**: No external dependencies
- **Fully Responsive**: Mobile-first approach
- **Performance**: Optimized for fast loading

## Color Scheme
- Primary: #6366f1 (Indigo)
- Secondary: #ec4899 (Pink)
- Accent: #f59e0b (Amber)
- Light Background: #f8fafc
- Dark Text: #1e293b

## Footer Credit
"Designed by I BCA - AI & ML (Artificial Intelligence)"

This indicates the project was created by the AI stream of I BCA program.

## Browser Compatibility
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Future Enhancements
- Database integration for more careers and courses
- User authentication for saving recommendations
- PDF export of recommendations
- Comparative analysis between options
- Industry trends and salary data
- Mentor connection feature
- Job postings integration
