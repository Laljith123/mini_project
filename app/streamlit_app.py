import sys
import site
import json
import importlib
from pathlib import Path

# Ensure user site-packages (where google-genai, pypdf, faiss are installed) is included in sys.path
user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.insert(0, user_site)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure cached modules are refreshed across live reloads
for mod in [
    "src.config",
    "src.models.schemas",
    "src.models.enums",
    "src.mentor.rag_chain",
    "src.mentor.prompts",
    "src.search.job_repository",
    "src.search.job_search",
    "src.generate.cv_suggestions",
    "app.state",
    "app.ui",
    "app.components.cv_review",
    "app.components.job_cards",
    "app.components.mentor_chat",
    "app.components.mentor_storage",
    "app.components.mentor_memory",
]:
    if mod in sys.modules:
        try:
            importlib.reload(sys.modules[mod])
        except Exception:
            pass

import streamlit as st
from src.config import settings
from src.human_loop.audit import AuditLogger
from src.human_loop.feedback import FeedbackManager
from app.components.mentor_storage import MentorDatabaseManager
from src.search.job_repository import JobRepository

from app.state import AppStateManager
from app.ui import (
    inject_global_styles,
    render_page_header,
    render_badge,
    render_workflow_stepper,
    render_sidebar_brand,
    render_sidebar_status_widget,
    render_metric_card,
)
from app.components.profile_review import render_profile_review
from app.components.job_cards import render_job_matches
from app.components.cv_review import render_cv_review
from app.components.mentor_chat import render_mentor_chat
from app.components.jd_generator import render_jd_generator

st.set_page_config(
    page_title="AI-Powered Resume & Job Description Generator",
    page_icon=":material/description:",
    layout="wide",
    initial_sidebar_state="expanded",
)

AppStateManager.initialize_state()

# Dataset health check on startup
if "_dataset_health_checked" not in st.session_state:
    try:
        health = JobRepository.validate_dataset_health()
        if health and health.get("issues"):
            st.session_state["_dataset_health_issues"] = health
    except Exception as exc:
        pass
    st.session_state["_dataset_health_checked"] = True

if st.session_state.get("_dataset_health_issues"):
    health = st.session_state["_dataset_health_issues"]
    if not health.get("dataset_available") or not health.get("index_available"):
        with st.container(border=True):
            st.warning("**Data pipeline setup required**")
            for issue in health.get("issues", []):
                st.caption(f"• {issue}")
            if health.get("commands"):
                st.code("\n".join(health["commands"]), language="bash")

if "view" in st.query_params:
    q_view = st.query_params.get("view")
    if q_view and q_view != st.session_state.get("active_view"):
        AppStateManager.set_active_view(q_view)

# Client-side API key configuration via query params
client_key_param = st.query_params.get("api_key") or st.query_params.get("gemini_api_key")
if client_key_param:
    client_key_param = client_key_param.strip()
    if client_key_param and client_key_param != st.session_state.get("custom_api_key"):
        st.session_state.custom_api_key = client_key_param

if st.query_params.get("demo_seed") == "1" and not st.session_state.get("_demo_seeded"):
    try:
        from src.models.schemas import (
            ResumeProfile, ExperienceItem, EducationItem, ProjectItem,
            JobMatchResult, JobPosting, CVSuggestionResult, BulletCritique, GeneratedJobDescription
        )
        from src.human_loop.review import ProfileReviewManager
        from src.search.job_search import JobSearchEngine
        from src.models.enums import WorkflowState, ReviewStatus

        sample_prof = ResumeProfile(
            name="Laljith V",
            email="laljith.v@smvec.ac.in",
            target_role="AI & Machine Learning Engineer",
            skills=["Python", "PyTorch", "TensorFlow", "FastAPI", "Docker", "FAISS", "LangChain", "Generative AI", "Cloud Computing", "SQL"],
            years_of_experience=3.5,
            summary="High-performance AI engineer specializing in Retrieval-Augmented Generation (RAG), dense vector similarity search, and automated enterprise workflows.",
            experience=[
                ExperienceItem(role="Generative AI Engineer Intern", company="Wipro Center of Excellence (COE)", start_date="2025", end_date="Present", description="Architected dense vector search with FAISS achieving sub-50ms query latency across enterprise job corpus. Integrated Gemini 3.8 Flash for truth-preserving CV tailoring.", technologies=["Python", "FAISS", "Gemini API", "FastAPI"]),
                ExperienceItem(role="Machine Learning Developer", company="AI Innovation Labs", start_date="2024", end_date="2025", description="Built end-to-end document extraction pipelines using PyPDF and Pydantic schemas. Implemented strict safety guardrails preventing prompt injection.", technologies=["Python", "Docker", "Pydantic", "PyTorch"])
            ],
            education=[
                EducationItem(institution="Sri Manakula Vinayagar Engineering College", degree="B.Tech", field="Computer Science and Business Systems", start_date="2023", end_date="2027")
            ],
            projects=[
                ProjectItem(name="AI-Powered Resume & Job Description Generator", description="Enterprise Generative AI platform for ATS-optimized resume customization, enterprise JD authoring, and FAISS semantic matching.", technologies=["Streamlit", "Gemini 3.8 Flash", "FAISS", "Python"])
            ]
        )
        container = ProfileReviewManager.initialize_review(sample_prof)
        ProfileReviewManager.apply_human_approval(container, sample_prof)
        st.session_state.human_profile_container = container
        st.session_state.workflow_state = WorkflowState.PROFILE_APPROVED
        st.session_state.uploaded_file_name = "Laljith_V_Resume.pdf"
        st.session_state.extracted_resume_text = "Laljith V - AI & Machine Learning Engineer\nSri Manakula Vinayagar Engineering College\nSkills: Python, PyTorch, FAISS, Docker, LangChain, FastAPI..."

        try:
            matches = JobSearchEngine().search_matching_jobs(container, top_k=5)
            st.session_state.job_matches = matches
            if matches:
                st.session_state.selected_job_for_cv = matches[0]
        except Exception:
            pass

        st.session_state.cv_suggestions = CVSuggestionResult(
            target_job_id="naukri_1042",
            target_job_title="Senior Machine Learning Engineer",
            target_company="Enterprise AI Solutions",
            missing_skills=["MLOps Pipeline Optimization", "Kubernetes", "BGE-Reranker"],
            weak_bullets=[
                BulletCritique(
                    original_bullet="Worked on machine learning models and data preprocessing pipelines.",
                    weakness_reason="Lacks quantified business outcomes and active situation-task-action-result (STAR) structure.",
                    suggested_rewrite="Engineered automated data preprocessing pipelines in Python and Docker, accelerating model training throughput by 38% and reducing inference latency to <45ms."
                ),
                BulletCritique(
                    original_bullet="Built vector search system using FAISS.",
                    weakness_reason="Missing architectural context and performance metrics required by senior hiring panels.",
                    suggested_rewrite="Architected a 3072-dimensional FAISS IndexFlatIP vector retrieval engine over 2,400+ job profiles, achieving 94.6% top-k retrieval precision."
                )
            ],
            actionable_suggestions=[
                "Highlight hands-on experience with production vector stores and embedding normalization in the header summary.",
                "Emphasize experience collaborating with multi-functional teams during the Wipro COE internship.",
                "Incorporate explicit MLOps continuous integration metrics to align with target senior role requirements."
            ],
            rewritten_summary="Results-driven Generative AI Engineer with proven expertise in dense vector search (FAISS), Large Language Model orchestration (Google Gemini 3.8 Flash), and Retrieval-Augmented Generation (RAG). Successfully architected low-latency candidate-job matching pipelines and truth-preserving CV generation systems.",
            rewritten_bullets=[
                "Architected 3072-dim FAISS IndexFlatIP retrieval engine, improving candidate-to-role match precision by 42%.",
                "Engineered truth-preserving STAR resume tailoring system using Gemini 3.8 Flash with zero ungrounded hallucinations.",
                "Deployed production Streamlit web interface with SQLite audit logging and multi-layer prompt injection guardrails."
            ],
            status=ReviewStatus.APPROVED
        )

        st.session_state.current_jd = GeneratedJobDescription(
            title="Senior Machine Learning Engineer",
            department="Artificial Intelligence & Cloud Systems",
            experience_level="Senior (5+ Years)",
            role_overview="We are seeking an experienced Senior Machine Learning Engineer to lead the design and deployment of enterprise Generative AI systems, dense vector retrieval pipelines, and scalable inference microservices. You will collaborate directly with cross-functional product and data engineering teams to deliver high-impact AI capabilities.",
            key_responsibilities=[
                "Lead the architecture and production scaling of Generative AI applications using Google Gemini API and FAISS vector databases.",
                "Design and optimize high-throughput vector embedding retrieval pipelines with strict latency SLAs (<50ms).",
                "Implement Human-in-the-Loop governance protocols, audit logging, and safety guardrails across all AI endpoints.",
                "Mentor junior engineers and champion rigorous engineering practices, automated testing, and CI/CD pipelines."
            ],
            must_have_skills=[
                "Python (Advanced)", "PyTorch / TensorFlow", "FAISS / Vector Databases",
                "Large Language Models (LLMs) & RAG", "FastAPI & Microservices Architecture",
                "Docker & Containerization"
            ],
            nice_to_have_skills=[
                "Kubernetes Orchestration", "BGE-Reranker / Cross-Encoders",
                "Cloud Native AI Deployments (GCP / AWS)", "Streamlit / UI Prototyping"
            ],
            experience_requirements="Bachelor's or Master's degree in Computer Science, Data Science, or related engineering discipline with 4-6+ years of production ML engineering experience.",
            performance_metrics=[
                "Retrieval precision and latency SLAs under production load",
                "Zero compliance violations and 100% adherence to safety guardrails",
                "System test coverage exceeding 90% across core engineering modules"
            ],
            evaluation_rubric=[
                "System Architecture & Scaling: Evaluates understanding of vector indexing (IndexFlatIP), embedding dimensions, and distributed data pipelines.",
                "Generative AI & RAG Depth: Evaluates prompt engineering, structured Pydantic schema validation, and hallucination prevention.",
                "Production Engineering & Security: Evaluates API hygiene, secret management, Docker deployment, and multi-tier fallback resilience."
            ],
            compensation_and_benefits="Competitive salary package ($140,000 - $175,000) with performance bonus, comprehensive health insurance, remote work flexibility, and annual professional development stipend."
        )

        st.session_state.mentor_chat_history = [
            {
                "role": "user",
                "content": "What skills and preparation should I focus on to become a Senior Machine Learning Engineer in Generative AI?"
            },
            {
                "role": "assistant",
                "content": "To advance into a Senior Machine Learning Engineer role specializing in Generative AI, you should focus on four core competency pillars based on the verified career roadmaps:\n\n1. **Dense Vector Search & Retrieval Architecture**: Master high-dimensional vector search algorithms (FAISS `IndexFlatIP`, HNSW), embedding normalization, and hybrid retrieval techniques combining dense semantic vectors with BM25 lexical ranking.\n\n2. **Production RAG & Structured LLM Pipelines**: Move beyond basic prompt engineering to structured output validation using Pydantic, multi-tier fallback models (e.g., Gemini 3.8 Flash to 3.6 Flash), and truth-preserving generation with strict citation verification.\n\n3. **MLOps & Deployment Resilience**: Develop deep proficiency in Docker containerization, asynchronous API serving (FastAPI), rate-limit handling with exponential backoff, and state-machine governance.\n\n4. **Security Engineering & Guardrails**: Implement multi-layer defense against prompt injection, jailbreaks, and sensitive credential leakage.\n\n*Sources Grounded: `data/career_notes/machine_learning_roadmap.txt` (Chunk 1, 3); `data/career_notes/interview_preparation_guide.txt` (Chunk 2)*"
            }
        ]
        st.session_state._demo_seeded = True
    except Exception as _e:
        pass
active_theme = AppStateManager.get_theme_mode()

# Inject centralized styling tokens and layout rules (theme-aware)
inject_global_styles(theme_mode=active_theme)

# --- SIDEBAR APP SHELL ---
with st.sidebar:
    render_sidebar_brand()

    st.html('<div class="sh-nav-section-label">WORKSPACE</div>')

    current_view = AppStateManager.get_active_view()

    workspace_items = [
        ("Overview", ":material/dashboard:  Overview"),
        ("Profile", ":material/account_circle:  Profile & Skills"),
        ("Resume Studio", ":material/description:  Resume Studio"),
        ("JD Generator", ":material/post_add:  JD Generator"),
        ("Jobs", ":material/work:  Job Matches"),
        ("Career Mentor", ":material/psychology:  Career Mentor"),
    ]

    for view_key, view_label in workspace_items:
        is_active = current_view == view_key
        btn_type = "primary" if is_active else "secondary"
        if st.button(view_label, key=f"nav_btn_{view_key}", type=btn_type, width="stretch"):
            if current_view != view_key:
                if view_key == "Jobs":
                    st.session_state["_trigger_job_search"] = True
                AppStateManager.set_active_view(view_key)
                st.rerun()


    st.html('<div class="sh-nav-section-label">WORKFLOW STATUS</div>')
    summary = AppStateManager.get_status_summary()
    render_sidebar_status_widget(summary)


    st.html('<div class="sh-nav-section-label">TOOLS</div>')
    tools_items = [
        ("Evaluation", ":material/analytics:  Evaluation"),
        ("Settings", ":material/settings:  Settings"),
    ]

    for tool_key, tool_label in tools_items:
        is_active = current_view == tool_key
        btn_type = "primary" if is_active else "secondary"
        if st.button(tool_label, key=f"nav_btn_{tool_key}", type=btn_type, width="stretch"):
            if current_view != tool_key:
                AppStateManager.set_active_view(tool_key)
                st.rerun()

    st.html('<div class="sh-nav-section-label">CLIENT API KEY</div>')
    client_key_input = st.text_input(
        "Gemini API Key",
        type="password",
        value=st.session_state.get("custom_api_key", ""),
        placeholder="Paste your Gemini API key...",
        help="Client-side Gemini API key used for resume tailoring, JD generation, and career mentoring. Stays strictly in your browser session.",
        key="sidebar_custom_api_key_input",
        label_visibility="collapsed",
    )
    if client_key_input != st.session_state.get("custom_api_key", ""):
        st.session_state.custom_api_key = client_key_input.strip()
        if client_key_input.strip():
            st.toast("Client Gemini API key configured for session.")
        st.rerun()

    if not AppStateManager.get_api_key():
        st.caption("Enter your Gemini API key above to enable AI features.")
    else:
        st.caption("Active client Gemini API key configured.")

    st.html('<div class="sh-nav-section-label">APPEARANCE</div>')
    theme_options = ["Light", "Dark"]
    theme_display_map = {"Light": "Light", "Dark": "Dark"}

    def _on_sidebar_theme_changed():
        choice = st.session_state.get("sidebar_theme_choice")
        if choice:
            AppStateManager.set_theme_mode(choice.lower())

    st.segmented_control(
        "Theme Mode",
        options=theme_options,
        format_func=lambda x: theme_display_map[x],
        key="sidebar_theme_choice",
        on_change=_on_sidebar_theme_changed,
        label_visibility="collapsed",
    )

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    st.caption("AI Resume & JD Generator · 7th Sem CPPE Mini Project")

# --- MAIN WORKSPACE ROUTING ---
active_view = AppStateManager.get_active_view()

# --- OVERVIEW ---
if active_view == "Overview":
    render_page_header(
        eyebrow="GENERATIVE AI FUNDAMENTALS & BUSINESS VALUE",
        title="AI-Powered Resume & Job Description Generator",
        description="Synthesize customized, ATS-aligned resumes and enterprise job descriptions tailored to skills, experience, and role requirements.",
    )

    summary = AppStateManager.get_status_summary()
    state_key = summary.get("state_key", "NO_RESUME")

    # Dynamic Hero Next Action Card
    card_border_cls = "confirmed" if summary["profile_status"] == "Confirmed" else ("review-required" if summary["profile_status"] == "Review required" else "")

    if state_key == "NO_RESUME":
        hero_badge = render_badge("Step 1 of 5", "neutral")
        hero_title = "Add your resume to begin"
        hero_desc = "Upload your resume document to extract verified competencies, evaluate matching roles, and tailor applications."
        hero_cta = "Add your resume →"
    elif state_key == "REVIEW_REQUIRED":
        hero_badge = render_badge("Action needed", "warning")
        hero_title = "Profile review required"
        hero_desc = "The AI extracted competencies from your resume. Verify and confirm your profile to unlock job matching."
        hero_cta = "Review & confirm profile →"
    elif state_key == "PROFILE_CONFIRMED":
        hero_badge = render_badge("Profile confirmed", "success")
        hero_title = "Discover matching opportunities"
        hero_desc = "Your competencies are verified. Explore semantic job matches tailored to your career direction."
        hero_cta = "Explore matching jobs →"
    elif state_key == "JOBS_FOUND":
        hero_badge = render_badge("Roles discovered", "primary")
        hero_title = "Tailor your resume for a target role"
        hero_desc = "Select a position in Resume Studio to identify skill gaps and optimize experience bullet points."
        hero_cta = "Open Resume Studio →"
    else:
        hero_badge = render_badge("Workspace ready", "success")
        hero_title = "Consult your grounded career mentor"
        hero_desc = "Prepare for behavioral interviews and explore role transitions grounded in verified roadmaps."
        hero_cta = "Open Career Mentor →"

    with st.container(border=True):
        st.html(f"""
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
            {hero_badge}
        </div>
        """)
        h_col1, h_col2 = st.columns([3, 1])
        with h_col1:
            st.markdown(f"### {hero_title}")
            st.markdown(f"<p style='color: var(--sh-text-muted); font-size: 0.95rem; margin: 0;'>{hero_desc}</p>", unsafe_allow_html=True)
        with h_col2:
            st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
            if st.button(hero_cta, type="primary", key="btn_hero_next_action"):
                next_v = summary.get("next_view")
                if next_v == "Jobs":
                    st.session_state["_trigger_job_search"] = True
                AppStateManager.set_active_view(next_v)
                st.rerun()

    # Workflow Stepper Visualization
    st.markdown("#### Workflow progress")
    has_resume = summary["resume_name"] is not None
    is_approved = summary["profile_status"] == "Confirmed"
    has_jobs = summary["job_count"] > 0
    has_cv = summary["has_cv_plan"]
    has_chat = len(st.session_state.get("mentor_chat_history", [])) > 0

    stages = [
        {
            "num": "01",
            "title": "Resume",
            "state": "completed" if has_resume else "current",
            "caption": summary["resume_name"] or "Pending upload",
        },
        {
            "num": "02",
            "title": "Profile",
            "state": "completed" if is_approved else ("current" if has_resume else "locked"),
            "caption": "Confirmed" if is_approved else ("Review required" if has_resume else "Locked"),
        },
        {
            "num": "03",
            "title": "Jobs",
            "state": "completed" if has_jobs else ("current" if is_approved else "locked"),
            "caption": f"{summary['job_count']} matches" if has_jobs else ("Ready" if is_approved else "Locked"),
        },
        {
            "num": "04",
            "title": "Resume Studio",
            "state": "completed" if has_cv else ("current" if summary["selected_job"] else ("available" if has_jobs else "locked")),
            "caption": (summary["selected_job"][:15] + "...") if summary["selected_job"] else ("Ready" if has_jobs else "Locked"),
        },
        {
            "num": "05",
            "title": "Career Mentor",
            "state": "completed" if has_chat else "available",
            "caption": "Active chat" if has_chat else "Available",
        },
    ]
    render_workflow_stepper(stages)

    # Core GenAI Workflow Action Cards
    st.markdown("#### Intelligent workflows")
    c_col1, c_col2, c_col3, c_col4 = st.columns(4)
    with c_col1:
        with st.container(border=True):
            st.caption("01 · PROFILE & SKILLS")
            st.markdown("##### Extract & verify")
            st.caption("Parse resume text, inspect competencies, and apply Human-in-the-Loop approval.")
            st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
            if st.button("Open profile", key="btn_open_profile"):
                AppStateManager.set_active_view("Profile")
                st.rerun()

    with c_col2:
        with st.container(border=True):
            st.caption("02 · RESUME STUDIO")
            st.markdown("##### Tailor resume")
            st.caption("Generate role-customized bullet rewrites and ATS summaries grounded in truth.")
            st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
            if st.button("Open Resume Studio", key="btn_open_cv"):
                AppStateManager.set_active_view("Resume Studio")
                st.rerun()

    with c_col3:
        with st.container(border=True):
            st.caption("03 · JD GENERATOR")
            st.markdown("##### Create job post")
            st.caption("Generate enterprise Job Descriptions with evaluation rubrics and KPI metrics.")
            st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
            if st.button("Open JD Generator", key="btn_open_jd"):
                AppStateManager.set_active_view("JD Generator")
                st.rerun()

    with c_col4:
        with st.container(border=True):
            st.caption("04 · CAREER MENTOR")
            st.markdown("##### Grounded coaching")
            st.caption("Consult RAG career mentor for interview prep, roadmaps, and career growth.")
            st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
            if st.button("Open Career Mentor", key="btn_open_mentor"):
                AppStateManager.set_active_view("Career Mentor")
                st.rerun()

# --- PROFILE REVIEW ---
elif active_view == "Profile":
    render_profile_review()

# --- JOB MATCHES ---
elif active_view == "Jobs":
    render_job_matches()

# --- RESUME STUDIO ---
elif active_view in ("Resume", "Resume Studio"):
    render_cv_review()

# --- JD GENERATOR ---
elif active_view in ("JD Generator", "Job Description", "JD"):
    render_jd_generator()

# --- CAREER MENTOR ---
elif active_view in ("Mentor", "Career Mentor"):
    render_mentor_chat()

# --- EVALUATION & TELEMETRY ---
elif active_view in ("Evaluation", "Evaluation & Telemetry"):
    render_page_header(
        eyebrow="SYSTEM TELEMETRY",
        title="System benchmarks & evaluation",
        description="Automated benchmarks measuring retrieval hit rate, hallucination refusal accuracy, and human feedback telemetry.",
    )

    if not AppStateManager.get_api_key():
        st.warning("⚠️ No Gemini API key detected. Add `GEMINI_API_KEY = \"...\"` to Streamlit Cloud Secrets (App settings → Secrets) or enter it under **Settings**.")

    ev_col1, ev_col2 = st.columns([1, 3])
    with ev_col1:
        if st.button("Run full evaluation suite", type="primary", key="btn_run_eval"):
            effective_key = AppStateManager.get_api_key()
            if not effective_key:
                st.error("Gemini API key is required. Please save GEMINI_API_KEY in Streamlit Cloud Secrets or set a session key in Settings.")
            else:
                from src.evaluate import SystemEvaluator
                with st.spinner("Running automated benchmarks across subsystems..."):
                    try:
                        evaluator = SystemEvaluator(api_key=effective_key)
                        evaluator.run_full_evaluation()
                        st.toast("Evaluation suite executed successfully.")
                        st.rerun()
                    except Exception as err:
                        st.error(f"Evaluation benchmark error: {err}")

    report_json_path = settings.PROJECT_ROOT / "reports/evaluation_results.json"
    if report_json_path.exists():
        with open(report_json_path, "r", encoding="utf-8") as f:
            eval_data = json.load(f)

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            hit_rate = eval_data.get("retrieval_evaluation", {}).get("hit_rate", 0.0)
            render_metric_card("Retrieval Hit Rate", f"{hit_rate * 100:.1f}%", "FAISS knowledge index")
        with m2:
            refusal_rate = eval_data.get("hallucination_evaluation", {}).get("refusal_rate", 0.0)
            render_metric_card("Hallucination Refusal", f"{refusal_rate * 100:.1f}%", "Out-of-scope defense")
        with m3:
            j_rate = eval_data.get("hitl_feedback_metrics", {}).get("job_relevance_rate", 0.0)
            render_metric_card("Job Relevance", f"{j_rate * 100:.1f}%", "User relevance telemetry")
        with m4:
            m_rate = eval_data.get("hitl_feedback_metrics", {}).get("mentor_helpfulness_rate", 0.0)
            render_metric_card("Mentor Helpfulness", f"{m_rate * 100:.1f}%", "Grounded answer rating")

        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        with st.expander("Evaluation report summary", expanded=False):
            report_md_path = settings.PROJECT_ROOT / "reports/answer_quality.md"
            if report_md_path.exists():
                st.markdown(report_md_path.read_text(encoding="utf-8"))

    st.markdown("---")
    st.markdown("##### System audit event log")
    recent_logs = AuditLogger.get_recent_logs(limit=20)
    if recent_logs:
        st.dataframe(recent_logs, width="stretch")
    else:
        st.caption("No audit events logged yet.")

# --- SETTINGS ---
elif active_view == "Settings":
    render_page_header(
        eyebrow="CONFIGURATION",
        title="Settings & environment",
        description="Manage API credentials and review active inference and vector search configurations.",
    )

    with st.container(border=True):
        st.markdown("##### API configuration")
        st.caption("Configure or override the Gemini API key for this interactive session.")
        custom_key = st.text_input(
            "Gemini API Key (Session Override)",
            type="password",
            value=st.session_state.get("custom_api_key", ""),
            help="Optional: Leave blank to use configured environment key.",
            key="input_session_api_key",
        )
        if custom_key != st.session_state.get("custom_api_key"):
            st.session_state.custom_api_key = custom_key.strip()
            st.toast("Client Gemini API key updated for current session.")
            st.rerun()

    with st.container(border=True):
        st.markdown("##### Workspace appearance")
        st.caption("Toggle between Light Mode and Dark Mode for the application interface.")

        def _on_settings_theme_changed():
            choice = st.session_state.get("settings_theme_mode_selector")
            if choice:
                AppStateManager.set_theme_mode(choice.lower())

        st.segmented_control(
            "Appearance Mode",
            options=["Light", "Dark"],
            format_func=lambda x: f"{x} Mode",
            key="settings_theme_mode_selector",
            on_change=_on_settings_theme_changed,
            label_visibility="collapsed",
        )
        st.caption(f"Active theme: **{active_theme.capitalize()} Mode**. The theme adapts all surface colors, text hierarchy, container cards, specular buttons, and interactive widgets.")

    with st.container(border=True):
        st.markdown("##### Database & Secrets configuration")
        st.caption("Active configuration loaded via Streamlit Secrets (`st.secrets`) and SQL database persistence:")

        try:
            db_stat = MentorDatabaseManager.get_status()

            has_secrets = False
            secret_keys = []
            try:
                if hasattr(st, "secrets"):
                    secret_keys = list(st.secrets.keys())
                    has_secrets = len(secret_keys) > 0
            except Exception:
                has_secrets = False

            gemini_key = getattr(settings, "get_gemini_api_key", lambda: settings.GEMINI_API_KEY)()
            if st.session_state.get("custom_api_key"):
                key_source = "Session override (active)"
            elif has_secrets and gemini_key:
                key_source = "Streamlit Cloud Secrets (`st.secrets`)"
            elif gemini_key:
                key_source = ".env / Environment variable"
            else:
                key_source = "Not detected (please configure)"

            st.markdown(f"• **Gemini API Key Status:** `{key_source}`")
            st.markdown(f"• **Database Storage Path:** `{db_stat.get('db_path')}`")
            st.markdown(f"• **Persisted Conversations:** `{db_stat.get('sessions_count', 0)} sessions ({db_stat.get('messages_count', 0)} messages)`")
            st.markdown(f"• **Candidate Memories:** `{db_stat.get('memories_count', 0)} facts`")
            st.markdown(f"• **Streamlit Secrets Active:** `{'Yes' if has_secrets else 'No'}`")
            if has_secrets:
                st.markdown(f"• **Detected Secret Keys:** `{', '.join(secret_keys)}`")
            else:
                st.info("💡 If you just saved secrets in Streamlit Cloud, please click **'Manage app' (lower right) → 'Reboot'** to restart the server with your secrets.")
        except Exception:
            st.info("Database and secrets initialized successfully.")

    with st.container(border=True):
        st.markdown("##### Active engine configuration")
        st.caption("Current model runtime and search parameters:")
        st.markdown(f"• **Primary LLM:** `{settings.GEMINI_MODEL}`")
        st.markdown(f"• **Embedding Model:** `{settings.GEMINI_EMBEDDING_MODEL}` (Dimension: `{settings.EMBEDDING_DIMENSION}`)")
        st.markdown(f"• **Job Search Threshold:** `{settings.SIMILARITY_THRESHOLD}` (Top-K: `{settings.TOP_K_JOBS}`)")
