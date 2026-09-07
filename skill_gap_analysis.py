"""
skill_gap_analysis.py
----------------------
Module 6 — Skill Gap Analysis Module.

Objective (per slide 20):
  - Identify the gap between the student's current skills and the
    skills required for the target job role.
  - Analyze resume, assessment (quiz) and interview performance.
  - Prioritize the skills that need improvement.
  - New: Adds course/certification history as a supporting signal, and
    classifies each skill as Beginner, Intermediate, or Advanced.

This version is wired into the shared project: it uses config.py for
the LLM (falls back to rule-based logic with no API key needed) and
database.py to pull in the latest resume analysis, quiz result,
interview result, and course history for a given student_id — so you
can call run_skill_gap_analysis_for_student(student_id, target_role)
and it assembles everything automatically from what the other five
modules already saved.
"""

import json
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from config import USE_LLM, get_model
from database import (
    get_latest_resume_analysis,
    get_latest_quiz_result,
    get_latest_interview_result,
    get_course_history,
    save_skill_gap_report,
)

# ---------------------------------------------------------------------------
# 1. IT DEPARTMENTS & ROLE -> REQUIRED SKILLS MAP
# ---------------------------------------------------------------------------

IT_DEPARTMENTS: Dict[str, List[str]] = {
    "Software Engineering & Development": [
        "Software Development Engineer (SDE)",
        "Full Stack Web Developer",
        "Frontend Developer",
        "Backend Developer",
        "Mobile App Developer",
    ],
    "Data Science, Analytics & AI": [
        "Data Analytics",
        "Data Analyst",
        "AI/ML Engineer",
        "Data Engineer",
    ],
    "Cloud, DevOps & Systems Infrastructure": [
        "Cloud & DevOps Engineer",
        "Network & Systems Administrator",
    ],
    "Cybersecurity & Information Security": [
        "Cybersecurity Analyst",
    ],
    "Quality Assurance & Software Testing": [
        "QA Automation Engineer",
    ],
}

ROLE_SKILL_MAP: Dict[str, Dict[str, int]] = {
    # Data Science, Analytics & AI
    "Data Analytics": {
        "Python": 90, "SQL": 95, "Excel": 80, "Statistics": 85,
        "Power BI / Tableau": 75, "Data Cleaning": 80, "Communication": 60,
    },
    "Data Analyst": {
        "Python": 90, "SQL": 95, "Excel": 80, "Statistics": 85,
        "Power BI / Tableau": 75, "Data Cleaning": 80, "Communication": 60,
    },
    "AI/ML Engineer": {
        "Python": 95, "Machine Learning": 95, "Deep Learning": 85, "Statistics": 85,
        "Data Structures": 65, "Model Deployment": 70,
    },
    "Data Engineer": {
        "Python": 90, "SQL": 95, "Big Data & Spark": 85, "Data Warehousing": 80,
        "ETL Pipelines": 85, "Database Management (DBMS)": 75,
    },

    # Software Engineering & Development
    "Software Development Engineer (SDE)": {
        "Data Structures": 95, "Python": 85, "OOP & System Design": 85,
        "Database Management (DBMS)": 75, "Operating Systems": 70, "Communication": 60,
    },
    "Software Developer": {  # Backwards compatibility alias
        "Data Structures": 95, "Python": 85, "OOP & System Design": 85,
        "Database Management (DBMS)": 75, "Operating Systems": 70, "Communication": 60,
    },
    "Full Stack Web Developer": {
        "JavaScript / Web Tech": 90, "React / Frontend": 85, "Backend APIs & Node": 85,
        "SQL": 75, "Web Security & Auth": 70, "Communication": 60,
    },
    "Frontend Developer": {
        "JavaScript / Web Tech": 95, "React / Frontend": 90, "HTML & CSS / UI Styling": 90,
        "Web Performance": 75, "Communication": 60,
    },
    "Backend Developer": {
        "Backend APIs & Node": 95, "SQL": 90, "Python": 85,
        "System Design": 80, "Operating Systems": 75, "Database Management (DBMS)": 85,
    },
    "Mobile App Developer": {
        "Mobile App Development": 95, "Mobile UI/UX": 85, "REST APIs": 80,
        "State Management": 80, "Communication": 60,
    },

    # Cloud, DevOps & Systems Infrastructure
    "Cloud & DevOps Engineer": {
        "Linux & Shell Scripting": 90, "Docker & Containers": 90, "Kubernetes & Orchestration": 85,
        "CI/CD Pipelines": 85, "Cloud Platforms (AWS/Azure)": 90, "Computer Networks": 75,
    },
    "Network & Systems Administrator": {
        "Computer Networks": 95, "Linux & Shell Scripting": 90, "Network Security": 85,
        "Troubleshooting & Diagnostics": 85, "Operating Systems": 80,
    },

    # Cybersecurity & Information Security
    "Cybersecurity Analyst": {
        "Network Security": 95, "Ethical Hacking & Web Security": 85, "Cryptography": 80,
        "Vulnerability Assessment": 90, "Computer Networks": 85, "Operating Systems": 75,
    },

    # Quality Assurance & Software Testing
    "QA Automation Engineer": {
        "Software Testing Principles": 95, "Test Automation (Selenium)": 90,
        "API Testing": 85, "Python": 80, "CI/CD Pipelines": 75, "Communication": 65,
    },
}


def get_department_for_role(role: str) -> str:
    """Returns the IT Department that the role belongs to."""
    if role == "Software Developer":
        return "Software Engineering & Development"
    if "Analytics" in role or "Data Analyst" in role:
        return "Data Science, Analytics & AI"

    # Check database role definition if available
    try:
        from database import get_role
        db_role = get_role(role)
        if db_role and db_role.get("department"):
            return db_role["department"]
    except Exception:
        pass

    for dept, roles in IT_DEPARTMENTS.items():
        if role in roles:
            return dept
    return "Software Engineering & Development"


def get_roles_for_department(department: str) -> List[str]:
    """Returns the list of roles belonging to an IT department."""
    try:
        from database import get_all_roles
        db_roles = [r["name"] for r in get_all_roles(department)]
        if db_roles:
            return db_roles
    except Exception:
        pass
    return IT_DEPARTMENTS.get(department, list(ROLE_SKILL_MAP.keys()))


def get_required_skills(target_role: str) -> Dict[str, int]:
    if target_role not in ROLE_SKILL_MAP:
        # Check database first
        try:
            from database import get_role
            db_role = get_role(target_role)
            if db_role and db_role.get("required_skills"):
                return db_role["required_skills"]
        except Exception:
            pass

        # Fallback alias check
        if "Analytics" in target_role or "Data Analyst" in target_role:
            return ROLE_SKILL_MAP["Data Analytics"]
        if "Software" in target_role or "SDE" in target_role:
            return ROLE_SKILL_MAP["Software Development Engineer (SDE)"]
        raise ValueError(f"Unknown role '{target_role}'. Available: {list(ROLE_SKILL_MAP)}")
    return ROLE_SKILL_MAP[target_role]


# ---------------------------------------------------------------------------
# 2a. RESUME -> CLAIMED SKILLS
# ---------------------------------------------------------------------------

def extract_skills_from_resume(resume_text: str, candidate_skills: List[str]) -> Dict[str, int]:
    if USE_LLM:
        model = get_model()
        prompt = (f"Given this resume and skill list, output ONLY a JSON object mapping each "
                  f"skill to a confidence score 0-100 based on evidence in the resume (0 if "
                  f"not mentioned). Skills: {json.dumps(candidate_skills)}\nResume:\n\"\"\"{resume_text}\"\"\"")
        raw = model.generate_content(prompt).text.strip()
        raw = re.sub(r"^```json|```$", "", raw, flags=re.MULTILINE).strip()
        try:
            scores = json.loads(raw)
            return {s: int(scores.get(s, 0)) for s in candidate_skills}
        except json.JSONDecodeError:
            pass

    lower = resume_text.lower()
    project_markers = ["project", "built", "developed", "implemented", "used", "led"]
    scores = {}
    for skill in candidate_skills:
        if skill.lower() not in lower:
            scores[skill] = 0
            continue
        idx = lower.find(skill.lower())
        window = lower[max(0, idx - 60):idx + 60]
        scores[skill] = 65 if any(m in window for m in project_markers) else 35
    return scores


# ---------------------------------------------------------------------------
# 2b. TECHNICAL QUIZ -> DEMONSTRATED SKILLS
# ---------------------------------------------------------------------------

@dataclass
class QuizResult:
    topic_scores: Dict[str, float]


def quiz_to_skill_scores(quiz: QuizResult, candidate_skills: List[str]) -> Dict[str, int]:
    return {s: int(quiz.topic_scores.get(s, 0)) for s in candidate_skills}


# ---------------------------------------------------------------------------
# 2c. MOCK INTERVIEW -> DEMONSTRATED SKILLS
# ---------------------------------------------------------------------------

@dataclass
class InterviewResult:
    skill_scores: Dict[str, float]


def interview_to_skill_scores(interview: InterviewResult, candidate_skills: List[str]) -> Dict[str, int]:
    return {s: int(interview.skill_scores.get(s, 0)) for s in candidate_skills}


# ---------------------------------------------------------------------------
# 2d. COURSE / CERTIFICATION HISTORY -> SUPPORTING SIGNAL
# ---------------------------------------------------------------------------

@dataclass
class CourseRecord:
    skill: str
    course_name: str
    duration_days: int
    verified: bool = False
    days_since_completion: int = 0


def course_history_to_scores(courses: List[CourseRecord], candidate_skills: List[str]) -> Dict[str, int]:
    scores = {s: 0 for s in candidate_skills}
    for c in courses:
        if c.skill not in scores:
            continue
        base = 40
        if c.verified:
            base += 15
        if c.days_since_completion > 90:
            decay = max(0.5, 1 - (c.days_since_completion - 90) / 365)
            base = int(base * decay)
        scores[c.skill] = max(scores[c.skill], base)
    return scores


# ---------------------------------------------------------------------------
# 3. BLEND ALL FOUR SIGNALS
# ---------------------------------------------------------------------------

SOURCE_WEIGHTS = {"resume": 0.15, "quiz": 0.40, "interview": 0.30, "course": 0.15}


def blend_proficiency(resume_scores, quiz_scores, interview_scores, course_scores) -> Dict[str, float]:
    blended = {}
    for skill in resume_scores:
        blended[skill] = round(
            resume_scores.get(skill, 0) * SOURCE_WEIGHTS["resume"]
            + quiz_scores.get(skill, 0) * SOURCE_WEIGHTS["quiz"]
            + interview_scores.get(skill, 0) * SOURCE_WEIGHTS["interview"]
            + course_scores.get(skill, 0) * SOURCE_WEIGHTS["course"],
            1,
        )
    return blended


# ---------------------------------------------------------------------------
# 4. CLASSIFICATION
# ---------------------------------------------------------------------------

def classify_level(proficiency: float) -> str:
    if proficiency <= 40:
        return "Beginner"
    elif proficiency <= 70:
        return "Intermediate"
    else:
        return "Advanced"


# ---------------------------------------------------------------------------
# 5. GAP COMPUTATION + PRIORITY RANKING
# ---------------------------------------------------------------------------

@dataclass
class SkillGap:
    skill: str
    required_weight: int
    proficiency: float
    level: str
    gap: float
    priority_score: float


def compute_gaps(required: Dict[str, int], proficiency: Dict[str, float]) -> List[SkillGap]:
    gaps = []
    for skill, weight in required.items():
        prof = proficiency.get(skill, 0)
        gap = max(0.0, weight - prof)
        priority_score = round(gap * (weight / 100), 2)
        gaps.append(SkillGap(skill, weight, prof, classify_level(prof), round(gap, 1), priority_score))
    gaps.sort(key=lambda g: g.priority_score, reverse=True)
    return gaps


# ---------------------------------------------------------------------------
# 6. RECOMMENDATIONS
# ---------------------------------------------------------------------------

def generate_recommendations(target_role: str, gaps: List[SkillGap], top_n: int = 5) -> str:
    top_gaps = gaps[:top_n]

    if USE_LLM:
        model = get_model()
        gap_summary = "\n".join(
            f"- {g.skill}: proficiency {g.proficiency}/100 ({g.level}), "
            f"role requires {g.required_weight}/100 (gap {g.gap})" for g in top_gaps
        )
        prompt = (f"A student is preparing for \"{target_role}\". Biggest skill gaps:\n{gap_summary}\n"
                  f"For each: 1) why it matters, 2) 2-3 concrete learning actions, "
                  f"3) a realistic time estimate. Concise, skill names as headers.")
        return model.generate_content(prompt).text.strip()

    lines = []
    for g in top_gaps:
        if g.level == "Beginner":
            action = "Start with foundational tutorials + daily practice problems (30-45 min/day)."
            weeks = max(3, round(g.gap / 12))
        elif g.level == "Intermediate":
            action = "Do targeted practice on weak sub-topics + build one small project using this skill."
            weeks = max(2, round(g.gap / 15))
        else:
            action = "Polish edge cases and be ready to explain trade-offs in interviews."
            weeks = 1
        lines.append(
            f"## {g.skill}  ({g.level}, gap {g.gap} pts)\n"
            f"- Role importance: {g.required_weight}/100\n"
            f"- Action: {action}\n"
            f"- Estimated time to close gap: ~{weeks} week(s) at steady daily effort.\n"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 7. ORCHESTRATORS
# ---------------------------------------------------------------------------

@dataclass
class SkillGapReport:
    target_role: str
    gaps: List[SkillGap]
    recommendations: str
    overall_readiness: float
    overall_level: str


def run_skill_gap_analysis(target_role: str, resume_text: str, quiz: QuizResult,
                            interview: InterviewResult,
                            courses: Optional[List[CourseRecord]] = None) -> SkillGapReport:
    """Direct call — pass everything in manually (used by the standalone
    Streamlit demo, or when you want to test without touching the DB)."""
    courses = courses or []
    required = get_required_skills(target_role)
    candidate_skills = list(required.keys())

    resume_scores = extract_skills_from_resume(resume_text, candidate_skills)
    quiz_scores = quiz_to_skill_scores(quiz, candidate_skills)
    interview_scores = interview_to_skill_scores(interview, candidate_skills)
    course_scores = course_history_to_scores(courses, candidate_skills)

    proficiency = blend_proficiency(resume_scores, quiz_scores, interview_scores, course_scores)
    gaps = compute_gaps(required, proficiency)
    recommendations = generate_recommendations(target_role, gaps)

    total_weight = sum(required.values())
    weighted_prof = sum(proficiency[s] * (required[s] / total_weight) for s in required)
    overall_readiness = round(weighted_prof, 1)

    return SkillGapReport(target_role, gaps, recommendations, overall_readiness,
                          classify_level(overall_readiness))


def run_skill_gap_analysis_for_student(student_id: int, target_role: str) -> SkillGapReport:
    """
    The 'connected' path: pulls the student's latest saved results from
    Modules 3, 4, 5 (technical quiz, mock interview, resume analysis) and
    their course history out of the shared database, then runs the same
    analysis as run_skill_gap_analysis(). This is what app.py calls once
    a student has been through the other modules.
    """
    resume_row = get_latest_resume_analysis(student_id)
    quiz_row = get_latest_quiz_result(student_id)
    interview_row = get_latest_interview_result(student_id)
    course_rows = get_course_history(student_id)

    resume_text = resume_row["resume_text"] if resume_row else ""
    quiz = QuizResult(topic_scores=quiz_row["topic_scores"] if quiz_row else {})
    interview = InterviewResult(skill_scores=interview_row["skill_scores"] if interview_row else {})
    courses = [
        CourseRecord(skill=c["skill"], course_name=c["course_name"],
                     duration_days=c["duration_days"], verified=bool(c["verified"]))
        for c in course_rows
    ]

    report = run_skill_gap_analysis(target_role, resume_text, quiz, interview, courses)

    report_json = json.dumps([g.__dict__ for g in report.gaps])
    save_skill_gap_report(student_id, target_role, report_json,
                          report.overall_readiness, report.overall_level)

    return report


# ---------------------------------------------------------------------------
# 8. DEMO — run this file directly: `python skill_gap_analysis.py`
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    resume_text = """
    Bharath Kumar S — B.Tech AI & Data Science student.
    Completed Python Intermediate course (30 days). Completed Data
    Analytics basics masterclass (30 days). Used Python and pandas to
    build a data cleaning script for a college project. Familiar with
    SQL and Excel from coursework. Skills: Python, SQL, Excel,
    Data Cleaning, Statistics.
    """

    quiz = QuizResult(topic_scores={
        "Python": 72, "SQL": 38, "Excel": 55, "Statistics": 60,
        "Power BI / Tableau": 20, "Data Cleaning": 65, "Communication": 70,
    })

    interview = InterviewResult(skill_scores={
        "Python": 65, "SQL": 30, "Excel": 40, "Statistics": 55,
        "Power BI / Tableau": 10, "Data Cleaning": 60, "Communication": 75,
    })

    courses = [
        CourseRecord(skill="Python", course_name="Python Intermediate",
                     duration_days=30, verified=True, days_since_completion=10),
        CourseRecord(skill="Statistics", course_name="Data Analytics Basics Masterclass",
                     duration_days=30, verified=False, days_since_completion=10),
    ]

    report = run_skill_gap_analysis("Data Analyst", resume_text, quiz, interview, courses)

    print(f"\n{'='*70}\nSKILL GAP REPORT — Target Role: {report.target_role}\n{'='*70}")
    print(f"Overall Readiness: {report.overall_readiness}/100  ->  {report.overall_level}\n")
    print(f"{'Skill':<22}{'Level':<14}{'Proficiency':<13}{'Required':<10}{'Gap':<8}{'Priority'}")
    print("-" * 70)
    for g in report.gaps:
        print(f"{g.skill:<22}{g.level:<14}{g.proficiency:<13}{g.required_weight:<10}{g.gap:<8}{g.priority_score}")
    print(f"\n{'='*70}\nRECOMMENDATIONS\n{'='*70}")
    print(report.recommendations)
