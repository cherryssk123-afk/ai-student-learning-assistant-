# AI-Powered Student Learning Assistant for Higher Education

> **MSc Dissertation Project — Coventry University**  
> **Tagline:** *Learn Smarter. Not Harder.*  
> **Theme:** Dark Emerald Green (`#064E3B`), Obsidian Charcoal (`#0F172A`), Gold Accents (`#F59E0B`), Modern Glassmorphism UI  

---

## 🎓 Overview

University students often waste significant time navigating fragmented academic resources across Google, YouTube, university LMS portals, lecture PDFs, and external websites before locating structured study material. 

The **AI-Powered Student Learning Assistant** addresses this core problem by providing higher education students with a single, intelligent SaaS platform. Rather than functioning as a generic AI chatbot, the platform provides **guided learning pathways** from beginner to advanced mastery tailored to university degree programs.

---

## 🛠️ Technology Stack

- **Frontend:** HTML5, CSS3 (Vanilla Glassmorphism Design System), Bootstrap 5, JavaScript (AJAX & Markdown Engine), Bootstrap Icons
- **Backend:** Python Flask (Application Factory Pattern, Blueprints, Modular Architecture)
- **Database:** SQLite (SQLAlchemy ORM with Flask-SQLAlchemy)
- **AI Integration:** OpenAI API (with built-in Smart AI Engine fallback for 100% offline out-of-the-box operation)
- **Authentication:** Flask-Login session management with Werkzeug password hashing
- **Security:** CSRF protection (Flask-WTF), `.env` environment isolation, input validation
- **Research Evaluation:** System Usability Scale (SUS) 10-item empirical survey engine

---

## 🌟 Key Application Features

1. **High-Impact Landing Page**
   - Modern glassmorphism hero banner with live pathway preview
   - Coventry University MSc dissertation project description & problem statement
   - Feature grid, student testimonials, FAQs, and authentication modals/pages

2. **Secure Authentication & Session Management**
   - Student Registration & Login with password hashing (`pbkdf2:sha256`)
   - Remember Me functionality, session security controls, and CSRF protection

3. **Guided Learning Roadmap Generator (Main Feature)**
   - Interactive wizard: "What do you want to learn?" (e.g. Machine Learning, Cyber Security)
   - Custom parameters: Current Level (Beginner / Intermediate / Advanced), Purpose (Exam / Assignment / Skill), Available Study Hours
   - Dynamic week-by-week progress timeline cards with interactive task check-offs and real-time database progress calculation

4. **AI Academic Tutor**
   - Interactive chat interface maintaining session conversation history
   - Modern chat UI with typing indicator animation, code formatting, and markdown rendering
   - System prompt tailored for higher education conceptual explanations

5. **Notes Summariser & Flashcard Generator**
   - Converts raw lecture transcripts and reading notes into Executive Takeaways, Core Concepts, and Active Recall Flashcards
   - One-click Copy to Clipboard and TXT file download features

6. **Smart Study Planner**
   - Distributes available weekly study hours across degree modules
   - Generates daily Pomodoro study schedules (50min study / 10min break)

7. **Academic Assignment Guidance Scaffolder**
   - **Academic Integrity Protected:** Scaffolds structural paper outlines (Introduction, Literature Review, Methodology, Analysis, Conclusion), research questions, and IEEE/APA referencing guides
   - Refrains from ghostwriting to preserve university honor codes

8. **Exam Preparation & Revision Engine**
   - Priority revision checklists, high-yield concept definitions, and active recall practice questions with toggleable answer outlines

9. **Curated Academic Resource Finder**
   - Curated textbooks, peer-reviewed publications, video lectures (MIT OCW), official documentation, and library portal links

10. **System Usability Scale (SUS) Research Survey**
    - Standard 10-question SUS Likert survey (1 to 5)
    - Automated SUS Score calculation ($0$ to $100$ scale) based on standard ISO 9241-11 criteria:
      $$\text{SUS Score} = \left( \sum (Q_{\text{odd}} - 1) + \sum (5 - Q_{\text{even}}) \right) \times 2.5$$
    - Automated SUS Grade interpretation (Grade A Excellent to Grade F) stored in SQLite for academic evaluation

11. **Student Profile & Gamified Analytics**
    - Student degree details, unlocked academic achievement badges (e.g., *Pathway Pioneer*, *Mastery Achieved*, *Inquisitive Scholar*), and full learning activity history log

---

## 📁 Project Directory Structure

```
anti gravity/
├── app/
│   ├── __init__.py           # Flask app factory, extension init (DB, Auth, CSRF)
│   ├── config.py             # App configurations & SQLite settings
│   ├── models.py             # SQLAlchemy models (User, LearningRoadmap, RoadmapWeek, StudyPlan, TutorChat, Feedback, LearningHistory, Achievement)
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── ai_service.py     # OpenAI API integration + Contextual AI Fallback Engine
│   │   └── helpers.py        # SUS score computer, badge evaluator, activity logger
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py           # Index, Dashboard, Profile
│   │   ├── auth.py           # Register, Login, Logout
│   │   ├── roadmap.py        # Guided Learning Roadmap generator & timeline tracker
│   │   ├── tutor.py          # AI Academic Tutor chat
│   │   ├── notes.py          # Notes Summariser & flashcards
│   │   ├── planner.py        # Study Planner & schedule generator
│   │   ├── assignment.py     # Assignment Guidance tool
│   │   ├── exam.py           # Exam Preparation engine
│   │   ├── resources.py      # Resource Finder
│   │   └── feedback.py       # SUS Survey & feedback storage
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css     # Dark Emerald & Glassmorphism Design System CSS
│   │   └── js/
│   │       └── main.js       # AJAX handlers, progress progress bar logic, chat rendering
│   └── templates/
│       ├── base.html         # Glassmorphism base template layout with sidebar
│       ├── index.html        # Landing page
│       ├── auth/
│       │   ├── login.html
│       │   └── register.html
│       ├── dashboard.html    # Student dashboard
│       ├── roadmap/
│       │   ├── create.html   # Roadmap creation wizard
│       │   └── view.html     # Interactive timeline viewer
│       ├── tutor.html        # AI Tutor chat page
│       ├── notes.html        # Notes Summariser page
│       ├── planner.html      # Study Planner page
│       ├── assignment.html   # Assignment Guidance page
│       ├── exam.html         # Exam Prep page
│       ├── resources.html    # Resource Recommendation page
│       ├── feedback.html     # SUS Evaluation page
│       └── profile.html      # Profile & achievements page
├── instance/
│   └── app.db                # SQLite Database
├── .env.example              # Environment variables template
├── .env                      # Local environment configuration
├── requirements.txt          # Python package dependencies
├── run.py                    # Application launcher
└── README.md                 # Project documentation
```

---

## ⚡ Quick Start & Installation Instructions

### Prerequisites
- Python 3.9+ installed on Windows / macOS / Linux
- Visual Studio Code or any preferred IDE

### 1. Clone or Extract Project
Navigate to the project root directory:
```bash
cd "c:/Users/postm/OneDrive/Documents/anti gravity"
```

### 2. Create and Activate Virtual Environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
The `.env` file is pre-configured. To use an active OpenAI API key, open `.env` and enter your key:
```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=coventry_msc_dissertation_secret_key_2026_emerald_glass
DATABASE_URL=sqlite:///app.db
OPENAI_API_KEY=your_openai_api_key_here
```
*(Note: If `OPENAI_API_KEY` is left blank, the application automatically uses its built-in Smart AI Fallback Engine).*

### 5. Launch Application
```bash
python run.py
```

Open your browser and navigate to:
**`http://127.0.0.1:5000`**

---

## 📜 Academic Integrity Statement

This web application has been developed strictly in accordance with **Coventry University Academic Integrity Regulations**. All AI features function as learning scaffolding, tutoring, and study organization aids.

---

## ✒️ MSc Dissertation Metadata

- **Project Title:** AI-Powered Student Learning Assistant for Higher Education
- **University:** Coventry University
- **Degree:** MSc Dissertation Project
