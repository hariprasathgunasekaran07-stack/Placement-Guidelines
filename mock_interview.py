"""
mock_interview.py
------------------
Module 4 — AI Mock Interview Module.

Workflow:
  Select Job Role & Department -> Question Generated -> Student Provides Answer
  -> LLM / Heuristic Evaluates Answer -> Feedback & Scoring

Features:
- Full skill-coverage across all 5 IT departments and 11 targeted roles
- Context-aware question generation (role, department, and technical skill)
- Realistic IT departmental scenario questions
- LLM generation via Gemini (with automatic graceful fallback to an extensive
  keyword-evaluated fallback question bank if running offline).
"""

import re
from typing import Dict, List, Optional, Tuple

from config import USE_LLM, get_model
from database import save_interview_result

# ---------------------------------------------------------------------------
# Fallback Question Bank — Comprehensive questions for all skills & roles
# ---------------------------------------------------------------------------

FALLBACK_QUESTIONS: Dict[str, List[str]] = {
    # Programming & Core Software
    "Python": [
        "Explain the difference between a list and a tuple in Python.",
        "What are Python decorators, and how do they work under the hood?",
        "How does Python manage memory, and what is the role of the GIL (Global Interpreter Lock)?",
    ],
    "Data Structures": [
        "When would you choose a hash map over a balanced binary search tree?",
        "Explain how you would detect a cycle in a singly linked list.",
        "What is the difference between BFS and DFS, and when would you use each?",
    ],
    "OOP & System Design": [
        "Explain the four core principles of OOP with real-world software examples.",
        "How would you design a rate limiter for an API with millions of users?",
        "What is the difference between horizontal and vertical scaling?",
    ],
    "System Design": [
        "Explain how database indexing works and when an index might degrade write performance.",
        "What caching strategies (e.g. Cache-Aside, Write-Through) would you use for a high-traffic app?",
    ],

    # Web & Frontend
    "JavaScript / Web Tech": [
        "Explain how the JavaScript event loop handles asynchronous operations, microtasks, and macrotasks.",
        "What is the difference between '==' and '===' in JavaScript, and what is variable hoisting?",
    ],
    "React / Frontend": [
        "Explain the Virtual DOM in React and how the reconciliation process improves UI rendering.",
        "What is the difference between state and props, and when would you use useMemo vs useCallback?",
    ],
    "HTML & CSS / UI Styling": [
        "Explain the CSS box model and the difference between Flexbox and CSS Grid.",
        "How do media queries and responsive design units (rem, em, vh, vw) differ?",
    ],
    "Web Performance": [
        "What key strategies would you implement to improve Core Web Vitals (LCP, FID/INP, CLS)?",
        "How does lazy loading and code splitting optimize frontend bundle sizes?",
    ],

    # Backend & APIs
    "Backend APIs & Node": [
        "What are the core design principles of a RESTful API, and what makes an HTTP method idempotent?",
        "How does Node.js achieve high concurrency despite running on a single main thread?",
    ],
    "Web Security & Auth": [
        "What is the difference between Authentication and Authorization, and how do JWTs work?",
        "How do you protect a web application from Cross-Site Scripting (XSS) and CSRF attacks?",
    ],

    # Mobile App Development
    "Mobile App Development": [
        "Explain the lifecycle of a mobile application screen (e.g., in Android or Flutter).",
        "How do you manage offline data caching and synchronization in a mobile app?",
    ],
    "Mobile UI/UX": [
        "What considerations do you prioritize when designing mobile UI across varying screen resolutions?",
        "How do you handle background tasks and push notifications without draining battery life?",
    ],
    "State Management": [
        "Compare local state management versus global state management (e.g., Provider/Bloc/Redux) in mobile applications.",
    ],
    "REST APIs": [
        "How do you structure API error handling and pagination when consuming endpoints on mobile or web clients?",
    ],

    # Core IT Foundations
    "Database Management (DBMS)": [
        "Explain ACID properties in database transactions and what happens if Atomicity fails.",
        "What are database normalization (1NF, 2NF, 3NF) and when might you intentionally denormalize?",
    ],
    "Operating Systems": [
        "Explain the fundamental difference between a process and a thread, and how context switching works.",
        "What is virtual memory and paging, and what causes thrashing in an OS?",
    ],
    "Computer Networks": [
        "Walk through what happens under the hood when a user types 'https://www.google.com' into a browser.",
        "What is the difference between TCP and UDP, and in what scenarios is UDP preferred?",
    ],

    # Data Science, Analytics & AI
    "SQL": [
        "What is the difference between INNER JOIN, LEFT JOIN, and FULL OUTER JOIN?",
        "How do SQL window functions (like ROW_NUMBER and RANK) differ from standard GROUP BY aggregations?",
    ],
    "Statistics": [
        "Explain the difference between mean, median, and mode, and which is preferred for skewed data.",
        "What is a p-value in hypothesis testing, and what does a p-value < 0.05 signify?",
    ],
    "Machine Learning": [
        "Explain the bias-variance tradeoff and how it relates to overfitting and underfitting.",
        "How do you evaluate a classification model when the dataset has severe class imbalance?",
    ],
    "Deep Learning": [
        "Explain how backpropagation and gradient descent update weights in a neural network.",
        "What are Convolutional Neural Networks (CNNs) and why are they effective for image processing?",
    ],
    "Model Deployment": [
        "What are the key steps and challenges in serving a machine learning model via a production REST API?",
    ],
    "Big Data & Spark": [
        "What is Apache Spark's RDD architecture, and how does lazy evaluation optimize computation graphs?",
        "Explain data partitioning in distributed systems and how data skew impacts Spark job performance.",
    ],
    "Data Warehousing": [
        "Compare Star Schema versus Snowflake Schema in analytical data warehouse design.",
    ],
    "ETL Pipelines": [
        "How do you ensure data quality and handle pipeline failures in high-volume batch ETL jobs?",
    ],
    "Excel": [
        "How would you use XLOOKUP or INDEX-MATCH to merge data across multiple worksheets?",
        "What is a Pivot Table, and how do you use calculated fields to summarize metrics?",
    ],
    "Power BI / Tableau": [
        "How do you design an executive dashboard that highlights trends while enabling interactive drill-downs?",
        "In Power BI, what is the difference between a Calculated Column and a Measure?",
    ],
    "Data Cleaning": [
        "How do you identify and handle missing values, duplicate records, and outliers in a messy dataset?",
        "What steps do you take to validate data consistency before exploratory analysis?",
    ],

    # Cloud & DevOps
    "Linux & Shell Scripting": [
        "How do file permissions (chmod, chown) work in Linux, and how would you find processes consuming high memory?",
        "How do you write a bash script to monitor a background service and restart it upon failure?",
    ],
    "Docker & Containers": [
        "What is the difference between a Docker image and a Docker container, and how do layers work?",
        "How do Docker volumes provide persistent storage for containers?",
    ],
    "Kubernetes & Orchestration": [
        "What is the role of Pods, Deployments, and Services in a Kubernetes cluster?",
        "How does Kubernetes handle automatic self-healing and rolling updates for application workloads?",
    ],
    "CI/CD Pipelines": [
        "Describe a complete CI/CD pipeline from code commit to production deployment.",
        "How do automated testing and canary/blue-green deployments minimize deployment risk?",
    ],
    "Cloud Platforms (AWS/Azure)": [
        "Explain the difference between IaaS, PaaS, and Serverless compute (e.g. AWS Lambda).",
        "What is the purpose of VPCs, Subnets, and Security Groups in cloud infrastructure?",
    ],
    "Troubleshooting & Diagnostics": [
        "A web server returns HTTP 504 Gateway Timeout. What diagnostic commands and logs would you inspect?",
    ],

    # Cybersecurity
    "Network Security": [
        "Explain the difference between a stateful firewall and an Intrusion Detection/Prevention System (IDS/IPS).",
        "How does a VPN establish a secure encrypted tunnel across public networks?",
    ],
    "Ethical Hacking & Web Security": [
        "Explain how SQL Injection works and how parameterized queries prevent it.",
        "What are the top vulnerabilities in the OWASP Top 10, and how do you remediate them?",
    ],
    "Cryptography": [
        "What is the fundamental difference between symmetric encryption (AES) and asymmetric encryption (RSA)?",
        "What is the difference between hashing and encryption, and why are passwords salted?",
    ],
    "Vulnerability Assessment": [
        "How do CVSS vulnerability scoring and automated scanning tools help prioritize security patches?",
    ],

    # Quality Assurance & Testing
    "Software Testing Principles": [
        "Explain the difference between smoke testing, regression testing, and boundary value analysis.",
        "What is the difference between verification and validation in software engineering?",
    ],
    "Test Automation (Selenium)": [
        "What is the Page Object Model (POM) in Selenium, and why is it recommended for maintainability?",
        "How do implicit waits and explicit waits differ when automating dynamic single-page web apps?",
    ],
    "API Testing": [
        "How do you design automated test suites for REST APIs using tools like Postman or REST Assured?",
    ],

    # Communication & Department Behavioral
    "Communication": [
        "Describe a situation where you had to explain a complex technical issue or data insight to non-technical stakeholders.",
        "How do you handle technical disagreements during a code review or architectural discussion?",
    ],
}

# ---------------------------------------------------------------------------
# Keywords a strong answer should touch on (for rule-based scoring)
# ---------------------------------------------------------------------------

_EXPECTED_KEYWORDS: Dict[str, List[str]] = {
    "Explain the difference between a list and a tuple in Python.": ["mutable", "immutable", "list", "tuple", "memory", "hash"],
    "What are Python decorators, and how do they work under the hood?": ["function", "wrap", "decorator", "@", "closure", "argument"],
    "How does Python manage memory, and what is the role of the GIL (Global Interpreter Lock)?": ["gil", "thread", "memory", "garbage", "reference"],
    "When would you choose a hash map over a balanced binary search tree?": ["o(1)", "o(log n)", "hash", "tree", "order", "collision"],
    "Explain how you would detect a cycle in a singly linked list.": ["floyd", "slow", "fast", "pointer", "hash", "node"],
    "What is the difference between BFS and DFS, and when would you use each?": ["queue", "stack", "breadth", "depth", "level", "shortest"],
    "Explain the four core principles of OOP with real-world software examples.": ["encapsulation", "inheritance", "polymorphism", "abstraction"],
    "How would you design a rate limiter for an API with millions of users?": ["token", "leaky", "redis", "sliding", "window", "limit"],
    "What is the difference between horizontal and vertical scaling?": ["cpu", "ram", "server", "cluster", "distributed", "load balancer"],
    "Explain how database indexing works and when an index might degrade write performance.": ["b-tree", "lookup", "write", "insert", "index", "disk"],
    "What caching strategies (e.g. Cache-Aside, Write-Through) would you use for a high-traffic app?": ["cache", "redis", "read", "write", "ttl", "hit"],
    "Explain how the JavaScript event loop handles asynchronous operations, microtasks, and macrotasks.": ["call stack", "queue", "promise", "microtask", "callback", "event loop"],
    "What is the difference between '==' and '===' in JavaScript, and what is variable hoisting?": ["type", "coercion", "strict", "declaration", "hoist", "scope"],
    "Explain the Virtual DOM in React and how the reconciliation process improves UI rendering.": ["virtual dom", "diff", "reconcil", "render", "state", "batch"],
    "What is the difference between state and props, and when would you use useMemo vs useCallback?": ["mutable", "parent", "child", "memo", "callback", "render"],
    "Explain the CSS box model and the difference between Flexbox and CSS Grid.": ["content", "padding", "border", "margin", "flex", "grid", "1d", "2d"],
    "What key strategies would you implement to improve Core Web Vitals (LCP, FID/INP, CLS)?": ["lazy", "bundle", "cache", "lcp", "cls", "image", "cdn"],
    "What are the core design principles of a RESTful API, and what makes an HTTP method idempotent?": ["stateless", "http", "idempotent", "get", "put", "post", "resource"],
    "How does Node.js achieve high concurrency despite running on a single main thread?": ["event loop", "non-blocking", "async", "i/o", "libuv", "callback"],
    "What is the difference between Authentication and Authorization, and how do JWTs work?": ["who", "permission", "token", "signature", "header", "payload"],
    "How do you protect a web application from Cross-Site Scripting (XSS) and CSRF attacks?": ["sanitize", "encode", "token", "cookie", "samesite", "escape"],
    "Explain the lifecycle of a mobile application screen (e.g., in Android or Flutter).": ["create", "start", "resume", "pause", "stop", "destroy"],
    "Explain ACID properties in database transactions and what happens if Atomicity fails.": ["atomicity", "consistency", "isolation", "durability", "rollback", "commit"],
    "What are database normalization (1NF, 2NF, 3NF) and when might you intentionally denormalize?": ["redundancy", "dependency", "primary key", "foreign key", "join", "read"],
    "Explain the fundamental difference between a process and a thread, and how context switching works.": ["memory", "address space", "share", "cpu", "overhead", "register"],
    "What is virtual memory and paging, and what causes thrashing in an OS?": ["page", "swap", "frame", "mmu", "thrashing", "disk"],
    "Walk through what happens under the hood when a user types 'https://www.google.com' into a browser.": ["dns", "tcp", "handshake", "tls", "http", "ip", "render"],
    "What is the difference between TCP and UDP, and in what scenarios is UDP preferred?": ["reliable", "ordered", "connection", "fast", "packet", "streaming", "loss"],
    "What is the difference between INNER JOIN, LEFT JOIN, and FULL OUTER JOIN?": ["match", "null", "left", "both", "table", "unmatched"],
    "How do SQL window functions (like ROW_NUMBER and RANK) differ from standard GROUP BY aggregations?": ["partition", "over", "individual", "aggregate", "collapse", "row"],
    "Explain the difference between mean, median, and mode, and which is preferred for skewed data.": ["average", "middle", "frequent", "skew", "outlier", "median"],
    "What is a p-value in hypothesis testing, and what does a p-value < 0.05 signify?": ["null", "hypothesis", "significance", "probability", "reject", "0.05"],
    "Explain the bias-variance tradeoff and how it relates to overfitting and underfitting.": ["overfit", "underfit", "bias", "variance", "complexity", "generaliz"],
    "How do you evaluate a classification model when the dataset has severe class imbalance?": ["precision", "recall", "f1", "auc", "roc", "accuracy"],
    "Explain how backpropagation and gradient descent update weights in a neural network.": ["gradient", "loss", "chain rule", "weight", "derivative", "learning rate"],
    "What are Convolutional Neural Networks (CNNs) and why are they effective for image processing?": ["filter", "kernel", "convolution", "pooling", "feature", "spatial"],
    "What is Apache Spark's RDD architecture, and how does lazy evaluation optimize computation graphs?": ["rdd", "distributed", "dag", "lazy", "transformation", "action"],
    "Compare Star Schema versus Snowflake Schema in analytical data warehouse design.": ["fact", "dimension", "normalize", "query", "star", "snowflake"],
    "How do you ensure data quality and handle pipeline failures in high-volume batch ETL jobs?": ["validation", "idempotent", "retry", "alert", "schema", "lineage"],
    "How would you use XLOOKUP or INDEX-MATCH to merge data across multiple worksheets?": ["lookup", "index", "match", "column", "return", "exact"],
    "What is a Pivot Table, and how do you use calculated fields to summarize metrics?": ["aggregate", "dimension", "measure", "group", "filter", "summary"],
    "How do you identify and handle missing values, duplicate records, and outliers in a messy dataset?": ["impute", "drop", "null", "mean", "median", "duplicate", "outlier"],
    "How do file permissions (chmod, chown) work in Linux, and how would you find processes consuming high memory?": ["read", "write", "execute", "top", "ps", "permission", "user"],
    "What is the difference between a Docker image and a Docker container, and how do layers work?": ["image", "container", "runtime", "layer", "isolated", "blueprint"],
    "What is the role of Pods, Deployments, and Services in a Kubernetes cluster?": ["pod", "deployment", "service", "replica", "cluster", "network", "node"],
    "Describe a complete CI/CD pipeline from code commit to production deployment.": ["build", "test", "lint", "artifact", "deploy", "pipeline", "automated"],
    "Explain the difference between IaaS, PaaS, and Serverless compute (e.g. AWS Lambda).": ["infrastructure", "platform", "serverless", "manage", "cloud", "scaling"],
    "Explain the difference between a stateful firewall and an Intrusion Detection/Prevention System (IDS/IPS).": ["packet", "state", "connection", "signature", "anomaly", "block", "alert"],
    "Explain how SQL Injection works and how parameterized queries prevent it.": ["input", "malicious", "sql", "parameter", "sanitize", "prepared statement"],
    "What is the fundamental difference between symmetric encryption (AES) and asymmetric encryption (RSA)?": ["single", "public", "private", "key", "aes", "rsa", "speed"],
    "Explain the difference between smoke testing, regression testing, and boundary value analysis.": ["smoke", "regression", "break", "boundary", "edge", "verify"],
    "What is the Page Object Model (POM) in Selenium, and why is it recommended for maintainability?": ["page", "locator", "reuse", "maintain", "class", "separation"],
    "When testing a REST API endpoint, what does status code 401 Unauthorized signify?": ["auth", "token", "permission", "invalid", "credential"],
    "Describe a situation where you had to explain a complex technical issue or data insight to non-technical stakeholders.": ["stakeholder", "clear", "business", "analogy", "visual", "impact"],
    "How do you handle technical disagreements during a code review or architectural discussion?": ["listen", "data", "tradeoff", "collaborat", "standard", "respect"],
}


def generate_question(skill: str, role: Optional[str] = None, department: Optional[str] = None) -> str:
    """
    Generates a targeted interview question:
    - LLM path: Gemini drafts a contextual technical question for the specific role & skill.
    - Fallback path: Selects a question from the comprehensive fallback bank for that skill.
    """
    if USE_LLM:
        try:
            model = get_model()
            role_ctx = f" for a candidate interviewing for the role of '{role}'" if role else ""
            dept_ctx = f" in the '{department}' department" if department else ""
            prompt = (
                f"You are a technical hiring manager{dept_ctx}. Ask ONE clear, realistic interview question "
                f"to test the candidate's practical expertise in {skill}{role_ctx}. "
                f"Output ONLY the question text without any greeting, labels, or preamble."
            )
            q = model.generate_content(prompt).text.strip()
            if q:
                return q
        except Exception:
            pass  # gracefully drop to fallback

    # Fallback path
    bank = FALLBACK_QUESTIONS.get(skill)
    if bank:
        return bank[0]
    return f"Explain how you have practically utilized {skill} in your projects or coursework."


def evaluate_answer(question: str, answer: str, skill: str = "") -> Tuple[float, str]:
    """
    Evaluates the candidate's answer:
    - LLM path: Gemini provides an objective score (0-100) and actionable 1-2 sentence feedback.
    - Fallback path: Keyword-density and answer-depth analysis based on technical terms.
    """
    if not answer or not answer.strip():
        return 0.0, "No answer provided. In an interview, attempt to structure your thoughts even if partially sure."

    if USE_LLM:
        try:
            model = get_model()
            prompt = (
                f"Question: {question}\n"
                f"Candidate's Answer: {answer}\n\n"
                f"You are evaluating this response for technical accuracy, clarity, and depth. "
                f"Score from 0 to 100.\n"
                f"Output your response strictly in the following format:\n"
                f"SCORE: <number between 0 and 100>\n"
                f"FEEDBACK: <1 to 2 sentences of constructive feedback highlighting strengths or gaps>"
            )
            text = model.generate_content(prompt).text.strip()
            score_match = re.search(r"SCORE:\s*(\d+)", text)
            feedback_match = re.search(r"FEEDBACK:\s*(.+)", text, re.DOTALL)
            score = float(score_match.group(1)) if score_match else 60.0
            feedback = feedback_match.group(1).strip() if feedback_match else text
            return min(100.0, max(0.0, score)), feedback
        except Exception:
            pass

    # Heuristic fallback evaluation
    expected = _EXPECTED_KEYWORDS.get(question, [])
    if not expected and skill:
        # Fallback keyword extraction from any matching bank question
        for q_key, kws in _EXPECTED_KEYWORDS.items():
            if skill.lower() in q_key.lower():
                expected = kws
                break

    answer_lower = answer.lower()
    words = answer.split()
    word_count = len(words)

    if expected:
        hits = sum(1 for kw in expected if kw in answer_lower)
        keyword_score = (hits / min(len(expected), 4)) * 60  # up to 60 pts from key concepts
    else:
        # General technical presence signal
        keyword_score = 40.0

    length_score = min(40.0, word_count * 1.2)  # up to 40 pts for completeness
    score = round(min(100.0, keyword_score + length_score), 1)

    if score >= 75:
        feedback = "Excellent response — you demonstrated solid conceptual clarity and covered key technical terms."
    elif score >= 50:
        feedback = "Good attempt — you captured the core premise, but elaborating with practical details or edge cases would strengthen it."
    else:
        feedback = "Needs improvement — review the fundamental concepts for this topic and aim for more precise technical explanations."

    return score, feedback


def run_mock_interview(student_id: int, role: str, skills: List[str],
                       answers: Dict[str, str], department: Optional[str] = None) -> Dict:
    """
    Executes a complete mock interview session for the candidate.
    - skills: list of skills to evaluate
    - answers: {skill: student's answer text}
    Logs question, answer, score, and feedback, saving results to database.
    """
    qa_log = []
    skill_scores: Dict[str, float] = {}

    for skill in skills:
        question = generate_question(skill, role=role, department=department)
        answer = answers.get(skill, "")
        score, feedback = evaluate_answer(question, answer, skill=skill)
        skill_scores[skill] = score
        qa_log.append({
            "skill": skill,
            "question": question,
            "answer": answer,
            "score": score,
            "feedback": feedback,
        })

    overall_score = (
        round(sum(skill_scores.values()) / len(skill_scores), 1)
        if skill_scores else 0.0
    )

    save_interview_result(student_id, role, qa_log, skill_scores, overall_score)

    return {
        "role": role,
        "department": department,
        "qa_log": qa_log,
        "skill_scores": skill_scores,
        "overall_score": overall_score,
    }


if __name__ == "__main__":
    from database import init_db
    init_db()

    answers = {
        "Python": "Lists are mutable and tuples are immutable in Python.",
        "Computer Networks": "TCP is connection oriented with 3-way handshake, UDP is connectionless and fast.",
    }
    res = run_mock_interview(
        student_id=1,
        role="Software Development Engineer (SDE)",
        skills=list(answers.keys()),
        answers=answers,
        department="Software Engineering & Development",
    )
    print("Mock Interview Result:", res["overall_score"])
    for item in res["qa_log"]:
        print(f"[{item['skill']}] Score: {item['score']} | {item['feedback']}")
