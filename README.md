# Future Map — Career & Course Guidance System

Future Map is a full-stack web application that helps students discover their ideal career path and educational programs based on their skills, academic performance, and education level. It features AI-powered interview preparation, personalized roadmaps, and a smart recommendation engine.

---

## Features

### 🎯 Career & Course Recommendation
- Select your education level (SSLC, PUC, Diploma, Degree, Masters)
- Set your academic marks using an interactive slider
- Choose from 8 skill categories — Analytical, Creative, Technical, Communication, Leadership, Problem-Solving, Teamwork, and Design
- Receive top 5 career and course recommendations with match scores
- Click any result to view detailed information

### 💼 Career Explorer
- Browse 100+ careers across multiple categories
- Categories include Computer & IT, Engineering, Healthcare, Aerospace & Aviation, Agriculture, Business & Finance, Arts, Education, and more
- Search and filter careers by category
- View detailed career info — salary range, education required, and key responsibilities

### 📚 Course Explorer
- Explore 35+ educational programs
- Filter by type — Degree, Medical, Professional, and Technical
- View course details — duration, admission requirements, career scope

### 🗺️ Your Path (Roadmap Generator)
- Select a career and course combination
- Get a personalized step-by-step learning roadmap
- Access curated resources, projects, and skill development guides
- Save and manage multiple roadmaps

### 🎤 AI Mock Interview
- AI-powered interview question generator using Google Gemini
- Select a specific career category for targeted questions
- Choose difficulty level — Easy, Medium, or Hard
- Get detailed feedback and evaluation on your answers
- Full interview session management with chat history

### 👤 User Authentication
- Secure registration and login system
- Session-based authentication with cookie security
- User profile management — name, bio, birthday, avatar, status
- Rate-limited login (5 attempts/min) and registration (10 attempts/min)

### 📂 Projects
- Add and showcase personal projects
- Track project links and descriptions
- Synced to MongoDB for persistence

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Backend** | Python, Flask 2.3 |
| **Databases** | MongoDB Atlas |
| **AI** | Google Gemini API (interview generation) |
| **Deployment** | Vercel (serverless Python) |
| **Security** | Werkzeug password hashing, CSRF protection, XSS escaping, rate limiting |

---

## Project Structure

```
Future Map/
├── main.py                  # Flask app entry point
├── config.py                # Environment variables & app config
├── database.py              # MongoDB Atlas connection
├── extensions.py            # Flask extensions (rate limiter)
├── errors.py                # Global error handlers
├── utils.py                 # Utility functions & decorators
├── requirements.txt         # Python dependencies
├── vercel.json              # Vercel deployment config
│
├── routes/
│   ├── __init__.py           # Blueprint registration
│   ├── auth.py               # Login, register, logout, profile
│   ├── careers.py            # Careers API
│   ├── courses.py            # Courses API
│   ├── recommendations.py    # Recommendation engine API
│   ├── roadmaps.py           # Save/load user roadmaps
│   ├── yourpath.py           # Roadmap template data
│   ├── interview.py          # AI interview generation
│   ├── projects.py           # User projects CRUD
│   ├── search.py             # Search API
│   └── static.py             # Static file serving
│
├── services/
│   ├── recommendations.py    # Scoring algorithm
│   └── gemini_client.py      # Google Gemini AI client
│
├── data/
│   ├── careers.py            # Fallback career data
│   ├── courses.py            # Fallback course data
│   ├── interview.py          # Fallback interview questions
│   └── yourpath.py           # Fallback roadmap templates
│
└── frontend/
    ├── index.html             # Home / dashboard
    ├── login.html             # Login & registration
    ├── recommendation.html    # Career & course recommendations
    ├── careers.html           # Career explorer
    ├── courses.html           # Course explorer
    ├── yourpath.html          # Roadmap generator
    ├── interview.html         # AI mock interview
    ├── projects.html          # User projects
    ├── account.html           # Profile management
    ├── css/style.css          # Global styles
    └── js/
        ├── main.js            # Shared utilities, auth guard, API helper
        ├── login.js           # Auth forms logic
        ├── recommendation.js  # Recommendation page logic
        ├── careers.js         # Career explorer logic
        ├── courses.js         # Course explorer logic
        ├── yourpath.js        # Roadmap generator logic
        ├── interview.js       # AI interview logic
        ├── projects.js        # Projects page logic
        └── account.js         # Profile page logic
```

---

## Setup & Installation

### Prerequisites
- Python 3.9+
- MongoDB Atlas account (free tier works)
- Google Gemini API key (for AI interview features)

### 1. Clone the Repository
```bash
git clone https://github.com/srajankharvi/Future-Map.git
cd Future-Map
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root and add the required configuration variables (Database URLs, API Keys, etc.).


### 5. Run the Application
```bash
python main.py
```
Open your browser and go to **http://127.0.0.1:5000**

---

## Deploying to Vercel

### 1. Push Code to GitHub
Make sure `vercel.json` is in the project root (already included).

### 2. Import Project on Vercel
Go to [vercel.com](https://vercel.com), import your GitHub repository.

### 3. Set Environment Variables
Add the required environment variables in the Vercel Dashboard under **Settings → Environment Variables**.

### 4. Deploy
Vercel will automatically build and deploy your application.

> **Note:** All application data, including user accounts, profiles, roadmaps, and projects, is stored in MongoDB Atlas for persistence across serverless cold starts.


---

## Recommendation Algorithm

The system scores careers and courses based on three factors:

1. **Skill Matching (up to 60 points)** — Each selected skill maps to relevant careers/courses
2. **Academic Performance (-20 to +30 points)** — Marks-based scoring with granular tiers
3. **Education Level Bonus (+10 points)** — Careers suitable for the user's education level get a bonus

**Score thresholds:**
- Marks below 30 → No recommendations returned
- Careers need a score above 20 to be shown
- Courses need a score above 15 to be shown
- Top 5 results returned for each, sorted by score

---

## Design

- **Theme:** Dark mode with purple/blue gradient accents
- **Typography:** Clean, modern font stack
- **Layout:** Fully responsive — mobile, tablet, and desktop
- **UI Elements:** Cards, modals, tabs, search filters, sliders
- **Animations:** Smooth transitions and hover effects

---

## Browser Support

- Google Chrome (latest)
- Mozilla Firefox (latest)
- Microsoft Edge (latest)
- Safari (latest)

---

## Credits

Designed by **I BCA — AI & ML (Artificial Intelligence)**

© 2026 Future Map
