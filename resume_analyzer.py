"""
resume_analyzer.py
-------------------
Module 5 — Resume Analyzer Module.

Purpose: Analyze the student's resume and provide improvement
suggestions. Also extracts a skill-confidence map used later by Module 6
(Skill Gap Analysis) as the "claimed skills" signal.

Accepts either a raw text resume or a PDF file path (extracted via
PyPDF2). Falls back to a rule-based checklist analyzer when no LLM key
is configured.
"""

import json
import re
import zlib
from typing import Dict, List

from config import USE_LLM, get_model
from database import save_resume_analysis


def _fallback_stream_extract(file_path: str) -> str:
    """Pure-Python fallback PDF text extractor using Python standard library (re + zlib)."""
    try:
        with open(file_path, "rb") as f:
            content = f.read()

        extracted_chunks = []
        stream_pattern = re.compile(rb"stream[\r\n]+(.*?)[\r\n]+endstream", re.DOTALL)
        for match in stream_pattern.finditer(content):
            stream_data = match.group(1)
            decompressed = None
            try:
                decompressed = zlib.decompress(stream_data)
            except Exception:
                try:
                    decompressed = zlib.decompress(stream_data, -15)
                except Exception:
                    decompressed = stream_data

            if decompressed:
                # Matches literal text in PDF text operators like (Hello) Tj
                tj_matches = re.findall(rb"\((.*?)\)\s*Tj", decompressed)
                for tj in tj_matches:
                    try:
                        t = tj.decode("latin1", errors="ignore").strip()
                        if t:
                            extracted_chunks.append(t)
                    except Exception:
                        pass

                # Matches text arrays like [(Hello) 10 (World)] TJ
                tj_arrays = re.findall(rb"\[(.*?)\]\s*TJ", decompressed)
                for arr in tj_arrays:
                    parts = re.findall(rb"\((.*?)\)", arr)
                    for p in parts:
                        try:
                            t = p.decode("latin1", errors="ignore").strip()
                            if t:
                                extracted_chunks.append(t)
                        except Exception:
                            pass

        if extracted_chunks:
            return " ".join(extracted_chunks)

        # Basic ASCII string scanner if streams are uncompressed
        words = re.findall(rb"[A-Za-z0-9@.,/:\-+]{3,}", content)
        if words:
            filtered = [
                w.decode("latin1", errors="ignore")
                for w in words
                if w.lower() not in (
                    b"obj", b"endobj", b"stream", b"endstream", b"xref",
                    b"trailer", b"font", b"type", b"flatedecode"
                )
            ]
            if len(filtered) > 20:
                return " ".join(filtered)
    except Exception:
        pass
    return ""


def extract_text_from_pdf(file_path: str) -> str:
    """Extracts raw text from a PDF resume.
    Tries PyPDF2 -> pypdf -> pdfminer -> pure-Python standard library stream extractor.
    """
    # 1. Try PyPDF2
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        if text.strip():
            return text
    except Exception:
        pass

    # 2. Try pypdf (modern replacement)
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        if text.strip():
            return text
    except Exception:
        pass

    # 3. Try pdfminer if present
    try:
        from pdfminer.high_level import extract_text as pdfminer_extract
        text = pdfminer_extract(file_path)
        if text.strip():
            return text
    except Exception:
        pass

    # 4. Built-in zero-dependency stream extractor
    fallback_text = _fallback_stream_extract(file_path)
    if fallback_text.strip():
        return fallback_text

    raise RuntimeError(
        "Could not extract readable text from the uploaded PDF. "
        "Please install PyPDF2 by running 'pip install PyPDF2' or copy & paste your resume text into the text box."
    )


def extract_skills(resume_text: str, candidate_skills: List[str]) -> Dict[str, int]:
    """Same evidence-quality scoring used by Module 6 — kept here too so
    the Resume Analyzer can show extracted skills on its own, before the
    student even reaches the Skill Gap Analysis step."""
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


def generate_suggestions(resume_text: str, target_role: str) -> str:
    """LLM path: Gemini reviews the resume against the target role.
    Fallback path: a rule-based checklist covering common resume issues
    (missing quantifiable results, missing projects section, length, etc.)."""
    if USE_LLM:
        model = get_model()
        prompt = (f"You are a resume reviewer. The candidate is targeting the role: {target_role}.\n"
                  f"Resume:\n\"\"\"{resume_text}\"\"\"\n\n"
                  f"Give 4-6 concise, actionable improvement suggestions as a bulleted list.")
        return model.generate_content(prompt).text.strip()

    suggestions = []
    lower = resume_text.lower()

    if not re.search(r"\d+%|\d+x|\$\d|₹\d|\d+ (users|customers|projects|hours|days)", lower):
        suggestions.append("Add quantifiable achievements (e.g. 'reduced processing latency by 30%') "
                           "instead of just listing job duties.")
    if "project" not in lower:
        suggestions.append("Add a dedicated Projects section — placement recruiters weight "
                           "hands-on project implementation heavily.")
    if "github" not in lower and ("developer" in target_role.lower() or "sde" in target_role.lower() or "engineer" in target_role.lower()):
        suggestions.append("Include links to your GitHub profile and live project demos to prove code quality.")
    if "data" in target_role.lower() or "ai" in target_role.lower():
        if "kaggle" not in lower and "tableau" not in lower and "power bi" not in lower:
            suggestions.append("Highlight links to Kaggle notebooks, Tableau Public, or interactive data dashboards.")
    if "cloud" in target_role.lower() or "devops" in target_role.lower() or "security" in target_role.lower():
        if "certif" not in lower and "aws" not in lower and "docker" not in lower:
            suggestions.append("Highlight practical cloud labs, Docker containerization, or relevant industry certifications (AWS, CompTIA, etc.).")
    if "qa" in target_role.lower() or "test" in target_role.lower():
        if "selenium" not in lower and "automation" not in lower and "api" not in lower:
            suggestions.append("Explicitly specify automated testing frameworks (Selenium/Cypress) and API testing tools (Postman).")
    if "education" not in lower and "b.tech" not in lower and "degree" not in lower:
        suggestions.append("Make sure your degree, university, and GPA details are clearly formatted.")
    if len(resume_text.split()) < 120:
        suggestions.append("Your resume appears brief — add detail about tech stacks, methodologies (Agile/Git), and project results.")
    if "skills" not in lower:
        suggestions.append("Include a dedicated Technical Skills section with categorize bullet points for ATS scanner readability.")
    if not suggestions:
        suggestions.append(f"Strong resume foundations — tailor keywords specifically to the job descriptions for {target_role}.")

    return "\n".join(f"- {s}" for s in suggestions)


def analyze_resume(student_id: int, resume_text: str, target_role: str,
                    candidate_skills: List[str]) -> Dict:
    extracted_skills = extract_skills(resume_text, candidate_skills)
    suggestions = generate_suggestions(resume_text, target_role)

    save_resume_analysis(student_id, resume_text, extracted_skills, suggestions)

    return {"extracted_skills": extracted_skills, "suggestions": suggestions}


if __name__ == "__main__":
    from database import init_db
    init_db()

    sample_resume = """
    Bharath Kumar S — B.Tech AI & Data Science student.
    Completed Python Intermediate course (30 days). Completed Data
    Analytics basics masterclass (30 days). Used Python and pandas to
    build a data cleaning project for college coursework. Familiar with
    SQL and Excel. Skills: Python, SQL, Excel, Data Cleaning, Statistics.
    """

    result = analyze_resume(
        student_id=1,
        resume_text=sample_resume,
        target_role="Data Analyst",
        candidate_skills=["Python", "SQL", "Excel", "Statistics", "Power BI / Tableau",
                          "Data Cleaning", "Communication"],
    )
    print("Resume Analysis Result:")
    print(f"  Extracted Skills: {result['extracted_skills']}")
    print(f"  Suggestions:\n{result['suggestions']}")
