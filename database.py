"""
database.py
-----------
Single SQLite database shared by every module (per your Software
Requirements slide). Each module calls the helper functions here instead
of touching SQL directly, so all six modules stay connected through one
source of truth: the student's id.

Run this file directly to create/reset the database:
    python database.py
"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Dict, List, Optional

from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    department TEXT NOT NULL,
    required_skills TEXT NOT NULL,     -- JSON dict
    description TEXT
);

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    academic_details TEXT,
    skills TEXT,              -- JSON list
    target_role TEXT,
    department TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS aptitude_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    score REAL,
    category_scores TEXT,     -- JSON dict
    taken_at TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE TABLE IF NOT EXISTS quiz_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    topic_scores TEXT,        -- JSON dict, matches skill names
    weak_topics TEXT,         -- JSON list
    feedback TEXT,
    taken_at TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE TABLE IF NOT EXISTS interview_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    role TEXT,
    qa_log TEXT,               -- JSON list of {question, answer, score, feedback}
    skill_scores TEXT,         -- JSON dict
    overall_score REAL,
    taken_at TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE TABLE IF NOT EXISTS resume_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    resume_text TEXT,
    extracted_skills TEXT,     -- JSON dict
    suggestions TEXT,
    taken_at TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE TABLE IF NOT EXISTS course_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    skill TEXT,
    course_name TEXT,
    duration_days INTEGER,
    verified INTEGER,
    completed_at TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE TABLE IF NOT EXISTS skill_gap_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    target_role TEXT,
    report_json TEXT,
    overall_readiness REAL,
    overall_level TEXT,
    taken_at TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id)
);
"""


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


DEFAULT_ROLES: List[Dict] = [
    {
        "name": "Data Analytics",
        "department": "Data Science, Analytics & AI",
        "required_skills": {
            "Python": 90, "SQL": 95, "Excel": 80, "Statistics": 85,
            "Power BI / Tableau": 75, "Data Cleaning": 80, "Communication": 60,
        },
        "description": "Analyze complex datasets, build BI dashboards, and drive business decision-making with predictive insights.",
    },
    {
        "name": "Data Analyst",
        "department": "Data Science, Analytics & AI",
        "required_skills": {
            "Python": 90, "SQL": 95, "Excel": 80, "Statistics": 85,
            "Power BI / Tableau": 75, "Data Cleaning": 80, "Communication": 60,
        },
        "description": "Interpret data, conduct exploratory data analysis (EDA), and communicate insights via reports.",
    },
    {
        "name": "AI/ML Engineer",
        "department": "Data Science, Analytics & AI",
        "required_skills": {
            "Python": 95, "Machine Learning": 95, "Deep Learning": 85, "Statistics": 85,
            "Data Structures": 65, "Model Deployment": 70,
        },
        "description": "Design, train, evaluate, and deploy production machine learning & deep learning models.",
    },
    {
        "name": "Data Engineer",
        "department": "Data Science, Analytics & AI",
        "required_skills": {
            "Python": 90, "SQL": 95, "Big Data & Spark": 85, "Data Warehousing": 80,
            "ETL Pipelines": 85, "Database Management (DBMS)": 75,
        },
        "description": "Design and maintain high-throughput ETL data pipelines and warehouse architectures.",
    },
    {
        "name": "Software Development Engineer (SDE)",
        "department": "Software Engineering & Development",
        "required_skills": {
            "Data Structures": 95, "Python": 85, "OOP & System Design": 85,
            "Database Management (DBMS)": 75, "Operating Systems": 70, "Communication": 60,
        },
        "description": "Develop scalable backend systems, robust software architectures, and algorithmic solutions.",
    },
    {
        "name": "Full Stack Web Developer",
        "department": "Software Engineering & Development",
        "required_skills": {
            "JavaScript / Web Tech": 90, "React / Frontend": 85, "Backend APIs & Node": 85,
            "SQL": 75, "Web Security & Auth": 70, "Communication": 60,
        },
        "description": "Build end-to-end modern web applications across both client and server layers.",
    },
    {
        "name": "Frontend Developer",
        "department": "Software Engineering & Development",
        "required_skills": {
            "JavaScript / Web Tech": 95, "React / Frontend": 90, "HTML & CSS / UI Styling": 90,
            "Web Performance": 75, "Communication": 60,
        },
        "description": "Create responsive, accessible, and high-performance user interfaces and web apps.",
    },
    {
        "name": "Backend Developer",
        "department": "Software Engineering & Development",
        "required_skills": {
            "Backend APIs & Node": 95, "SQL": 90, "Python": 85,
            "System Design": 80, "Operating Systems": 75, "Database Management (DBMS)": 85,
        },
        "description": "Architect server-side logic, REST APIs, databases, and microservices.",
    },
    {
        "name": "Mobile App Developer",
        "department": "Software Engineering & Development",
        "required_skills": {
            "Mobile App Development": 95, "Mobile UI/UX": 85, "REST APIs": 80,
            "State Management": 80, "Communication": 60,
        },
        "description": "Develop native and cross-platform mobile apps for Android and iOS devices.",
    },
    {
        "name": "Cloud & DevOps Engineer",
        "department": "Cloud, DevOps & Systems Infrastructure",
        "required_skills": {
            "Linux & Shell Scripting": 90, "Docker & Containers": 90, "Kubernetes & Orchestration": 85,
            "CI/CD Pipelines": 85, "Cloud Platforms (AWS/Azure)": 90, "Computer Networks": 75,
        },
        "description": "Automate deployments, manage cloud infrastructure, and maintain CI/CD pipelines.",
    },
    {
        "name": "Network & Systems Administrator",
        "department": "Cloud, DevOps & Systems Infrastructure",
        "required_skills": {
            "Computer Networks": 95, "Linux & Shell Scripting": 90, "Network Security": 85,
            "Troubleshooting & Diagnostics": 85, "Operating Systems": 80,
        },
        "description": "Administer network infrastructure, servers, system security, and troubleshooting.",
    },
    {
        "name": "Cybersecurity Analyst",
        "department": "Cybersecurity & Information Security",
        "required_skills": {
            "Network Security": 95, "Ethical Hacking & Web Security": 85, "Cryptography": 80,
            "Vulnerability Assessment": 90, "Computer Networks": 85, "Operating Systems": 75,
        },
        "description": "Protect systems and networks from cyber threats, vulnerabilities, and unauthorized access.",
    },
    {
        "name": "QA Automation Engineer",
        "department": "Quality Assurance & Software Testing",
        "required_skills": {
            "Software Testing Principles": 95, "Test Automation (Selenium)": 90,
            "API Testing": 85, "Python": 80, "CI/CD Pipelines": 75, "Communication": 65,
        },
        "description": "Automate end-to-end testing, write test suites, and ensure software quality and reliability.",
    },
]


def seed_default_roles():
    """Seeds default IT departments and roles (including Data Analytics) into the database."""
    with get_conn() as conn:
        for r in DEFAULT_ROLES:
            conn.execute(
                "INSERT OR IGNORE INTO roles (name, department, required_skills, description) VALUES (?, ?, ?, ?)",
                (r["name"], r["department"], json.dumps(r["required_skills"]), r.get("description", "")),
            )


def add_role(name: str, department: str, required_skills: dict, description: str = ""):
    """Adds or updates a job role in the database."""
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO roles (name, department, required_skills, description) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(name) DO UPDATE SET "
            "department=excluded.department, required_skills=excluded.required_skills, description=excluded.description",
            (name, department, json.dumps(required_skills), description),
        )


def get_role(name: str) -> Optional[dict]:
    """Fetches role record and parsed required_skills by name."""
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM roles WHERE name = ?", (name,)).fetchone()
        if not row:
            return None
        d = dict(row)
        d["required_skills"] = json.loads(d["required_skills"] or "{}")
        return d


def get_all_roles(department: Optional[str] = None) -> List[dict]:
    """Fetches all roles, optionally filtered by department."""
    with get_conn() as conn:
        if department:
            rows = conn.execute("SELECT * FROM roles WHERE department = ?", (department,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM roles").fetchall()
        res = []
        for r in rows:
            d = dict(r)
            d["required_skills"] = json.loads(d["required_skills"] or "{}")
            res.append(d)
        return res


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)
        # Safe migration to add department if missing in existing DB
        cur = conn.execute("PRAGMA table_info(students)")
        columns = [row["name"] for row in cur.fetchall()]
        if "department" not in columns:
            conn.execute("ALTER TABLE students ADD COLUMN department TEXT")
    seed_default_roles()


# ---------------------------------------------------------------------------
# Module 2 — User Registration & Profile
# ---------------------------------------------------------------------------

def create_or_update_student(name, email, skills, academic_details, target_role, department=None) -> int:
    with get_conn() as conn:
        cur = conn.execute("SELECT id FROM students WHERE email = ?", (email,))
        row = cur.fetchone()
        if row:
            student_id = row["id"]
            conn.execute(
                "UPDATE students SET name=?, skills=?, academic_details=?, target_role=?, department=? WHERE id=?",
                (name, json.dumps(skills), academic_details, target_role, department, student_id),
            )
        else:
            cur = conn.execute(
                "INSERT INTO students (name, email, academic_details, skills, target_role, department, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (name, email, academic_details, json.dumps(skills), target_role, department, datetime.now().isoformat()),
            )
            student_id = cur.lastrowid
        return student_id


def get_student(student_id) -> dict:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        d["skills"] = json.loads(d["skills"] or "[]")
        if "department" not in d:
            d["department"] = None
        return d


# ---------------------------------------------------------------------------
# Module 1 — Aptitude Test
# ---------------------------------------------------------------------------

def save_aptitude_result(student_id, score, category_scores):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO aptitude_results (student_id, score, category_scores, taken_at) VALUES (?,?,?,?)",
            (student_id, score, json.dumps(category_scores), datetime.now().isoformat()),
        )


# ---------------------------------------------------------------------------
# Module 3 — Technical Quiz
# ---------------------------------------------------------------------------

def save_quiz_result(student_id, topic_scores, weak_topics, feedback):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO quiz_results (student_id, topic_scores, weak_topics, feedback, taken_at) "
            "VALUES (?,?,?,?,?)",
            (student_id, json.dumps(topic_scores), json.dumps(weak_topics), feedback, datetime.now().isoformat()),
        )


def get_latest_quiz_result(student_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM quiz_results WHERE student_id=? ORDER BY id DESC LIMIT 1", (student_id,)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        d["topic_scores"] = json.loads(d["topic_scores"] or "{}")
        d["weak_topics"] = json.loads(d["weak_topics"] or "[]")
        return d


# ---------------------------------------------------------------------------
# Module 4 — AI Mock Interview
# ---------------------------------------------------------------------------

def save_interview_result(student_id, role, qa_log, skill_scores, overall_score):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO interview_results (student_id, role, qa_log, skill_scores, overall_score, taken_at) "
            "VALUES (?,?,?,?,?,?)",
            (student_id, role, json.dumps(qa_log), json.dumps(skill_scores), overall_score,
             datetime.now().isoformat()),
        )


def get_latest_interview_result(student_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM interview_results WHERE student_id=? ORDER BY id DESC LIMIT 1", (student_id,)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        d["skill_scores"] = json.loads(d["skill_scores"] or "{}")
        d["qa_log"] = json.loads(d["qa_log"] or "[]")
        return d


# ---------------------------------------------------------------------------
# Module 5 — Resume Analyzer
# ---------------------------------------------------------------------------

def save_resume_analysis(student_id, resume_text, extracted_skills, suggestions):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO resume_analysis (student_id, resume_text, extracted_skills, suggestions, taken_at) "
            "VALUES (?,?,?,?,?)",
            (student_id, resume_text, json.dumps(extracted_skills), suggestions, datetime.now().isoformat()),
        )


def get_latest_resume_analysis(student_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM resume_analysis WHERE student_id=? ORDER BY id DESC LIMIT 1", (student_id,)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        d["extracted_skills"] = json.loads(d["extracted_skills"] or "{}")
        return d


def add_course_record(student_id, skill, course_name, duration_days, verified, days_since_completion=0):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO course_history (student_id, skill, course_name, duration_days, verified, completed_at) "
            "VALUES (?,?,?,?,?,?)",
            (student_id, skill, course_name, duration_days, int(verified), datetime.now().isoformat()),
        )


def get_course_history(student_id):
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM course_history WHERE student_id=?", (student_id,)).fetchall()
        return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Module 6 — Skill Gap Analysis
# ---------------------------------------------------------------------------

def save_skill_gap_report(student_id, target_role, report_json, overall_readiness, overall_level):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO skill_gap_reports "
            "(student_id, target_role, report_json, overall_readiness, overall_level, taken_at) "
            "VALUES (?,?,?,?,?,?)",
            (student_id, target_role, report_json, overall_readiness, overall_level,
             datetime.now().isoformat()),
        )


if __name__ == "__main__":
    init_db()
    print(f"Database ready at: {DB_PATH}")
