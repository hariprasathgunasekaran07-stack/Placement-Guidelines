"""
aptitude_test.py
-----------------
Module 1 — Aptitude Test Module.

Purpose: Evaluate the student's aptitude across diverse categories:
- Quantitative Aptitude (Arithmetic, Percentages, Ratios, Time & Work)
- Logical Reasoning (Series, Syllogisms, Blood Relations, Deduction)
- Verbal Ability (Grammar, Vocabulary, Sentence Correction)
- Data Interpretation (Graph & Table analysis — targeted for Data/AI roles)
- Pseudocode & Algorithmic Logic (Output prediction, Control flow — targeted for Software & QA roles)
- Systems & Network Diagnostics (Fault tracing, Binary/Subnetting logic — targeted for Cloud/Cyber roles)

Supports role-targeted aptitude test generation and full comprehensive placement assessment.
"""

from typing import Dict, List, Optional
from database import save_aptitude_result

# ---------------------------------------------------------------------------
# Comprehensive Multi-Category Question Bank
# ---------------------------------------------------------------------------

QUESTION_BANK: List[Dict] = [
    # ------------------ Quantitative Aptitude ------------------
    {"id": 1, "category": "Quantitative Aptitude",
     "departments": ["All"], "roles": ["All"],
     "question": "What is 15% of 200?",
     "options": ["20", "30", "25", "35"], "answer": 1},

    {"id": 2, "category": "Quantitative Aptitude",
     "departments": ["All"], "roles": ["All"],
     "question": "A train travels 60 km in 45 minutes. What is its speed in km/h?",
     "options": ["70", "75", "80", "90"], "answer": 2},

    {"id": 3, "category": "Quantitative Aptitude",
     "departments": ["All"], "roles": ["All"],
     "question": "If the ratio of two numbers is 3:5 and their sum is 40, what is the smaller number?",
     "options": ["12", "15", "18", "20"], "answer": 1},

    {"id": 4, "category": "Quantitative Aptitude",
     "departments": ["All"], "roles": ["All"],
     "question": "A pipe can fill a tank in 6 hours and another pipe empties it in 12 hours. If both open together, in how many hours will the tank fill?",
     "options": ["8 hours", "10 hours", "12 hours", "15 hours"], "answer": 2},

    {"id": 5, "category": "Quantitative Aptitude",
     "departments": ["All"], "roles": ["All"],
     "question": "A sum of ₹10,000 earns simple interest of ₹1,600 in 2 years. What is the annual interest rate?",
     "options": ["6%", "7%", "8%", "9%"], "answer": 2},

    # ------------------ Logical Reasoning ------------------
    {"id": 6, "category": "Logical Reasoning",
     "departments": ["All"], "roles": ["All"],
     "question": "Find the odd one out: Dog, Cat, Lion, Table",
     "options": ["Dog", "Cat", "Lion", "Table"], "answer": 3},

    {"id": 7, "category": "Logical Reasoning",
     "departments": ["All"], "roles": ["All"],
     "question": "If all Bloops are Razzies and all Razzies are Lazzies, are all Bloops definitely Lazzies?",
     "options": ["Yes", "No", "Cannot be determined", "Only sometimes"], "answer": 0},

    {"id": 8, "category": "Logical Reasoning",
     "departments": ["All"], "roles": ["All"],
     "question": "Complete the series: 2, 6, 12, 20, 30, ?",
     "options": ["36", "40", "42", "44"], "answer": 2},

    {"id": 9, "category": "Logical Reasoning",
     "departments": ["All"], "roles": ["All"],
     "question": "Pointing to a photograph, Rohit said 'Her mother is the only daughter of my mother.' How is Rohit related to the girl?",
     "options": ["Brother", "Father", "Uncle", "Grandfather"], "answer": 1},

    {"id": 10, "category": "Logical Reasoning",
     "departments": ["All"], "roles": ["All"],
     "question": "In a certain code, 'PYTHON' is written as 'QZWIPO'. How is 'JAVA' written in that same pattern (+1 for each character)?",
     "options": ["KBWB", "KZWA", "LBYB", "KAXB"], "answer": 0},

    # ------------------ Verbal Ability ------------------
    {"id": 11, "category": "Verbal Ability",
     "departments": ["All"], "roles": ["All"],
     "question": "Choose the correct antonym for 'OPTIMIZE':",
     "options": ["Improve", "Deteriorate / Worsen", "Refine", "Calibrate"], "answer": 1},

    {"id": 12, "category": "Verbal Ability",
     "departments": ["All"], "roles": ["All"],
     "question": "Select the grammatically correct sentence:",
     "options": [
         "Neither the developers nor the manager were available.",
         "Neither the developers nor the manager was available.",
         "Neither the developers or the manager was available.",
         "Neither developer or manager were available."
     ], "answer": 1},

    {"id": 13, "category": "Verbal Ability",
     "departments": ["All"], "roles": ["All"],
     "question": "Fill in the blank: The microservice architecture is well-suited for applications that require high ________ and rapid deployments.",
     "options": ["scalability", "lethargy", "redundance", "stagnation"], "answer": 0},

    # ------------------ Data Interpretation (Targeted for Data / AI roles) ------------------
    {"id": 14, "category": "Data Interpretation",
     "departments": ["Data Science, Analytics & AI"],
     "roles": ["Data Analytics", "Data Analyst", "AI/ML Engineer", "Data Engineer"],
     "question": "A company's revenue increased from $50M in 2024 to $65M in 2025. What is the percentage growth?",
     "options": ["25%", "30%", "35%", "15%"], "answer": 1},

    {"id": 15, "category": "Data Interpretation",
     "departments": ["Data Science, Analytics & AI"],
     "roles": ["Data Analytics", "Data Analyst", "AI/ML Engineer", "Data Engineer"],
     "question": "In a dataset of 1,000 transactions, 80 are flagged as fraud. What is the precision of a filter that caught 100 alerts, of which 70 were genuine fraud?",
     "options": ["87.5%", "70.0%", "80.0%", "75.0%"], "answer": 1},

    {"id": 16, "category": "Data Interpretation",
     "departments": ["Data Science, Analytics & AI"],
     "roles": ["Data Analytics", "Data Analyst", "AI/ML Engineer", "Data Engineer"],
     "question": "A scatter plot shows points closely clustering around a line sloping downward from left to right. What does this indicate?",
     "options": ["Strong positive correlation", "Strong negative correlation", "Zero correlation", "Non-linear cyclic relation"], "answer": 1},

    {"id": 17, "category": "Data Interpretation",
     "departments": ["Data Science, Analytics & AI"],
     "roles": ["Data Analytics", "Data Analyst", "AI/ML Engineer", "Data Engineer"],
     "question": "If the mean of 5 numbers is 20, and 4 of the numbers are 15, 20, 25, and 10, what is the 5th number?",
     "options": ["25", "30", "35", "20"], "answer": 1},

    # ------------------ Pseudocode & Algorithmic Logic (Targeted for Software & QA) ------------------
    {"id": 18, "category": "Pseudocode & Logic",
     "departments": ["Software Engineering & Development", "Quality Assurance & Software Testing"],
     "roles": [
         "Software Development Engineer (SDE)", "Software Developer",
         "Full Stack Web Developer", "Frontend Developer", "Backend Developer",
         "Mobile App Developer", "QA Automation Engineer",
     ],
     "question": "What is the output of the following pseudocode?\ncount = 1;\nwhile (count < 10) {\n    count = count * 2;\n}\nprint(count);",
     "options": ["8", "10", "16", "32"], "answer": 2},

    {"id": 19, "category": "Pseudocode & Logic",
     "departments": ["Software Engineering & Development", "Quality Assurance & Software Testing"],
     "roles": [
         "Software Development Engineer (SDE)", "Software Developer",
         "Full Stack Web Developer", "Backend Developer", "QA Automation Engineer",
     ],
     "question": "A function calls itself recursively: f(n) = f(n-1) + f(n-2) with f(1)=1, f(2)=1. What is f(5)?",
     "options": ["3", "5", "8", "13"], "answer": 1},

    {"id": 20, "category": "Pseudocode & Logic",
     "departments": ["Software Engineering & Development", "Quality Assurance & Software Testing"],
     "roles": [
         "Software Development Engineer (SDE)", "Software Developer",
         "Full Stack Web Developer", "Frontend Developer", "Backend Developer",
     ],
     "question": "If an array has n elements, how many comparisons does binary search take in the worst case?",
     "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"], "answer": 1},

    {"id": 21, "category": "Pseudocode & Logic",
     "departments": ["Software Engineering & Development", "Quality Assurance & Software Testing"],
     "roles": [
         "Software Development Engineer (SDE)", "Software Developer",
         "QA Automation Engineer", "Backend Developer",
     ],
     "question": "Which logical statement is logically equivalent to NOT (A AND B)?",
     "options": ["(NOT A) AND (NOT B)", "(NOT A) OR (NOT B)", "NOT A OR B", "A OR NOT B"], "answer": 1},

    # ------------------ Systems & Network Diagnostics (Targeted for Cloud, Cyber, Admin) ------------------
    {"id": 22, "category": "System & Network Logic",
     "departments": ["Cloud, DevOps & Systems Infrastructure", "Cybersecurity & Information Security"],
     "roles": ["Cloud & DevOps Engineer", "Network & Systems Administrator", "Cybersecurity Analyst"],
     "question": "How many usable host IP addresses are available in an IPv4 subnet with mask /28 (255.255.255.240)?",
     "options": ["14", "16", "30", "32"], "answer": 0},

    {"id": 23, "category": "System & Network Logic",
     "departments": ["Cloud, DevOps & Systems Infrastructure", "Cybersecurity & Information Security"],
     "roles": ["Cloud & DevOps Engineer", "Network & Systems Administrator", "Cybersecurity Analyst"],
     "question": "A server can ping 8.8.8.8 successfully but fails to load 'google.com'. What is the most likely root cause?",
     "options": ["Default Gateway is down", "DNS resolution failure", "NIC hardware failure", "ARP table is full"], "answer": 1},

    {"id": 24, "category": "System & Network Logic",
     "departments": ["Cloud, DevOps & Systems Infrastructure", "Cybersecurity & Information Security"],
     "roles": ["Cloud & DevOps Engineer", "Network & Systems Administrator", "Cybersecurity Analyst"],
     "question": "In a 3-tier system (Web -> App -> DB), web users receive HTTP 504 Gateway Timeout. Which layer is most likely taking too long to respond?",
     "options": ["Client Browser", "Upstream Application or Database Server", "DNS root server", "Local ISP router"], "answer": 1},

    {"id": 25, "category": "System & Network Logic",
     "departments": ["Cloud, DevOps & Systems Infrastructure", "Cybersecurity & Information Security"],
     "roles": ["Cloud & DevOps Engineer", "Network & Systems Administrator", "Cybersecurity Analyst"],
     "question": "If a server's memory usage is 98% and swap usage is continuously rising, what phenomenon is likely occurring?",
     "options": ["Thrashing / Memory Exhaustion", "CPU Cache Miss", "Over-clocking", "Disk Fragmentation"], "answer": 0},
]


def get_questions(target_role: Optional[str] = None,
                  department: Optional[str] = None,
                  mode: str = "Targeted") -> List[Dict]:
    """
    Returns aptitude questions without the answer key.
    - If mode == 'Targeted' and target_role/department is given:
      Selects foundational questions (Quant, Logic, Verbal) plus specialized questions
      tailored to the target role/department.
    - If mode == 'All': Returns the full question bank.
    """
    if mode == "All" or (not target_role and not department):
        filtered = QUESTION_BANK
    else:
        role_norm = target_role or ""
        dept_norm = department or ""
        filtered = []
        for q in QUESTION_BANK:
            # Common questions
            if "All" in q.get("departments", []) or "All" in q.get("roles", []):
                filtered.append(q)
            # Department or Role matched questions
            elif (dept_norm and dept_norm in q.get("departments", [])) or \
                 (role_norm and any(r.lower() in role_norm.lower() or role_norm.lower() in r.lower() for r in q.get("roles", []))):
                filtered.append(q)

    return [{k: v for k, v in q.items() if k != "answer"} for q in filtered]


def score_aptitude_test(answers: Dict[int, int], student_id: int,
                        question_ids: Optional[List[int]] = None) -> Dict:
    """
    answers: {question_id: selected_option_index}
    question_ids: optional list of question IDs that were part of this test session.
                  If omitted, evaluates against questions present in answers, or the whole bank.
    Returns overall score (0-100) and per-category breakdown, saved to the database.
    """
    bank_map = {q["id"]: q for q in QUESTION_BANK}

    # Determine the questions to score against
    if question_ids:
        active_questions = [bank_map[qid] for qid in question_ids if qid in bank_map]
    elif answers:
        active_questions = [bank_map[qid] for qid in answers.keys() if qid in bank_map]
    else:
        active_questions = QUESTION_BANK

    if not active_questions:
        active_questions = QUESTION_BANK

    category_totals: Dict[str, List[int]] = {}  # category -> [correct_count, total_count]
    correct_count = 0

    for q in active_questions:
        cat = q["category"]
        category_totals.setdefault(cat, [0, 0])
        category_totals[cat][1] += 1
        if answers.get(q["id"]) == q["answer"]:
            category_totals[cat][0] += 1
            correct_count += 1

    overall_score = round(100 * correct_count / len(active_questions), 1) if active_questions else 0.0
    category_scores = {
        cat: round(100 * right / total, 1) for cat, (right, total) in category_totals.items()
    }

    save_aptitude_result(student_id, overall_score, category_scores)

    return {"overall_score": overall_score, "category_scores": category_scores}


if __name__ == "__main__":
    from database import init_db
    init_db()

    # Targeted test for Data Analyst
    da_questions = get_questions(target_role="Data Analyst", department="Data Science, Analytics & AI")
    print(f"Total questions for Data Analyst: {len(da_questions)}")
    sample_answers = {q["id"]: 1 for q in da_questions}
    res = score_aptitude_test(sample_answers, student_id=1, question_ids=[q["id"] for q in da_questions])
    print("Data Analyst Aptitude Result:", res)
