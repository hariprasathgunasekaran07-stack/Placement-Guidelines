"""
app.py
------
Main Streamlit app — sidebar-navigated dashboard tying all six modules
together via the shared SQLite database (database.py) and student_id.

Features:
- Department & Targeted Role cascaded selection across 5 IT Departments & 11 Industry Roles
- Role-targeted multi-category Aptitude Tests (Quant, Logic, Verbal, Data Interpretation, Pseudocode, Systems)
- Role- & Department-aligned Technical Quizzes (Role tech stack + IT core subjects: OS, DBMS, Networks)
- Role-specific AI Mock Interviews with tailored rubrics and scenario probing
- Resume Analyzer with department-specific recommendations
- Comprehensive Skill Gap Analysis with priority rankings and actionable learning roadmaps

Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd

from database import init_db, add_course_record
from user_profile import register_student, get_profile
import aptitude_test
import technical_quiz
import mock_interview
import resume_analyzer
from skill_gap_analysis import (
    run_skill_gap_analysis_for_student,
    ROLE_SKILL_MAP,
    IT_DEPARTMENTS,
    get_department_for_role,
    get_roles_for_department,
)
from config import USE_LLM

init_db()

st.set_page_config(
    page_title="Smart Placement Guidance — IT Career Readiness",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom styling — clean, modern card aesthetic with department badges
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .block-container { padding-top: 1.8rem; }

    .app-card {
        background: #FFFFFF;
        border: 1px solid #E8EAED;
        border-radius: 12px;
        padding: 1.3rem 1.6rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        margin-bottom: 1rem;
    }

    .metric-big {
        font-size: 2.1rem;
        font-weight: 800;
        color: #1E293B;
        margin: 0;
    }
    .metric-label {
        font-size: 0.82rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 0;
    }

    .level-badge {
        display: inline-block;
        padding: 0.2rem 0.75rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.8rem;
        color: white;
    }
    .badge-beginner { background: #EF4444; }
    .badge-intermediate { background: #F59E0B; }
    .badge-advanced { background: #10B981; }

    .dept-badge {
        display: inline-block;
        background: #EEF2FF;
        color: #4F46E5;
        border: 1px solid #C7D2FE;
        border-radius: 6px;
        padding: 0.2rem 0.6rem;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .tag-badge {
        display: inline-block;
        background: #F1F5F9;
        color: #334155;
        border-radius: 4px;
        padding: 0.15rem 0.5rem;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 0.4rem;
    }

    section[data-testid="stSidebar"] {
        border-right: 1px solid #E2E8F0;
    }

    h1, h2, h3 { color: #0F172A; }
</style>
""", unsafe_allow_html=True)


def level_badge(level: str) -> str:
    cls = {
        "Beginner": "badge-beginner",
        "Intermediate": "badge-intermediate",
        "Advanced": "badge-advanced",
    }.get(level, "badge-intermediate")
    return f'<span class="level-badge {cls}">{level}</span>'


def metric_card(label: str, value: str, col):
    col.markdown(f"""
    <div class="app-card">
        <p class="metric-label">{label}</p>
        <p class="metric-big">{value}</p>
    </div>
    """, unsafe_allow_html=True)


if "student_id" not in st.session_state:
    st.session_state.student_id = None

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🎓 Placement Guidance")
    st.caption("AI-Powered Multi-Department Placement Readiness" if USE_LLM else "Placement Readiness (Offline Fallback Mode)")
    st.divider()

    page = st.radio("Navigate", [
        "🏠 Dashboard", "👤 Profile", "🧠 Aptitude Test", "💻 Technical Quiz",
        "🎤 Mock Interview", "📄 Resume Analyzer", "🎯 Skill Gap Report",
    ], label_visibility="collapsed")

    st.divider()
    if st.session_state.student_id:
        profile = get_profile(st.session_state.student_id)
        st.success(f"Logged in: **{profile['name']}**")
        dept = profile.get("department") or get_department_for_role(profile.get("target_role", ""))
        st.markdown(f'<span class="dept-badge">{dept}</span>', unsafe_allow_html=True)
        st.caption(f"🎯 Target Role: **{profile['target_role']}**")
    else:
        st.info("👋 Register in **Profile** to begin your targeted preparation.")

# ---------------------------------------------------------------------------
# Dashboard — Overview & Metrics
# ---------------------------------------------------------------------------
if page == "🏠 Dashboard":
    st.title("Campus Placement Readiness Dashboard 👋")
    st.write("Track your comprehensive preparation across Aptitude, Technical Quiz, Mock Interview, and Resume Analysis.")

    if not st.session_state.student_id:
        st.warning("Please navigate to the **👤 Profile** tab in the sidebar to register and select your IT Department & Target Role.")
    else:
        sid = st.session_state.student_id
        profile = get_profile(sid)
        role = profile["target_role"] or "Software Development Engineer (SDE)"
        dept = profile.get("department") or get_department_for_role(role)

        from database import (
            get_latest_quiz_result,
            get_latest_interview_result,
            get_latest_resume_analysis,
        )
        quiz_row = get_latest_quiz_result(sid)
        interview_row = get_latest_interview_result(sid)
        resume_row = get_latest_resume_analysis(sid)

        st.markdown(f'<div class="dept-badge">IT Department: {dept}</div>', unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        metric_card("Target Role", role, c1)
        metric_card(
            "Quiz Score",
            f"{quiz_row['topic_scores'] and round(sum(quiz_row['topic_scores'].values())/len(quiz_row['topic_scores'])) or 0}/100" if quiz_row else "—",
            c2,
        )
        metric_card("Interview Score", f"{interview_row['overall_score']:.0f}/100" if interview_row else "—", c3)
        metric_card("Resume Analyzed", "Yes ✅" if resume_row else "Not yet", c4)

        st.markdown("### Next Recommended Step")
        if not quiz_row:
            st.info("➡️ Complete the **💻 Technical Quiz** tailored to your chosen role & core IT subjects.")
        elif not interview_row:
            st.info("➡️ Take the **🎤 AI Mock Interview** to practice verbal technical & situational questions.")
        elif not resume_row:
            st.info("➡️ Upload or paste your resume in **📄 Resume Analyzer**.")
        else:
            st.success("🎉 You have completed all inputs! Generate your full **🎯 Skill Gap Report**.")

# ---------------------------------------------------------------------------
# Module 2: Profile Registration (with Department & Role Cascade)
# ---------------------------------------------------------------------------
elif page == "👤 Profile":
    st.title("Student Profile & Targeted Role Registration")
    st.write("Select your target IT department and specialized job role to unlock personalized assessments.")

    with st.container():
        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        with st.form("profile_form"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Full Name", value="Bharath Kumar S")
            email = col2.text_input("College / Personal Email", value="bharath@example.com")

            col3, col4 = st.columns(2)
            # Department selection
            selected_dept = col3.selectbox("IT Department", list(IT_DEPARTMENTS.keys()), index=0)
            roles_in_dept = get_roles_for_department(selected_dept)
            target_role = col4.selectbox("Target Job Role", roles_in_dept, index=0)

            # Pre-populate suggested skills for this role
            default_skills = ", ".join(list(ROLE_SKILL_MAP.get(target_role, {}).keys())[:4])
            skills = st.text_input("Current Skills (comma-separated)", value=default_skills)
            academic_details = st.text_area("Academic Details", value="B.Tech Computer Science / IT / AI & DS, 3rd Year")

            submitted = st.form_submit_button("Save / Update Profile", type="primary")
            if submitted:
                sid = register_student(
                    name=name,
                    email=email,
                    skills=[s.strip() for s in skills.split(",") if s.strip()],
                    academic_details=academic_details,
                    target_role=target_role,
                    department=selected_dept,
                )
                st.session_state.student_id = sid
                st.success(f"Profile saved successfully! Student ID: {sid} | Role: {target_role} ({selected_dept})")
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.student_id:
        st.subheader("Active Student Profile")
        p = get_profile(st.session_state.student_id)
        st.json(p)

# ---------------------------------------------------------------------------
# Module 1: Multi-Type Aptitude Test (Role & Department Targeted)
# ---------------------------------------------------------------------------
elif page == "🧠 Aptitude Test":
    st.title("Aptitude & Reasoning Assessment")
    st.write("Practice Quantitative Aptitude, Logical Reasoning, Verbal Ability, Data Interpretation, Pseudocode, and System Logic.")

    if not st.session_state.student_id:
        st.warning("Please register in the **👤 Profile** tab first.")
    else:
        profile = get_profile(st.session_state.student_id)
        role = profile["target_role"] or "Software Development Engineer (SDE)"
        dept = profile.get("department") or get_department_for_role(role)

        test_mode = st.radio(
            "Select Aptitude Test Type:",
            ["🎯 Role & Department Targeted (Recommended)", "📚 Comprehensive Placement Test (All Categories)"],
            horizontal=True,
        )

        mode_param = "Targeted" if "Targeted" in test_mode else "All"
        questions = aptitude_test.get_questions(target_role=role, department=dept, mode=mode_param)
        question_ids = [q["id"] for q in questions]

        st.caption(f"Showing **{len(questions)}** questions tailored for: **{role}** ({dept})")

        answers = {}
        for idx, q in enumerate(questions):
            with st.container():
                st.markdown('<div class="app-card">', unsafe_allow_html=True)
                st.markdown(f'<span class="tag-badge">{q["category"]}</span> **Q{idx + 1}.** {q["question"]}', unsafe_allow_html=True)
                choice = st.radio(
                    "Choose one:",
                    q["options"],
                    key=f"apt_{q['id']}",
                    index=None,
                    label_visibility="collapsed",
                )
                if choice is not None:
                    answers[q["id"]] = q["options"].index(choice)
                st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Submit Aptitude Test", type="primary"):
            result = aptitude_test.score_aptitude_test(
                answers, st.session_state.student_id, question_ids=question_ids
            )
            st.success(f"Aptitude Test Completed! Overall Score: **{result['overall_score']}/100**")
            st.subheader("Category Breakdown")
            cat_df = pd.Series(result["category_scores"], name="Score (%)")
            st.bar_chart(cat_df)

# ---------------------------------------------------------------------------
# Module 3: Technical Quiz (Role & Department Tailored)
# ---------------------------------------------------------------------------
elif page == "💻 Technical Quiz":
    st.title("Technical Knowledge Quiz")
    st.write("Dynamic quiz covering your targeted role's technology stack along with essential IT department core fundamentals (OS, DBMS, Computer Networks).")

    if not st.session_state.student_id:
        st.warning("Please register in the **👤 Profile** tab first.")
    else:
        profile = get_profile(st.session_state.student_id)
        role = profile["target_role"] or "Software Development Engineer (SDE)"
        dept = profile.get("department") or get_department_for_role(role)

        st.markdown(f'<div class="dept-badge">Tailored for: {role} — {dept}</div>', unsafe_allow_html=True)

        q_list = technical_quiz.get_questions_for_role(target_role=role, department=dept, count=12)
        question_ids = [q["id"] for q in q_list]

        answers = {}
        for idx, q in enumerate(q_list):
            with st.container():
                st.markdown('<div class="app-card">', unsafe_allow_html=True)
                st.markdown(f'<span class="tag-badge">{q["topic"]}</span> **Q{idx + 1}.** {q["question"]}', unsafe_allow_html=True)
                choice = st.radio(
                    "Choose one:",
                    q["options"],
                    key=f"tq_{q['id']}",
                    index=None,
                    label_visibility="collapsed",
                )
                if choice is not None:
                    answers[q["id"]] = q["options"].index(choice)
                st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Submit Technical Quiz", type="primary"):
            result = technical_quiz.score_technical_quiz(
                answers, st.session_state.student_id, question_ids=question_ids
            )
            st.success(f"Quiz Submitted! Overall Score: **{result['overall_score']}/100**")

            if result["weak_topics"]:
                st.warning(f"⚠️ Topics Needing Review: {', '.join(result['weak_topics'])}")
            else:
                st.balloons()
                st.success("🎉 Outstanding performance! No weak topics detected.")

            st.info(result["feedback"])
            st.subheader("Topic-Wise Mastery")
            st.bar_chart(pd.Series(result["topic_scores"]))

# ---------------------------------------------------------------------------
# Module 4: AI Mock Interview (Role & Scenario Probing)
# ---------------------------------------------------------------------------
elif page == "🎤 Mock Interview":
    st.title("AI Mock Technical Interview")
    st.write("Experience role-tailored technical, architectural, and behavioral interview questions evaluated with instant score and feedback.")

    if not st.session_state.student_id:
        st.warning("Please register in the **👤 Profile** tab first.")
    else:
        profile = get_profile(st.session_state.student_id)
        role = profile["target_role"] or list(ROLE_SKILL_MAP.keys())[0]
        dept = profile.get("department") or get_department_for_role(role)
        skills_for_role = list(ROLE_SKILL_MAP[role].keys())

        st.markdown(f'<div class="dept-badge">Interview Role: {role} ({dept})</div>', unsafe_allow_html=True)
        st.caption("Answer each question in 2-4 sentences explaining core technical concepts, trade-offs, and design rationale.")

        answers = {}
        for skill in skills_for_role:
            q = mock_interview.generate_question(skill, role=role, department=dept)
            with st.container():
                st.markdown('<div class="app-card">', unsafe_allow_html=True)
                st.markdown(f'<span class="tag-badge">{skill}</span> **{q}**', unsafe_allow_html=True)
                answers[skill] = st.text_area(
                    "Your answer:",
                    key=f"iv_{skill}",
                    height=100,
                    label_visibility="collapsed",
                    placeholder=f"Type your explanation for {skill}...",
                )
                st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Submit Mock Interview", type="primary"):
            result = mock_interview.run_mock_interview(
                st.session_state.student_id, role, skills_for_role, answers, department=dept
            )
            st.success(f"Interview Evaluation Complete! Overall Score: **{result['overall_score']}/100**")
            st.subheader("Detailed Question Feedback")
            for qa in result["qa_log"]:
                with st.expander(f"Skill: {qa['skill']} — Score: {qa['score']}/100", expanded=True):
                    st.markdown(f"**Question:** {qa['question']}")
                    st.markdown(f"**Your Answer:** {qa['answer'] or '*(No answer provided)*'}")
                    st.info(f"**Feedback:** {qa['feedback']}")

# ---------------------------------------------------------------------------
# Module 5: Resume Analyzer
# ---------------------------------------------------------------------------
elif page == "📄 Resume Analyzer":
    st.title("Targeted Resume Analyzer")
    st.write("Scan your resume against your targeted role and IT department to verify ATS compatibility, technical skills, and projects.")

    if not st.session_state.student_id:
        st.warning("Please register in the **👤 Profile** tab first.")
    else:
        profile = get_profile(st.session_state.student_id)
        role = profile["target_role"] or list(ROLE_SKILL_MAP.keys())[0]
        dept = profile.get("department") or get_department_for_role(role)

        st.markdown(f'<div class="dept-badge">Reviewing against: {role} ({dept})</div>', unsafe_allow_html=True)

        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
        pasted_text = st.text_area("...or paste plain text resume", height=150)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        st.subheader("Add Completed Courses & Certifications (Optional)")
        st.caption("Documenting verified courses provides supporting signals for your skill proficiency report.")
        n = st.number_input("Number of courses to add", min_value=0, max_value=5, value=0)
        course_inputs = []
        for i in range(n):
            c1, c2, c3, c4 = st.columns(4)
            cskill = c1.selectbox(f"Skill #{i+1}", list(ROLE_SKILL_MAP[role].keys()), key=f"cs_{i}")
            cname = c2.text_input(f"Course Name #{i+1}", key=f"cn_{i}")
            cdays = c3.number_input(f"Duration (Days) #{i+1}", 1, 180, 30, key=f"cd_{i}")
            cverif = c4.checkbox(f"Verified #{i+1}", key=f"cv_{i}")
            course_inputs.append((cskill, cname, cdays, cverif))
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Analyze Resume", type="primary"):
            resume_text = ""
            if uploaded:
                try:
                    with open("temp_resume.pdf", "wb") as f:
                        f.write(uploaded.read())
                    resume_text = resume_analyzer.extract_text_from_pdf("temp_resume.pdf")
                except Exception as ex:
                    st.error(f"⚠️ Could not extract text from the uploaded PDF: {ex}")
                    st.info("💡 **Tip**: Install `PyPDF2` in your terminal by running `pip install PyPDF2`, or paste your resume text into the box above.")
                    resume_text = pasted_text
            else:
                resume_text = pasted_text

            if not resume_text or not resume_text.strip():
                st.warning("Please provide resume content by uploading a valid PDF or pasting your plain text resume above.")
            else:
                result = resume_analyzer.analyze_resume(
                    st.session_state.student_id,
                    resume_text,
                    role,
                    list(ROLE_SKILL_MAP[role].keys()),
                )
                for cskill, cname, cdays, cverif in course_inputs:
                    if cname:
                        add_course_record(st.session_state.student_id, cskill, cname, cdays, cverif)

                st.subheader("Extracted Skill Evidence")
                st.json(result["extracted_skills"])

                st.subheader("Targeted Improvement Suggestions")
                st.markdown(result["suggestions"])

# ---------------------------------------------------------------------------
# Module 6: Skill Gap Analysis & Learning Roadmap
# ---------------------------------------------------------------------------
elif page == "🎯 Skill Gap Report":
    st.title("Role-Specific Skill Gap Report")
    st.write("Synthesizes performance signals from your Resume, Technical Quiz, Mock Interview, and Course History to prioritize high-impact areas.")

    if not st.session_state.student_id:
        st.warning("Please register in the **👤 Profile** tab first.")
    else:
        profile = get_profile(st.session_state.student_id)
        role = profile["target_role"] or list(ROLE_SKILL_MAP.keys())[0]
        dept = profile.get("department") or get_department_for_role(role)

        st.markdown(f'<div class="dept-badge">Target Role: {role} | Department: {dept}</div>', unsafe_allow_html=True)

        if st.button("Generate Skill Gap Report", type="primary"):
            report = run_skill_gap_analysis_for_student(st.session_state.student_id, role)

            c1, c2 = st.columns(2)
            metric_card("Overall Placement Readiness", f"{report.overall_readiness:.0f}/100", c1)
            with c2:
                st.markdown(f"""
                <div class="app-card">
                    <p class="metric-label">Assessed Level</p>
                    <p class="metric-big">{level_badge(report.overall_level)}</p>
                </div>
                """, unsafe_allow_html=True)

            df = pd.DataFrame([
                {
                    "Skill": g.skill,
                    "Level": g.level,
                    "Current Proficiency": g.proficiency,
                    "Role Benchmark": g.required_weight,
                    "Skill Gap": g.gap,
                    "Priority Rank": g.priority_score,
                }
                for g in report.gaps
            ])

            st.subheader("Skill Gap Matrix")
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.subheader("Proficiency vs Role Benchmark")
            st.bar_chart(df.set_index("Skill")[["Current Proficiency", "Role Benchmark"]])

            st.subheader("Tailored Action Plan & Learning Recommendations")
            st.markdown(report.recommendations)
