"""
user_profile.py
----------------
Module 2 — User Registration & Profile Module.

Purpose: Create and maintain the student's profile for personalized
preparation.

Input:  Name, Email, Skills, Academic Details, Target Role
Output: Personalized Student Profile (a student_id that every other
        module uses to save/load results against).
"""

from typing import List

from database import create_or_update_student, get_student


def register_student(name: str, email: str, skills: List[str],
                     academic_details: str, target_role: str,
                     department: str = None) -> int:
    """Creates a new student profile, or updates it if the email already
    exists (so re-running registration doesn't create duplicates)."""
    if not name or not email:
        raise ValueError("Name and email are required.")
    if "@" not in email:
        raise ValueError("Enter a valid email address.")

    student_id = create_or_update_student(
        name=name, email=email, skills=skills,
        academic_details=academic_details, target_role=target_role,
        department=department,
    )
    return student_id


def get_profile(student_id: int) -> dict:
    profile = get_student(student_id)
    if not profile:
        raise ValueError(f"No student found with id {student_id}")
    return profile


if __name__ == "__main__":
    from database import init_db
    init_db()

    sid = register_student(
        name="Bharath Kumar S",
        email="bharath@example.com",
        skills=["Python", "SQL", "Excel"],
        academic_details="B.Tech AI & Data Science, 3rd year",
        target_role="Data Analyst",
    )
    print(f"Registered student id: {sid}")
    print("Profile:", get_profile(sid))
