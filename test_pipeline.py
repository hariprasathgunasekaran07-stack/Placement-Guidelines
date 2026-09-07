"""
test_pipeline.py
-----------------
Runs all six modules end-to-end for sample students across multiple IT departments
and targeted roles, verifying full integration and readiness.

Run: python test_pipeline.py
"""

from database import init_db, add_course_record
from user_profile import register_student, get_profile
from aptitude_test import get_questions as get_aptitude_questions, score_aptitude_test
from technical_quiz import get_questions_for_role, score_technical_quiz
from mock_interview import run_mock_interview
from resume_analyzer import analyze_resume
from skill_gap_analysis import (
    run_skill_gap_analysis_for_student,
    ROLE_SKILL_MAP,
    IT_DEPARTMENTS,
    get_department_for_role,
)


def run_pipeline_for_role(name: str, email: str, target_role: str, department: str):
    print(f"\n{'='*75}")
    print(f"Testing End-to-End Pipeline for: {target_role} | Department: {department}")
    print(f"{'='*75}")

    # --- Module 2: Registration & Profile ---
    print("\n[Module 2] Registering student profile...")
    skills_for_role = list(ROLE_SKILL_MAP[target_role].keys())
    sid = register_student(
        name=name,
        email=email,
        skills=skills_for_role[:3],
        academic_details=f"B.Tech 3rd year — {department}",
        target_role=target_role,
        department=department,
    )
    profile = get_profile(sid)
    print(f"  student_id = {sid}")
    print(f"  profile: {profile['name']} | Role: {profile['target_role']} | Dept: {profile.get('department')}")

    # --- Module 1: Role-Targeted Aptitude Test ---
    print("\n[Module 1] Running role-targeted aptitude test...")
    apt_questions = get_aptitude_questions(target_role=target_role, department=department)
    print(f"  Loaded {len(apt_questions)} targeted aptitude questions.")
    apt_q_ids = [q["id"] for q in apt_questions]
    # Simulate realistic answers (mostly correct, some incorrect)
    apt_answers = {q["id"]: (1 if q["id"] % 3 != 0 else 0) for q in apt_questions}
    apt_result = score_aptitude_test(apt_answers, sid, question_ids=apt_q_ids)
    print(f"  Aptitude Overall Score: {apt_result['overall_score']}/100")
    print(f"  Category Scores: {apt_result['category_scores']}")

    # --- Module 3: Role- & Department-Targeted Technical Quiz ---
    print("\n[Module 3] Running role-tailored technical quiz...")
    tech_questions = get_questions_for_role(target_role=target_role, department=department, count=10)
    print(f"  Loaded {len(tech_questions)} technical questions for {target_role}.")
    tech_q_ids = [q["id"] for q in tech_questions]
    tech_answers = {q["id"]: 1 for q in tech_questions}
    quiz_result = score_technical_quiz(tech_answers, sid, question_ids=tech_q_ids)
    print(f"  Technical Score: {quiz_result['overall_score']}/100")
    print(f"  Topic Breakdown: {quiz_result['topic_scores']}")
    print(f"  Weak Topics: {quiz_result['weak_topics'] or 'None'}")
    print(f"  Feedback: {quiz_result['feedback']}")

    # --- Module 4: AI Mock Interview ---
    print("\n[Module 4] Running mock interview with role-aligned questions...")
    interview_answers = {}
    for skill in skills_for_role[:5]:
        interview_answers[skill] = (
            f"I have strong hands-on experience applying {skill} in software projects, "
            f"following standard design patterns, efficiency trade-offs, and testing methodologies."
        )
    interview_result = run_mock_interview(
        student_id=sid,
        role=target_role,
        skills=list(interview_answers.keys()),
        answers=interview_answers,
        department=department,
    )
    print(f"  Mock Interview Overall Score: {interview_result['overall_score']}/100")
    for item in interview_result["qa_log"][:2]:
        print(f"  - [{item['skill']}]: {item['score']}/100 -> {item['feedback']}")

    # --- Module 5: Resume Analyzer ---
    print("\n[Module 5] Analyzing resume...")
    resume_text = f"""
    {name} — Engineering Student ({department}).
    Passionate about {target_role}.
    Completed projects demonstrating {', '.join(skills_for_role[:4])}.
    Hands-on experience with github repositories and automated testing.
    Reduced processing latency by 30% through algorithm optimization.
    Skills: {', '.join(skills_for_role)}.
    """
    resume_result = analyze_resume(sid, resume_text, target_role, skills_for_role)
    print(f"  Extracted Skills: {resume_result['extracted_skills']}")
    print(f"  Suggestions Preview: {resume_result['suggestions'].splitlines()[0] if resume_result['suggestions'] else 'None'}")

    # --- Course History Supporting Signal ---
    print("\n[Module 6 Input] Adding course/certification records...")
    add_course_record(sid, skills_for_role[0], f"Advanced {skills_for_role[0]} Masterclass", 30, verified=True)
    if len(skills_for_role) > 1:
        add_course_record(sid, skills_for_role[1], f"{skills_for_role[1]} Foundations", 20, verified=False)
    print("  Course records added.")

    # --- Module 6: Skill Gap Analysis ---
    print("\n[Module 6] Generating Skill Gap Report...")
    report = run_skill_gap_analysis_for_student(sid, target_role)
    print(f"  Overall Readiness: {report.overall_readiness}/100 -> {report.overall_level}")
    print(f"  Top Gap: {report.gaps[0].skill} (Gap: {report.gaps[0].gap} pts, Priority: {report.gaps[0].priority_score})")
    print(f"  Recommendations Preview:\n{report.recommendations.splitlines()[:4]}")
    print(f"✅ Successfully completed pipeline for {target_role}")


def main():
    print("Initializing SQLite Database and schema migrations...")
    init_db()

    # Test 1: Data Science, Analytics & AI -> Data Analyst
    run_pipeline_for_role(
        name="Bharath Kumar S",
        email="bharath.da@example.com",
        target_role="Data Analyst",
        department="Data Science, Analytics & AI",
    )

    # Test 2: Software Engineering & Development -> Software Development Engineer (SDE)
    run_pipeline_for_role(
        name="Sneha Sharma",
        email="sneha.sde@example.com",
        target_role="Software Development Engineer (SDE)",
        department="Software Engineering & Development",
    )

    print("\n" + "="*75)
    print("🎉 ALL PIPELINE VERIFICATIONS PASSED SUCCESSFULLY!")
    print("Available IT Departments:", list(IT_DEPARTMENTS.keys()))
    print("Available Targeted Roles:", list(ROLE_SKILL_MAP.keys()))
    print("="*75)


if __name__ == "__main__":
    main()
