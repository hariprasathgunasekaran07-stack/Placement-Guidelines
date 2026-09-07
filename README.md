# Smart AI-Based Placement Guidance & Skill Gap Analysis

A 6-module student placement-prep system: Aptitude Test, User Profile,
Technical Quiz, AI Mock Interview, Resume Analyzer, and Skill Gap Analysis
— all connected through one shared SQLite database.

## Files

| File | Module |
|---|---|
| `config.py` | Shared LLM config (Gemini) — loads `.env`, works with or without an API key |
| `database.py` | Shared SQLite schema + helper functions used by every module |
| `user_profile.py` | Module 2 — registration & profile |
| `aptitude_test.py` | Module 1 — aptitude test (quant, logical, numerical, problem solving) |
| `technical_quiz.py` | Module 3 — technical quiz (Python, SQL, Data Structures, ML, fundamentals) |
| `mock_interview.py` | Module 4 — AI mock interview (question generation + answer scoring) |
| `resume_analyzer.py` | Module 5 — resume parsing + improvement suggestions |
| `skill_gap_analysis.py` | Module 6 — blends all signals, computes gaps, classifies levels |
| `app.py` | Main Streamlit app — all 6 modules as tabs, wired through the DB |
| `test_pipeline.py` | Runs all 6 modules end-to-end from the command line (no UI needed) |

## Setup

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up your environment file
cp .env.example .env
# Open .env and paste your Gemini API key (optional — see below)

# 4. Initialize the database
python database.py

# 5. Sanity-check everything works
python test_pipeline.py

# 6. Launch the full app
streamlit run app.py
```

## About the API key

Every module works **with or without** `GEMINI_API_KEY` set:

- **Without a key:** each module automatically falls back to rule-based
  logic (keyword matching for resume skills, a templated recommendation
  engine, a keyword-overlap interview scorer). You get real, working
  output immediately — good for testing and for demos where you don't
  want to depend on network/API calls.
- **With a key:** resume analysis, interview question generation/scoring,
  and skill-gap recommendations switch to Gemini for richer, more
  natural output.

Get a free key at https://aistudio.google.com/app/apikey and paste it
into `.env` — nothing else needs to change.

## How the modules connect

Every module writes its results to the shared SQLite database
(`placement.db`), keyed by `student_id` (created in Module 2). Module 6
(`run_skill_gap_analysis_for_student`) reads the **latest** saved resume
analysis, quiz result, interview result, and course history for that
student and blends them automatically — you don't need to pass data
between files manually.

```
Module 2 (Profile) --> student_id
                          |
        +----------+----------+----------+
        |          |          |          |
   Module 1    Module 3   Module 4   Module 5
  (Aptitude)   (Quiz)   (Interview) (Resume)
        |          |          |          |
        +----------+----------+----------+
                          |
                    Module 6 (Skill Gap Analysis)
                    reads all of the above from the DB
```
