"""
AI-Powered Job Description Generator UI Component.
Generates comprehensive, tailored, and unbiased Job Descriptions based on
role title, required skills, experience level, and business requirements.
"""

from typing import Optional, List, Dict, Any
import json
import streamlit as st

from src.config import settings
from src.models.schemas import GeneratedJobDescription
from src.generate.jd_generator import JobDescriptionGenerator
from app.state import AppStateManager
from app.ui import (
    render_page_header,
    render_badge,
    render_metric_card,
    render_skill_chips_html,
)

ROLE_PRESETS: Dict[str, Dict[str, Any]] = {
    "AI / Machine Learning Engineer": {
        "title": "Senior AI & Machine Learning Engineer",
        "department": "Artificial Intelligence & Data",
        "level": "Senior (5-8 yrs)",
        "required_skills": "Python, PyTorch/TensorFlow, Google GenAI SDK / Gemini API, RAG Architecture, Vector DBs (FAISS/Chroma), LLM Fine-tuning",
        "preferred_skills": "Kubernetes, MLflow, LangChain/LlamaIndex, Docker, Prompt Injection Defense",
        "responsibilities": "Design and deploy enterprise GenAI RAG pipelines, optimize LLM inference latency, enforce HITL safety guardrails, and lead AI system architecture.",
        "arrangement": "Hybrid",
        "context": "Enterprise Generative AI platform driving automated talent matching and intelligent career workflows.",
    },
    "Full-Stack Python & React Developer": {
        "title": "Full-Stack Software Engineer",
        "department": "Product Engineering",
        "level": "Mid-Level (3-5 yrs)",
        "required_skills": "Python, FastAPI / Flask, React / TypeScript, PostgreSQL, RESTful APIs, Git",
        "preferred_skills": "Streamlit, Docker, Redis, Tailwind CSS, CI/CD GitHub Actions",
        "responsibilities": "Develop responsive frontend interfaces, design performant backend microservices, write clean unit tests, and collaborate with product teams.",
        "arrangement": "Remote",
        "context": "Modern SaaS engineering team focused on high-reliability, customer-centric web applications.",
    },
    "Data Analyst & BI Specialist": {
        "title": "Data Analyst & Business Intelligence Specialist",
        "department": "Business Analytics & Growth",
        "level": "Mid-Level (3-5 yrs)",
        "required_skills": "SQL, Python / R, PowerBI / Tableau, Data Modeling, Statistical Analysis, Excel",
        "preferred_skills": "Snowflake, dbt, Predictive Modeling, Stakeholder Presentations",
        "responsibilities": "Build real-time executive dashboards, uncover actionable insights from funnel metrics, and partner with leadership on growth strategies.",
        "arrangement": "Hybrid",
        "context": "Data-driven organization delivering business value intelligence and operational dashboards.",
    },
    "Cloud & DevOps Architect": {
        "title": "Lead Cloud & DevOps Architect",
        "department": "Infrastructure & Cloud Ops",
        "level": "Lead / Principal (8+ yrs)",
        "required_skills": "AWS / GCP, Terraform / IaC, Kubernetes (EKS/GKE), Docker, CI/CD Pipelines, Linux Security",
        "preferred_skills": "FinOps Cloud Cost Optimization, Helm, Prometheus/Grafana, Zero-Trust Architecture",
        "responsibilities": "Architect multi-region scalable cloud infrastructure, maintain 99.99% uptime SLAs, automate deployment pipelines, and enforce cloud security standards.",
        "arrangement": "Remote",
        "context": "High-scale cloud infrastructure supporting mission-critical enterprise workloads.",
    },
}


def render_jd_generator():
    """Renders the AI-Powered Job Description Generator interface."""
    render_page_header(
        eyebrow="JOB DESCRIPTION GENERATOR",
        title="AI-Powered Job Description Generator",
        description="Synthesize structured, role-specific, and bias-free Job Descriptions based on target skills, experience level, and business objectives.",
    )

    # Initialize JD session state if missing
    if "jd_history" not in st.session_state:
        st.session_state["jd_history"] = []
    if "current_jd" not in st.session_state:
        st.session_state["current_jd"] = None

    # Top Metric Banner
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        render_metric_card(
            label="Generative AI Model",
            value="Gemini 3.8 Flash",
            subtext="Google GenAI SDK v2.22",
            icon=":material/neurology:",
        )
    with col_m2:
        render_metric_card(
            label="Customization Level",
            value="Skill & Exp Tailored",
            subtext="Role & KPI Grounded",
            icon=":material/tune:",
        )
    with col_m3:
        render_metric_card(
            label="Evaluation Rubric",
            value="Auto-Generated",
            subtext="Objective Interviewing Criteria",
            icon=":material/fact_check:",
        )
    with col_m4:
        total_gen = len(st.session_state.get("jd_history", []))
        render_metric_card(
            label="Generated JDs",
            value=f"{total_gen} Available",
            subtext="Ready for Export & Matching",
            icon=":material/assignment:",
        )

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    # Preset selection for fast prototyping
    with st.container(border=True):
        st.subheader("1. Configure Role Requirements & Skills", divider=False)
        st.caption("Select a quick template preset or enter custom role requirements.")

        preset_choice = st.selectbox(
            "Quick Role Presets",
            options=["Custom Role"] + list(ROLE_PRESETS.keys()),
            key="jd_preset_selector",
        )

        preset_data = ROLE_PRESETS.get(preset_choice, {})

        c1, c2 = st.columns(2)
        with c1:
            title_val = preset_data.get("title", "AI & Machine Learning Engineer")
            job_title = st.text_input("Job Title *", value=title_val, key="jd_input_title")

            dept_val = preset_data.get("department", "Engineering & AI")
            department = st.text_input("Department / Business Domain", value=dept_val, key="jd_input_dept")

            level_options = [
                "Entry-Level (0-2 yrs)",
                "Mid-Level (3-5 yrs)",
                "Senior (5-8 yrs)",
                "Lead / Principal (8+ yrs)",
                "Executive / Director",
            ]
            default_lvl_idx = 1
            if preset_data.get("level") in level_options:
                default_lvl_idx = level_options.index(preset_data.get("level"))
            experience_level = st.selectbox("Required Experience Level *", options=level_options, index=default_lvl_idx, key="jd_input_level")

        with c2:
            arrangement_options = ["Hybrid", "Remote", "On-site"]
            default_arr_idx = 0
            if preset_data.get("arrangement") in arrangement_options:
                default_arr_idx = arrangement_options.index(preset_data.get("arrangement"))
            work_arrangement = st.selectbox("Work Arrangement", options=arrangement_options, index=default_arr_idx, key="jd_input_arrangement")

            ctx_val = preset_data.get("context", "Enterprise Generative AI team building scalable intelligent applications.")
            company_context = st.text_input("Company / Team Context", value=ctx_val, key="jd_input_context")

            model_choice = st.selectbox(
                "Gemini Generator Model",
                options=[settings.GEMINI_MODEL, settings.GEMINI_FALLBACK_MODEL],
                key="jd_model_choice",
                help="Google Gemini GenAI model used to craft structured job description",
            )

        st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)

        req_skills_val = preset_data.get("required_skills", "Python, PyTorch, Gemini API, RAG, Vector Search")
        required_skills = st.text_area(
            "Core Required Skills (comma separated) *",
            value=req_skills_val,
            rows=2,
            key="jd_input_req_skills",
            help="Specify essential technical and domain competencies candidates must have.",
        )

        pref_skills_val = preset_data.get("preferred_skills", "Docker, Kubernetes, LangChain, CI/CD")
        preferred_skills = st.text_area(
            "Preferred / Nice-to-Have Skills",
            value=pref_skills_val,
            rows=2,
            key="jd_input_pref_skills",
            help="Valuable bonus skills that distinguish top candidates.",
        )

        resp_val = preset_data.get("responsibilities", "Lead the architecture and deployment of generative AI pipelines.")
        responsibilities = st.text_area(
            "Key Responsibilities & Deliverables",
            value=resp_val,
            rows=3,
            key="jd_input_resp",
            help="High-level milestones, projects, or duties expected for this role.",
        )

        generate_btn = st.button("Generate Tailored Job Description ✨", type="primary", use_container_width=True)

    if generate_btn:
        if not job_title.strip():
            st.error("Please enter a valid Job Title.")
            return

        with st.spinner("Synthesizing comprehensive Job Description via Google GenAI..."):
            try:
                engine = JobDescriptionGenerator()
                req_skills_list = [s.strip() for s in required_skills.split(",") if s.strip()]
                pref_skills_list = [s.strip() for s in preferred_skills.split(",") if s.strip()]

                jd_result = engine.generate(
                    job_title=job_title.strip(),
                    department=department.strip(),
                    experience_level=experience_level,
                    required_skills=req_skills_list,
                    preferred_skills=pref_skills_list,
                    responsibilities=responsibilities.strip(),
                    work_arrangement=work_arrangement,
                    company_context=company_context.strip(),
                    model_name=model_choice,
                )

                st.session_state["current_jd"] = jd_result
                # Add to history if unique
                if not any(h.title == jd_result.title and h.department == jd_result.department for h in st.session_state["jd_history"]):
                    st.session_state["jd_history"].insert(0, jd_result)

                st.toast("Job Description successfully generated!", icon="🎉")
            except Exception as exc:
                st.error(f"Failed to generate Job Description: {str(exc)}")
                return

    # Render Current / Selected Job Description
    active_jd: Optional[GeneratedJobDescription] = st.session_state.get("current_jd")

    if active_jd:
        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        st.subheader("2. Generated Job Description", divider=False)

        with st.container(border=True):
            header_col1, header_col2 = st.columns([3, 1])
            with header_col1:
                st.markdown(f"### {active_jd.title}")
                st.caption(f"**Department:** {active_jd.department} | **Seniority:** {active_jd.experience_level}")
            with header_col2:
                st.html(f"""
                <div style="text-align: right; margin-top: 0.5rem;">
                    {render_badge("AI Generated", "primary")}
                    {render_badge("Verified Format", "success")}
                </div>
                """)

            st.divider()

            # Section: Role Overview
            st.markdown("#### 📌 Role Overview & Business Impact")
            st.write(active_jd.role_overview)

            # Section: Core Responsibilities
            st.markdown("#### 🎯 Key Responsibilities")
            for resp in active_jd.key_responsibilities:
                st.markdown(f"• {resp}")

            st.divider()

            # Section: Skills Requirements
            sk_col1, sk_col2 = st.columns(2)
            with sk_col1:
                st.markdown("#### 🛠 Must-Have Skills & Experience")
                if active_jd.experience_requirements:
                    st.info(f"**Experience Requirement:** {active_jd.experience_requirements}")
                if active_jd.must_have_skills:
                    st.html(render_skill_chips_html(active_jd.must_have_skills))
                else:
                    st.caption("No specific must-have skills generated.")

            with sk_col2:
                st.markdown("#### ⭐ Preferred / Nice-to-Have Skills")
                if active_jd.nice_to_have_skills:
                    st.html(render_skill_chips_html(active_jd.nice_to_have_skills))
                else:
                    st.caption("No preferred skills specified.")

            # Section: Milestones & KPIs
            if active_jd.performance_metrics:
                st.divider()
                st.markdown("#### 📈 Key Milestones & Success Metrics (First 90-180 Days)")
                for idx, metric in enumerate(active_jd.performance_metrics, 1):
                    st.markdown(f"**{idx}.** {metric}")

            # Section: Candidate Evaluation Rubric
            if active_jd.evaluation_rubric:
                st.divider()
                st.markdown("#### 📋 Candidate Assessment & Interviewing Rubric")
                for rubric in active_jd.evaluation_rubric:
                    st.markdown(f"• {rubric}")

            # Section: Compensation & Benefits
            if active_jd.compensation_and_benefits:
                st.divider()
                st.markdown("#### 💼 Compensation & Workplace Benefits")
                st.write(active_jd.compensation_and_benefits)

            st.divider()

            # Action Buttons & Export
            act_col1, act_col2, act_col3 = st.columns([1.5, 1.5, 2])
            with act_col1:
                st.download_button(
                    label="Download JD (Markdown)",
                    data=active_jd.raw_markdown,
                    file_name=f"{active_jd.title.replace(' ', '_').lower()}_job_description.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
            with act_col2:
                if st.button("Copy / View Raw Markdown", use_container_width=True):
                    st.session_state["show_raw_jd_md"] = not st.session_state.get("show_raw_jd_md", False)

            with act_col3:
                if st.button("Tailor Candidate Resume to this JD →", type="primary", use_container_width=True):
                    # Set selected job or transition to Resume Studio
                    from src.models.schemas import JobPosting
                    synthetic_job = JobPosting(
                        job_id=f"gen_{abs(hash(active_jd.title)) % 100000}",
                        title=active_jd.title,
                        company=active_jd.department or "Target Organization",
                        location="Remote / Hybrid",
                        description=active_jd.role_overview + "\n" + "\n".join(active_jd.key_responsibilities),
                        skills=active_jd.must_have_skills + active_jd.nice_to_have_skills,
                    )
                    st.session_state["selected_job_for_cv"] = synthetic_job
                    AppStateManager.set_active_view("Resume Studio")
                    st.rerun()

            if st.session_state.get("show_raw_jd_md"):
                st.text_area("Full Markdown Job Description", value=active_jd.raw_markdown, height=300)

    # History Drawer
    if st.session_state.get("jd_history"):
        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        with st.expander(f"📁 Previously Generated Job Descriptions ({len(st.session_state['jd_history'])})"):
            for idx, hist_jd in enumerate(st.session_state["jd_history"]):
                h_col1, h_col2 = st.columns([3, 1])
                with h_col1:
                    st.write(f"**{hist_jd.title}** ({hist_jd.department}) - *{hist_jd.experience_level}*")
                with h_col2:
                    if st.button("Load Description", key=f"btn_load_hist_jd_{idx}"):
                        st.session_state["current_jd"] = hist_jd
                        st.rerun()
