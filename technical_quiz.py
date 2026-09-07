"""
technical_quiz.py
------------------
Module 3 — Technical Quiz Module.

Purpose: Evaluate technical knowledge required for campus & off-campus IT
placements. Supports:
- Core IT departmental subjects (Operating Systems, DBMS, Computer Networks)
- Specialized technical topics aligned with each targeted job role
- Dynamic question generation and targeted scoring per role and department.

Topic names match the skill names in Module 6's ROLE_SKILL_MAP so results
feed directly into the Skill Gap Analysis.
"""

from typing import Dict, List, Optional
from database import save_quiz_result
from skill_gap_analysis import get_required_skills, get_department_for_role

# ---------------------------------------------------------------------------
# Comprehensive Technical Question Bank (Categorized by Skill & IT Topics)
# ---------------------------------------------------------------------------

QUESTION_BANK: List[Dict] = [
    # ------------------ Python ------------------
    {"id": 1, "topic": "Python", "departments": ["All"],
     "question": "Which keyword is used to define a function in Python?",
     "options": ["func", "def", "function", "lambda"], "answer": 1},
    {"id": 2, "topic": "Python", "departments": ["All"],
     "question": "What does len([1, 2, 3]) return?",
     "options": ["2", "3", "4", "Error"], "answer": 1},
    {"id": 3, "topic": "Python", "departments": ["All"],
     "question": "Which data type is immutable in Python?",
     "options": ["list", "dict", "tuple", "set"], "answer": 2},
    {"id": 4, "topic": "Python", "departments": ["All"],
     "question": "What will be the output of bool([]) in Python?",
     "options": ["True", "False", "None", "TypeError"], "answer": 1},

    # ------------------ SQL ------------------
    {"id": 5, "topic": "SQL", "departments": ["All"],
     "question": "Which SQL clause is used to filter grouped results produced by GROUP BY?",
     "options": ["WHERE", "HAVING", "ORDER BY", "LIMIT"], "answer": 1},
    {"id": 6, "topic": "SQL", "departments": ["All"],
     "question": "Which JOIN returns all rows from both tables, with NULL in unmatched columns?",
     "options": ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN"], "answer": 3},
    {"id": 7, "topic": "SQL", "departments": ["All"],
     "question": "Which keyword is used to eliminate duplicate rows from a query result?",
     "options": ["UNIQUE", "DISTINCT", "FILTER", "ISOLATE"], "answer": 1},
    {"id": 8, "topic": "SQL", "departments": ["All"],
     "question": "What is the primary difference between RANK() and DENSE_RANK() window functions?",
     "options": [
         "RANK() ignores NULL values",
         "RANK() skips ranks after ties; DENSE_RANK() does not skip",
         "DENSE_RANK() only works with text",
         "There is no difference"
     ], "answer": 1},

    # ------------------ Data Structures ------------------
    {"id": 9, "topic": "Data Structures", "departments": ["Software Engineering & Development"],
     "question": "Which data structure follows the LIFO (Last In First Out) principle?",
     "options": ["Queue", "Stack", "Linked List", "Tree"], "answer": 1},
    {"id": 10, "topic": "Data Structures", "departments": ["Software Engineering & Development"],
     "question": "What is the average time complexity of searching an element in a balanced Binary Search Tree (BST)?",
     "options": ["O(1)", "O(log n)", "O(n)", "O(n^2)"], "answer": 1},
    {"id": 11, "topic": "Data Structures", "departments": ["Software Engineering & Development"],
     "question": "Which data structure is ideal for implementing Breadth-First Search (BFS) on a graph?",
     "options": ["Stack", "Queue", "Max-Heap", "Trie"], "answer": 1},
    {"id": 12, "topic": "Data Structures", "departments": ["Software Engineering & Development"],
     "question": "What is the worst-case time complexity of QuickSort with poor pivot selection?",
     "options": ["O(n log n)", "O(n)", "O(n^2)", "O(log n)"], "answer": 2},

    # ------------------ Core IT: Database Management (DBMS) ------------------
    {"id": 13, "topic": "Database Management (DBMS)", "departments": ["All"],
     "question": "In the ACID acronym for database transactions, what does 'I' stand for?",
     "options": ["Integrity", "Isolation", "Indexing", "Inheritance"], "answer": 1},
    {"id": 14, "topic": "Database Management (DBMS)", "departments": ["All"],
     "question": "Which normal form resolves transitive dependencies on the primary key?",
     "options": ["1NF", "2NF", "3NF", "BCNF"], "answer": 2},
    {"id": 15, "topic": "Database Management (DBMS)", "departments": ["All"],
     "question": "Why is a B-Tree index commonly chosen over a hash index for database columns?",
     "options": [
         "B-Trees use zero memory",
         "B-Trees support range queries (BETWEEN, <, >) efficiently",
         "Hash indexes are deprecated",
         "B-Trees only work on string columns"
     ], "answer": 1},

    # ------------------ Core IT: Operating Systems ------------------
    {"id": 16, "topic": "Operating Systems", "departments": ["All"],
     "question": "What is the primary difference between a process and a thread?",
     "options": [
         "Threads have their own separate address space; processes do not",
         "Processes share memory automatically; threads do not",
         "Threads within the same process share code, data, and OS resources",
         "Processes are managed in user space only"
     ], "answer": 2},
    {"id": 17, "topic": "Operating Systems", "departments": ["All"],
     "question": "Which of the following conditions is NOT required for a deadlock to occur?",
     "options": ["Mutual Exclusion", "Hold and Wait", "Preemption Allowed", "Circular Wait"], "answer": 2},
    {"id": 18, "topic": "Operating Systems", "departments": ["All"],
     "question": "What occurs when the CPU spends more time swapping pages into and out of memory than executing code?",
     "options": ["Paging", "Thrashing", "Fragmentation", "Context Switching"], "answer": 1},

    # ------------------ Core IT: Computer Networks ------------------
    {"id": 19, "topic": "Computer Networks", "departments": ["All"],
     "question": "At which layer of the OSI model does the TCP protocol operate?",
     "options": ["Network Layer", "Transport Layer", "Data Link Layer", "Session Layer"], "answer": 1},
    {"id": 20, "topic": "Computer Networks", "departments": ["All"],
     "question": "What is the key functional difference between TCP and UDP?",
     "options": [
         "TCP is connectionless and faster",
         "TCP provides reliable, ordered, connection-oriented delivery; UDP is connectionless and lightweight",
         "UDP guarantees packet delivery without loss",
         "TCP cannot be used over the internet"
     ], "answer": 1},
    {"id": 21, "topic": "Computer Networks", "departments": ["All"],
     "question": "Which protocol is responsible for resolving a domain name (e.g. google.com) into an IP address?",
     "options": ["DHCP", "DNS", "ARP", "BGP"], "answer": 1},

    # ------------------ OOP & System Design ------------------
    {"id": 22, "topic": "OOP & System Design", "departments": ["Software Engineering & Development"],
     "question": "Which OOP principle allows a subclass to provide a specific implementation of a method already defined in its superclass?",
     "options": ["Abstraction", "Method Overriding (Polymorphism)", "Encapsulation", "Multiple Inheritance"], "answer": 1},
    {"id": 23, "topic": "OOP & System Design", "departments": ["Software Engineering & Development"],
     "question": "In distributed system design, what component sits between clients and servers to distribute incoming traffic evenly?",
     "options": ["Reverse Proxy / Load Balancer", "Message Queue", "Database Shard", "DNS Resolver"], "answer": 0},

    # ------------------ Web & Frontend (JavaScript / React / HTML / CSS) ------------------
    {"id": 24, "topic": "JavaScript / Web Tech", "departments": ["Software Engineering & Development"],
     "question": "What is the event loop's primary role in JavaScript?",
     "options": [
         "Compile code to machine language",
         "Continuously monitor the Call Stack and execute tasks from the Callback Queue",
         "Manage DOM tree painting",
         "Handle garbage collection only"
     ], "answer": 1},
    {"id": 25, "topic": "JavaScript / Web Tech", "departments": ["Software Engineering & Development"],
     "question": "What does the '===' operator check in JavaScript compared to '=='?",
     "options": [
         "Checks equality of values with automatic type conversion",
         "Checks strict equality of both value AND data type without coercion",
         "Checks memory reference identity only",
         "Checks if variables are assigned"
     ], "answer": 1},
    {"id": 26, "topic": "React / Frontend", "departments": ["Software Engineering & Development"],
     "question": "What is the purpose of React's useEffect hook?",
     "options": [
         "Directly modify the DOM tree",
         "Perform side effects (e.g. data fetching, subscriptions, timers) in functional components",
         "Store global application state",
         "Define CSS stylesheets"
     ], "answer": 1},
    {"id": 27, "topic": "React / Frontend", "departments": ["Software Engineering & Development"],
     "question": "Why does React use keys when rendering lists of items?",
     "options": [
         "To apply CSS styles to elements",
         "To help React identify which items have changed, been added, or removed for efficient DOM diffing",
         "To enforce uniqueness in database records",
         "To enable multi-threading"
     ], "answer": 1},
    {"id": 28, "topic": "HTML & CSS / UI Styling", "departments": ["Software Engineering & Development"],
     "question": "In the CSS box model, which property creates space outside the element's border?",
     "options": ["Padding", "Margin", "Outline", "Content"], "answer": 1},
    {"id": 29, "topic": "Web Performance", "departments": ["Software Engineering & Development"],
     "question": "What optimization technique ensures expensive functions (like search autocomplete) only execute after the user pauses typing?",
     "options": ["Throttling", "Debouncing", "Memoization", "Prefetching"], "answer": 1},

    # ------------------ Backend & APIs ------------------
    {"id": 30, "topic": "Backend APIs & Node", "departments": ["Software Engineering & Development"],
     "question": "Which HTTP status code signifies that a resource was successfully created on the server?",
     "options": ["200 OK", "201 Created", "204 No Content", "301 Moved Permanently"], "answer": 1},
    {"id": 31, "topic": "Backend APIs & Node", "departments": ["Software Engineering & Development"],
     "question": "In a RESTful architecture, what does it mean if an HTTP method (like GET or PUT) is idempotent?",
     "options": [
         "It returns results instantly",
         "Making multiple identical requests produces the exact same server state as making a single request",
         "It cannot be cached by proxy servers",
         "It requires an encrypted SSL session"
     ], "answer": 1},
    {"id": 32, "topic": "Web Security & Auth", "departments": ["Software Engineering & Development", "Cybersecurity & Information Security"],
     "question": "Which attack occurs when malicious script is injected into trusted websites and executed in the victim's browser?",
     "options": ["SQL Injection", "Cross-Site Scripting (XSS)", "CSRF", "DDoS"], "answer": 1},

    # ------------------ Mobile App Development ------------------
    {"id": 33, "topic": "Mobile App Development", "departments": ["Software Engineering & Development"],
     "question": "In Flutter, what is the key difference between a StatelessWidget and a StatefulWidget?",
     "options": [
         "StatelessWidget cannot display text",
         "StatefulWidget can rebuild its UI dynamically when internal mutable state changes",
         "StatelessWidget is only for iOS",
         "StatefulWidget cannot accept constructor parameters"
     ], "answer": 1},
    {"id": 34, "topic": "Mobile UI/UX", "departments": ["Software Engineering & Development"],
     "question": "Which Android lifecycle callback is called when the activity is no longer visible to the user?",
     "options": ["onPause()", "onStop()", "onDestroy()", "onResume()"], "answer": 1},

    # ------------------ Machine Learning & AI ------------------
    {"id": 35, "topic": "Machine Learning", "departments": ["Data Science, Analytics & AI"],
     "question": "Which metric is most appropriate for evaluating a classification model on an extremely imbalanced dataset (e.g. credit card fraud)?",
     "options": ["Raw Accuracy", "Precision-Recall AUC / F1-Score", "Mean Squared Error", "R-Squared"], "answer": 1},
    {"id": 36, "topic": "Machine Learning", "departments": ["Data Science, Analytics & AI"],
     "question": "What is the primary purpose of regularization techniques like L1 (Lasso) and L2 (Ridge)?",
     "options": [
         "Increase training speed",
         "Prevent overfitting by penalizing large model coefficients",
         "Eliminate the need for data cleaning",
         "Convert classification tasks to regression"
     ], "answer": 1},
    {"id": 37, "topic": "Deep Learning", "departments": ["Data Science, Analytics & AI"],
     "question": "Which neural network architecture is traditionally best suited for image recognition and computer vision tasks?",
     "options": ["Recurrent Neural Network (RNN)", "Convolutional Neural Network (CNN)", "Multilayer Perceptron (MLP)", "Autoencoder"], "answer": 1},
    {"id": 38, "topic": "Statistics", "departments": ["Data Science, Analytics & AI"],
     "question": "What does a p-value less than 0.05 typically indicate in statistical hypothesis testing?",
     "options": [
         "The null hypothesis is definitively true",
         "Statistically significant evidence to reject the null hypothesis",
         "The sample size was too small",
         "The alternative hypothesis has a 95% error rate"
     ], "answer": 1},
    {"id": 39, "topic": "Data Cleaning", "departments": ["Data Science, Analytics & AI"],
     "question": "When data has extreme outliers, which imputation strategy is more robust for missing numerical values?",
     "options": ["Mean imputation", "Median imputation", "Zero replacement", "Random number generation"], "answer": 1},
    {"id": 40, "topic": "Excel", "departments": ["Data Science, Analytics & AI"],
     "question": "Which Excel formula allows searching a table both vertically and horizontally without requiring the lookup column to be on the far left?",
     "options": ["VLOOKUP", "XLOOKUP", "HLOOKUP", "MATCH"], "answer": 1},
    {"id": 41, "topic": "Power BI / Tableau", "departments": ["Data Science, Analytics & AI"],
     "question": "In Power BI, what is the fundamental difference between a Calculated Column and a Measure?",
     "options": [
         "Measures are evaluated row-by-row during data load; Calculated Columns evaluate on the fly",
         "Calculated Columns consume RAM and compute at row level; Measures compute dynamically based on report filter context",
         "There is no difference",
         "Measures can only produce string outputs"
     ], "answer": 1},

    # ------------------ Big Data & Data Engineering ------------------
    {"id": 42, "topic": "Big Data & Spark", "departments": ["Data Science, Analytics & AI"],
     "question": "What is an RDD in Apache Spark?",
     "options": [
         "Relational Data Definition",
         "Resilient Distributed Dataset — an immutable, fault-tolerant distributed collection of objects",
         "Random Data Distribution",
         "Realtime Database Daemon"
     ], "answer": 1},
    {"id": 43, "topic": "Data Warehousing", "departments": ["Data Science, Analytics & AI"],
     "question": "In dimensional modeling, what schema consists of a central fact table connected directly to multiple dimension tables?",
     "options": ["Snowflake Schema", "Star Schema", "Galaxy Schema", "Relational 3NF"], "answer": 1},
    {"id": 44, "topic": "ETL Pipelines", "departments": ["Data Science, Analytics & AI"],
     "question": "What does the 'T' in ETL represent, and what is its primary responsibility?",
     "options": [
         "Transfer: Move data between hard drives",
         "Transform: Clean, standardize, aggregate, and enrich raw data into business-ready format",
         "Test: Run automated unit tests",
         "Truncate: Delete past data"
     ], "answer": 1},

    # ------------------ Cloud & DevOps ------------------
    {"id": 45, "topic": "Linux & Shell Scripting", "departments": ["Cloud, DevOps & Systems Infrastructure"],
     "question": "In Linux, what command is used to view running processes with dynamic real-time resource utilization?",
     "options": ["df -h", "top (or htop)", "chmod", "iptables"], "answer": 1},
    {"id": 46, "topic": "Docker & Containers", "departments": ["Cloud, DevOps & Systems Infrastructure"],
     "question": "What is the primary difference between a Docker container and a Virtual Machine (VM)?",
     "options": [
         "Containers package full guest operating systems with hypervisors",
         "Containers share the host OS kernel and isolate at the user-space level, making them much more lightweight than VMs",
         "VMs are faster to boot than containers",
         "Containers require dedicated hardware pass-through"
     ], "answer": 1},
    {"id": 47, "topic": "Kubernetes & Orchestration", "departments": ["Cloud, DevOps & Systems Infrastructure"],
     "question": "What is the smallest deployable computing unit in Kubernetes?",
     "options": ["Pod", "Node", "Cluster", "Service"], "answer": 0},
    {"id": 48, "topic": "CI/CD Pipelines", "departments": ["Cloud, DevOps & Systems Infrastructure"],
     "question": "What is Continuous Deployment (CD)?",
     "options": [
         "Manually approving code changes before production release",
         "Automatically releasing every change that passes the automated testing pipeline directly to production",
         "Deploying code once a year",
         "Writing unit tests continuously"
     ], "answer": 1},
    {"id": 49, "topic": "Cloud Platforms (AWS/Azure)", "departments": ["Cloud, DevOps & Systems Infrastructure"],
     "question": "In cloud computing, what is an IAM (Identity & Access Management) Role primarily used for?",
     "options": [
         "Assigning static root passwords to users",
         "Granting temporary, secure credentials and permissions to trusted entities or services without sharing long-term keys",
         "Calculating cloud billing costs",
         "Deploying virtual machines"
     ], "answer": 1},

    # ------------------ Cybersecurity & Information Security ------------------
    {"id": 50, "topic": "Network Security", "departments": ["Cybersecurity & Information Security"],
     "question": "What type of firewall inspects the state of active network connections rather than evaluating packets in total isolation?",
     "options": ["Packet Filtering Firewall", "Stateful Inspection Firewall", "Application Gateway only", "Circuit Proxy"], "answer": 1},
    {"id": 51, "topic": "Cryptography", "departments": ["Cybersecurity & Information Security"],
     "question": "Which algorithm is an example of asymmetric (public-key) cryptography?",
     "options": ["AES-256", "RSA", "DES", "Blowfish"], "answer": 1},
    {"id": 52, "topic": "Vulnerability Assessment", "departments": ["Cybersecurity & Information Security"],
     "question": "What is SQL Injection, and what is the primary defense against it?",
     "options": [
         "Inserting malicious SQL via user inputs; prevented by Parameterized Queries / Prepared Statements",
         "Cracking passwords via brute force; prevented by firewalls",
         "Flooding servers with SYN packets; prevented by load balancers",
         "Infecting files via email; prevented by antivirus"
     ], "answer": 0},
    {"id": 53, "topic": "Ethical Hacking & Web Security", "departments": ["Cybersecurity & Information Security"],
     "question": "What does the principle of 'Least Privilege' mandate?",
     "options": [
         "Every user should have Administrator privileges for productivity",
         "Users and services should be granted only the minimum permissions necessary to perform their assigned tasks",
         "Passwords should not exceed 8 characters",
         "Firewalls should be turned off in staging"
     ], "answer": 1},

    # ------------------ Quality Assurance & Software Testing ------------------
    {"id": 54, "topic": "Software Testing Principles", "departments": ["Quality Assurance & Software Testing"],
     "question": "What is Regression Testing?",
     "options": [
         "Testing a brand new software application for the first time",
         "Re-running tests to verify that recent code changes have not broken existing, working functionality",
         "Testing database backup integrity",
         "Testing physical server cooling"
     ], "answer": 1},
    {"id": 55, "topic": "Test Automation (Selenium)", "departments": ["Quality Assurance & Software Testing"],
     "question": "In Selenium WebDriver, which locator strategy is generally the fastest and most reliable for selecting web elements?",
     "options": ["XPath", "ID", "Class Name", "Link Text"], "answer": 1},
    {"id": 56, "topic": "API Testing", "departments": ["Quality Assurance & Software Testing"],
     "question": "When testing a REST API endpoint, what does status code 401 Unauthorized signify?",
     "options": [
         "The endpoint does not exist",
         "The request requires user authentication which was either missing or invalid",
         "The server experienced an internal crash",
         "The payload was too large"
     ], "answer": 1},
]


def get_questions_for_role(target_role: Optional[str] = None,
                           department: Optional[str] = None,
                           count: int = 15) -> List[Dict]:
    """
    Returns a tailored list of technical questions for the specified target role and department.
    Questions are selected from:
    1. Direct skills required for the role (from ROLE_SKILL_MAP)
    2. Core IT department fundamentals (DBMS, OS, Computer Networks)
    """
    if not target_role:
        return [{k: v for k, v in q.items() if k != "answer"} for q in QUESTION_BANK[:count]]

    try:
        req_skills = set(get_required_skills(target_role).keys())
    except Exception:
        req_skills = set()

    dept = department or get_department_for_role(target_role)

    # Filter into role-skill questions and IT core questions
    role_questions = []
    it_core_questions = []
    other_questions = []

    for q in QUESTION_BANK:
        t = q["topic"]
        if t in req_skills:
            role_questions.append(q)
        elif t in ["Database Management (DBMS)", "Operating Systems", "Computer Networks"]:
            it_core_questions.append(q)
        elif dept in q.get("departments", []) or "All" in q.get("departments", []):
            other_questions.append(q)

    # Compose questions: prioritize role-specific skills, then IT core foundations
    combined = role_questions + it_core_questions + other_questions
    # Deduplicate while preserving order
    seen_ids = set()
    selected = []
    for q in combined:
        if q["id"] not in seen_ids:
            seen_ids.add(q["id"])
            selected.append(q)
        if len(selected) >= count:
            break

    # If count not met, backfill from question bank
    if len(selected) < count:
        for q in QUESTION_BANK:
            if q["id"] not in seen_ids:
                seen_ids.add(q["id"])
                selected.append(q)
            if len(selected) >= count:
                break

    return [{k: v for k, v in q.items() if k != "answer"} for q in selected]


def get_questions() -> List[Dict]:
    """Default backward-compatible question fetcher."""
    return [{k: v for k, v in q.items() if k != "answer"} for q in QUESTION_BANK]


def score_technical_quiz(answers: Dict[int, int], student_id: int,
                         question_ids: Optional[List[int]] = None) -> Dict:
    """
    answers: {question_id: selected_option_index}
    question_ids: optional list of question IDs from this quiz session.
    Calculates technical score, topic breakdown, identifies weak areas, and saves to DB.
    """
    bank_map = {q["id"]: q for q in QUESTION_BANK}

    if question_ids:
        active_questions = [bank_map[qid] for qid in question_ids if qid in bank_map]
    elif answers:
        active_questions = [bank_map[qid] for qid in answers.keys() if qid in bank_map]
    else:
        active_questions = QUESTION_BANK[:15]

    topic_totals: Dict[str, List[int]] = {}
    correct_count = 0

    for q in active_questions:
        topic = q["topic"]
        topic_totals.setdefault(topic, [0, 0])
        topic_totals[topic][1] += 1
        if answers.get(q["id"]) == q["answer"]:
            topic_totals[topic][0] += 1
            correct_count += 1

    topic_scores = {
        t: round(100 * right / total, 1) for t, (right, total) in topic_totals.items()
    }
    overall_score = round(100 * correct_count / len(active_questions), 1) if active_questions else 0.0
    weak_topics = [t for t, s in topic_scores.items() if s < 50]

    if weak_topics:
        feedback = f"Attempt completed ({overall_score}%). Focus dedicated practice on: {', '.join(weak_topics)}."
    else:
        feedback = f"Exceptional performance ({overall_score}%)! Strong foundation across all tested topics."

    save_quiz_result(student_id, topic_scores, weak_topics, feedback)

    return {
        "overall_score": overall_score,
        "topic_scores": topic_scores,
        "weak_topics": weak_topics,
        "feedback": feedback,
    }


if __name__ == "__main__":
    from database import init_db
    init_db()

    q_sde = get_questions_for_role("Software Development Engineer (SDE)")
    print(f"Loaded {len(q_sde)} questions for SDE")
    sample_answers = {q["id"]: 1 for q in q_sde}
    res = score_technical_quiz(sample_answers, student_id=1, question_ids=[q["id"] for q in q_sde])
    print("SDE Quiz Result:", res["overall_score"], res["topic_scores"])
