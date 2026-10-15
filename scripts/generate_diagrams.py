"""
Generate publication-quality diagrams for the CPPE Mini Project Report.
Outputs:
1. report_diagrams/architecture_diagram.png (System Architecture)
2. report_diagrams/data_engineering_activity.png (Module 1 Activity Diagram)
3. report_diagrams/cloud_engineering_activity.png (Module 2 Activity Diagram)
4. report_diagrams/ai_engineering_activity.png (Module 3 Activity Diagram)
5. report_diagrams/security_engineering_activity.png (Module 4 Activity Diagram)
"""

import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUT_DIR = Path("report_diagrams")
OUT_DIR.mkdir(exist_ok=True)

# -------------------------------------------------------------
# Common style parameters
# -------------------------------------------------------------
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'


def draw_box(ax, x, y, w, h, text, color="#E8F0FE", edge="#1A73E8", lw=1.5, fontsize=10, bold=False, boxstyle="round,pad=0.3"):
    bbox_props = dict(boxstyle=boxstyle, facecolor=color, edgecolor=edge, linewidth=lw)
    weight = "bold" if bold else "normal"
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize,
            fontweight=weight, color="#202124", multialignment="center",
            bbox=bbox_props)


def draw_diamond(ax, x, y, size, text, color="#FEF7E0", edge="#F9AB00", fontsize=9):
    # Diamond decision polygon
    pts = [
        (x, y + size / 2),
        (x + size / 2, y + size),
        (x + size, y + size / 2),
        (x + size / 2, y)
    ]
    poly = patches.Polygon(pts, closed=True, facecolor=color, edgecolor=edge, linewidth=1.5)
    ax.add_patch(poly)
    ax.text(x + size / 2, y + size / 2, text, ha="center", va="center", fontsize=fontsize,
            fontweight="bold", color="#202124", multialignment="center")


def draw_arrow(ax, x1, y1, x2, y2, label="", color="#5F6368", lw=1.5, label_offset=(0, 0)):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, shrinkA=2, shrinkB=2)
    )
    if label:
        mx = (x1 + x2) / 2 + label_offset[0]
        my = (y1 + y2) / 2 + label_offset[1]
        ax.text(mx, my, label, ha="center", va="center", fontsize=8, color="#3C4043",
                bbox=dict(boxstyle="square,pad=0.15", facecolor="white", edgecolor="none", alpha=0.85))


def generate_architecture_diagram():
    fig, ax = plt.subplots(figsize=(13, 8.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Title
    ax.text(50, 97, "AI-Powered Resume & Job Description Generator: System Architecture",
            ha="center", va="center", fontsize=15, fontweight="bold", color="#1A73E8")

    # Subgraph Layer 1: Ingestion & Input (Top-Left)
    rect1 = patches.FancyBboxPatch((2, 64), 30, 28, boxstyle="round,pad=0.5", facecolor="#F8F9FA", edgecolor="#DADCE0", lw=1.2)
    ax.add_patch(rect1)
    ax.text(17, 89, "INGESTION & DATA LAYER", ha="center", va="center", fontsize=10, fontweight="bold", color="#5F6368")
    draw_box(ax, 4, 80, 26, 6, "Multi-Format Resume Upload\n(PDF, DOCX, TXT Parsing)", color="#E1F5FE", edge="#0288D1", fontsize=8.5, bold=True)
    draw_box(ax, 4, 72, 26, 6, "Kaggle 24-Industry Dataset\n(2,484 Resumes Corpus)", color="#E1F5FE", edge="#0288D1", fontsize=8.5)
    draw_box(ax, 4, 65, 26, 5.5, "Pydantic Schema Validation\n(ResumeProfile & DynamicJSON)", color="#E1F5FE", edge="#0288D1", fontsize=8)

    # Subgraph Layer 2: Recruiter Inputs (Top-Right)
    rect2 = patches.FancyBboxPatch((68, 64), 30, 28, boxstyle="round,pad=0.5", facecolor="#F8F9FA", edgecolor="#DADCE0", lw=1.2)
    ax.add_patch(rect2)
    ax.text(83, 89, "RECRUITER ENGINE LAYER", ha="center", va="center", fontsize=10, fontweight="bold", color="#5F6368")
    draw_box(ax, 70, 80, 26, 6, "Role Criteria Input\n(Title, Domain, Seniority, KPIs)", color="#FFF3E0", edge="#F57C00", fontsize=8.5, bold=True)
    draw_box(ax, 70, 72, 26, 6, "JD Prompt Assembler\n(Structured Schema Directives)", color="#FFF3E0", edge="#F57C00", fontsize=8.5)
    draw_box(ax, 70, 65, 26, 5.5, "Interview Rubric Synthesizer\n(Assessment Dimensions)", color="#FFF3E0", edge="#F57C00", fontsize=8)

    # Subgraph Layer 3: Core AI & Retrieval Core (Center)
    rect3 = patches.FancyBboxPatch((18, 33), 64, 27, boxstyle="round,pad=0.5", facecolor="#E8EAED", edgecolor="#BDC1C6", lw=1.5)
    ax.add_patch(rect3)
    ax.text(50, 57, "INTELLIGENCE, MATCHING & GOVERNANCE CORE", ha="center", va="center", fontsize=11, fontweight="bold", color="#202124")

    draw_box(ax, 20, 48, 28, 6.5, "Human-in-the-Loop (HITL) Gate\n(REQUIRES_REVIEW -> APPROVED)", color="#FCE8E6", edge="#C5221F", fontsize=8.5, bold=True)
    draw_box(ax, 52, 48, 28, 6.5, "Google Gemini 3.8 / 3.6 Flash\n(Structured JSON & STAR Rewrites)", color="#E8F0FE", edge="#1A73E8", fontsize=8.5, bold=True)
    draw_box(ax, 20, 36, 28, 9, "FAISS Dense Vector Store\n- IndexFlatIP (3072-dim Cosine)\n- Jobs Corpus (naukri_jobs)\n- In-Memory Fallback Cache", color="#E6F4EA", edge="#137333", fontsize=8)
    draw_box(ax, 52, 36, 28, 9, "RAG & Safety Guardrail Layer\n- Prompt Injection Interceptor\n- Curated Career Roadmaps\n- Citation Verification Engine", color="#FEF7E0", edge="#B06000", fontsize=8)

    # Subgraph Layer 4: Application & User Interface (Bottom)
    rect4 = patches.FancyBboxPatch((2, 2), 96, 27, boxstyle="round,pad=0.5", facecolor="#F8F9FA", edgecolor="#DADCE0", lw=1.2)
    ax.add_patch(rect4)
    ax.text(50, 26, "DELIVERY LAYER: STREAMLIT SAAS WORKSPACE (Light / Dark Themes)", ha="center", va="center", fontsize=10, fontweight="bold", color="#5F6368")

    draw_box(ax, 4, 7, 21, 15, "Candidate View\n- Verified Profile\n- Dynamic JSON\n- Skills Taxonomy\n- HITL Review", color="#EDE7F6", edge="#512DA8", fontsize=8.5)
    draw_box(ax, 28, 7, 21, 15, "Semantic Matching\n- Top-k Job Matches\n- Overlap Scoring\n- Skill Gap Analysis\n- Feedback Logging", color="#E8F5E9", edge="#2E7D32", fontsize=8.5)
    draw_box(ax, 51, 7, 21, 15, "Resume Studio\n- STAR CV Rewriter\n- ATS Optimization\n- Truth-Preserving\n- One-Click Export", color="#E3F2FD", edge="#1565C0", fontsize=8.5)
    draw_box(ax, 74, 7, 22, 15, "Recruiter & Mentor\n- Enterprise JD Gen\n- Interview Rubric\n- 24/7 AI Mentor\n- Audit Telemetry", color="#FFF8E1", edge="#FF8F00", fontsize=8.5)

    # Connections
    draw_arrow(ax, 17, 65, 30, 54.5, "Parsed Profile")
    draw_arrow(ax, 83, 65, 70, 54.5, "Role Specs")
    draw_arrow(ax, 34, 48, 34, 45, "Approved Vector")
    draw_arrow(ax, 48, 51, 52, 51, "Verified Data")
    draw_arrow(ax, 66, 48, 66, 45, "Inference")
    draw_arrow(ax, 34, 36, 14, 22, "Profile Sync")
    draw_arrow(ax, 38, 36, 38, 22, "Ranked Matches")
    draw_arrow(ax, 60, 36, 61, 22, "Tailored Bullets")
    draw_arrow(ax, 76, 36, 85, 22, "JDs & Mentoring")

    plt.tight_layout()
    plt.savefig(OUT_DIR / "architecture_diagram.png", bbox_inches="tight")
    plt.close()
    print("Saved architecture_diagram.png")


def generate_data_eng_activity():
    fig, ax = plt.subplots(figsize=(10, 11), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    ax.text(50, 97, "Activity Diagram: Module 1 – Data Engineering",
            ha="center", va="center", fontsize=14, fontweight="bold", color="#0288D1")

    # Start Node
    start = patches.Circle((50, 92), 2, facecolor="#202124", edgecolor="#202124")
    ax.add_patch(start)

    draw_arrow(ax, 50, 90, 50, 85)
    draw_box(ax, 28, 79, 44, 6, "1. Ingest Resume Document (PDF / DOCX)\nor Load Kaggle 24-Industry Resume Corpus", color="#E1F5FE", edge="#0288D1", bold=True)

    draw_arrow(ax, 50, 79, 50, 74)
    draw_box(ax, 30, 68, 40, 6, "2. Document Parser (PyPDF & python-docx)\nExtract Plain Text & Normalize Unicode", color="#E1F5FE", edge="#0288D1")

    draw_arrow(ax, 50, 68, 50, 63)
    draw_box(ax, 28, 57, 44, 6, "3. Extract Structured Fields into Pydantic\n(ResumeProfile & DynamicResumeJSON)", color="#E1F5FE", edge="#0288D1")

    draw_arrow(ax, 50, 57, 50, 52)
    draw_diamond(ax, 43, 42, 14, "Validation\nPassed?", color="#FEF7E0", edge="#F9AB00")

    # Validation No branch
    draw_arrow(ax, 43, 49, 15, 49, "No")
    draw_box(ax, 5, 46, 20, 6, "Raise ValidationError\n& Request Clean Upload", color="#FCE8E6", edge="#C5221F", fontsize=8)
    draw_arrow(ax, 15, 52, 28, 82)

    # Validation Yes branch
    draw_arrow(ax, 50, 42, 50, 37, "Yes")
    draw_box(ax, 26, 31, 48, 6, "4. Text Chunker & Competency Segmentation\n(Experience, Projects, Education, Skill Chips)", color="#E8F5E9", edge="#2E7D32")

    draw_arrow(ax, 50, 31, 50, 26)
    draw_box(ax, 28, 20, 44, 6, "5. Compute 3072-dim Embeddings\nvia Google gemini-embedding-001", color="#E8F5E9", edge="#2E7D32")

    draw_arrow(ax, 50, 20, 50, 15)
    draw_box(ax, 26, 9, 48, 6, "6. Cache Normalized Vectors & Populate\nFAISS IndexFlatIP (Cosine Metric)", color="#E8F5E9", edge="#2E7D32", bold=True)

    draw_arrow(ax, 50, 9, 50, 4)
    # End node
    end_outer = patches.Circle((50, 2.5), 2.2, facecolor="white", edgecolor="#202124", lw=1.5)
    end_inner = patches.Circle((50, 2.5), 1.4, facecolor="#202124", edgecolor="#202124")
    ax.add_patch(end_outer)
    ax.add_patch(end_inner)

    plt.tight_layout()
    plt.savefig(OUT_DIR / "data_engineering_activity.png", bbox_inches="tight")
    plt.close()
    print("Saved data_engineering_activity.png")


def generate_cloud_eng_activity():
    fig, ax = plt.subplots(figsize=(10, 11), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    ax.text(50, 97, "Activity Diagram: Module 2 – Cloud Engineering",
            ha="center", va="center", fontsize=14, fontweight="bold", color="#1565C0")

    # Start Node
    start = patches.Circle((50, 92), 2, facecolor="#202124", edgecolor="#202124")
    ax.add_patch(start)

    draw_arrow(ax, 50, 90, 50, 85)
    draw_box(ax, 26, 79, 48, 6, "1. Client Browser Sends HTTP GET\nto Streamlit Cloud / Localhost:8501", color="#E3F2FD", edge="#1565C0", bold=True)

    draw_arrow(ax, 50, 79, 50, 74)
    draw_box(ax, 28, 68, 44, 6, "2. Bootstrap Settings & Resolve Secrets\n(Hierarchy: .env -> OS Env -> Secrets)", color="#E3F2FD", edge="#1565C0")

    draw_arrow(ax, 50, 68, 50, 63)
    draw_box(ax, 26, 57, 48, 6, "3. Initialize AppStateManager Session State\n& Verify SQLite Database Connectivity", color="#E3F2FD", edge="#1565C0")

    draw_arrow(ax, 50, 57, 50, 52)
    draw_box(ax, 26, 46, 48, 6, "4. Inject Dynamic CSS Styling Tokens\n(Responsive Layout & Light/Dark Theme)", color="#E3F2FD", edge="#1565C0")

    draw_arrow(ax, 50, 46, 50, 41)
    draw_diamond(ax, 43, 31, 14, "Action\nEvent?", color="#FEF7E0", edge="#F9AB00")

    # Branch Left: View Navigation
    draw_arrow(ax, 43, 38, 20, 38, "Nav Click")
    draw_box(ax, 5, 29, 24, 7, "Route Workspace View\n(Overview, Profile, Studio,\nJD Gen, Jobs, Mentor)", color="#EDE7F6", edge="#512DA8", fontsize=8)

    # Branch Right: Theme Toggle
    draw_arrow(ax, 57, 38, 80, 38, "Theme Mode")
    draw_box(ax, 71, 29, 24, 7, "Update Theme Tokens\n(Dark/Light CSS Classes)\n& Re-render Shell", color="#FFF8E1", edge="#FF8F00", fontsize=8)

    # Rejoin at State Persistence
    draw_arrow(ax, 17, 29, 40, 20)
    draw_arrow(ax, 83, 29, 60, 20)
    draw_arrow(ax, 50, 31, 50, 20, "Input Submit")

    draw_box(ax, 26, 14, 48, 6, "5. Synchronize State to SQLite & Audit Trail\nand Stream Reactive UI Updates to Client", color="#E8F5E9", edge="#2E7D32", bold=True)

    draw_arrow(ax, 50, 14, 50, 6)
    # End node
    end_outer = patches.Circle((50, 3.5), 2.2, facecolor="white", edgecolor="#202124", lw=1.5)
    end_inner = patches.Circle((50, 3.5), 1.4, facecolor="#202124", edgecolor="#202124")
    ax.add_patch(end_outer)
    ax.add_patch(end_inner)

    plt.tight_layout()
    plt.savefig(OUT_DIR / "cloud_engineering_activity.png", bbox_inches="tight")
    plt.close()
    print("Saved cloud_engineering_activity.png")


def generate_ai_eng_activity():
    fig, ax = plt.subplots(figsize=(12, 11), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    ax.text(50, 97, "Activity Diagram: Module 3 – AI Engineering",
            ha="center", va="center", fontsize=14, fontweight="bold", color="#2E7D32")

    # Start Node
    start = patches.Circle((50, 92), 2, facecolor="#202124", edgecolor="#202124")
    ax.add_patch(start)

    draw_arrow(ax, 50, 90, 50, 85)
    draw_box(ax, 30, 80, 40, 5.5, "1. Select AI Generation Mode", color="#E8F5E9", edge="#2E7D32", bold=True)

    # Fork Bar
    draw_arrow(ax, 50, 80, 50, 74)
    fork_bar = patches.Rectangle((10, 73), 80, 1.2, facecolor="#202124", edgecolor="#202124")
    ax.add_patch(fork_bar)

    # Lane 1: Resume Studio
    draw_arrow(ax, 20, 73, 20, 66)
    draw_box(ax, 4, 59, 32, 7, "Path A: Resume Tailoring\nLoad Approved Profile &\nTarget Job Description", color="#E8F0FE", edge="#1A73E8", fontsize=8.5)
    draw_arrow(ax, 20, 59, 20, 53)
    draw_box(ax, 4, 46, 32, 7, "Diagnose Skill Gaps &\nAssemble STAR Rewrite Prompt\n(Situation, Task, Action, Result)", color="#E8F0FE", edge="#1A73E8", fontsize=8)
    draw_arrow(ax, 20, 46, 20, 40)
    draw_box(ax, 4, 33, 32, 7, "Call Gemini 3.8 Flash Engine\nGenerate Truth-Preserving\nBullets & Executive Summary", color="#E8F0FE", edge="#1A73E8", fontsize=8)

    # Lane 2: JD Generator
    draw_arrow(ax, 50, 73, 50, 66)
    draw_box(ax, 35, 59, 30, 7, "Path B: Enterprise JD Gen\nIngest Role Criteria (Title,\nDomain, Seniority Tier, KPIs)", color="#FFF3E0", edge="#F57C00", fontsize=8.5)
    draw_arrow(ax, 50, 59, 50, 53)
    draw_box(ax, 35, 46, 30, 7, "Assemble Structured Prompt\nwith GeneratedJobDescription\nPydantic JSON Schema", color="#FFF3E0", edge="#F57C00", fontsize=8)
    draw_arrow(ax, 50, 46, 50, 40)
    draw_box(ax, 35, 33, 30, 7, "Synthesize Deliverables,\nMust-Have vs Preferred Skills\n& Candidate Interview Rubric", color="#FFF3E0", edge="#F57C00", fontsize=8)

    # Lane 3: Semantic Vector Matching
    draw_arrow(ax, 80, 73, 80, 66)
    draw_box(ax, 66, 59, 30, 7, "Path C: FAISS Job Matching\nEmbed Candidate Vector\nvia gemini-embedding-001", color="#E8F5E9", edge="#2E7D32", fontsize=8.5)
    draw_arrow(ax, 80, 59, 80, 53)
    draw_box(ax, 66, 46, 30, 7, "Execute Inner-Product Search\nover 3072-dim FAISS Index\n(Mathematically Cosine Metric)", color="#E8F5E9", edge="#2E7D32", fontsize=8)
    draw_arrow(ax, 80, 46, 80, 40)
    draw_box(ax, 66, 33, 30, 7, "Rank Matching Positions &\nCalculate Skill Overlap\nand Missing Competency Sets", color="#E8F5E9", edge="#2E7D32", fontsize=8)

    # Join Bar
    draw_arrow(ax, 20, 33, 20, 24)
    draw_arrow(ax, 50, 33, 50, 24)
    draw_arrow(ax, 80, 33, 80, 24)
    join_bar = patches.Rectangle((10, 23), 80, 1.2, facecolor="#202124", edgecolor="#202124")
    ax.add_patch(join_bar)

    draw_arrow(ax, 50, 23, 50, 17)
    draw_box(ax, 26, 10, 48, 6.5, "2. Render Structured Outputs, Quantified Metrics\n& Export Clean Markdown / Tailored Artifacts", color="#E1F5FE", edge="#0288D1", bold=True)

    draw_arrow(ax, 50, 10, 50, 4)
    # End node
    end_outer = patches.Circle((50, 2), 2, facecolor="white", edgecolor="#202124", lw=1.5)
    end_inner = patches.Circle((50, 2), 1.3, facecolor="#202124", edgecolor="#202124")
    ax.add_patch(end_outer)
    ax.add_patch(end_inner)

    plt.tight_layout()
    plt.savefig(OUT_DIR / "ai_engineering_activity.png", bbox_inches="tight")
    plt.close()
    print("Saved ai_engineering_activity.png")


def generate_security_eng_activity():
    fig, ax = plt.subplots(figsize=(10, 11.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    ax.text(50, 97, "Activity Diagram: Module 4 – Security Engineering",
            ha="center", va="center", fontsize=14, fontweight="bold", color="#C5221F")

    # Start Node
    start = patches.Circle((50, 92), 2, facecolor="#202124", edgecolor="#202124")
    ax.add_patch(start)

    draw_arrow(ax, 50, 90, 50, 85)
    draw_box(ax, 28, 79, 44, 6, "1. Ingest User Query or Workflow Request\n(Career Mentor Query / Resume Parsing)", color="#FCE8E6", edge="#C5221F", bold=True)

    draw_arrow(ax, 50, 79, 50, 74)
    draw_box(ax, 26, 68, 48, 6, "2. Pre-Execution Safety Inspection\nScan Regex Filters, Injection & Secret Keywords", color="#FCE8E6", edge="#C5221F")

    draw_arrow(ax, 50, 68, 50, 63)
    draw_diamond(ax, 43, 53, 14, "Security\nViolation?", color="#FEF7E0", edge="#F9AB00")

    # Violation = Yes
    draw_arrow(ax, 57, 60, 82, 60, "Yes")
    draw_box(ax, 72, 49, 24, 7, "Log Security Threat\nin AuditLogger &\nReturn Refusal Message", color="#FCE8E6", edge="#C5221F", fontsize=8)
    draw_arrow(ax, 84, 49, 84, 10)

    # Violation = No
    draw_arrow(ax, 50, 53, 50, 48, "No")
    draw_diamond(ax, 43, 38, 14, "Profile\nApproved?", color="#FEF7E0", edge="#F9AB00")

    # Approval = No
    draw_arrow(ax, 43, 45, 18, 45, "No")
    draw_box(ax, 6, 37, 24, 7, "Lock Downstream Matching\nDisplay Review Banner\n(Enforce State Gate)", color="#FEF7E0", edge="#B06000", fontsize=8)
    draw_arrow(ax, 18, 37, 18, 10)

    # Approval = Yes
    draw_arrow(ax, 50, 38, 50, 32, "Yes")
    draw_box(ax, 26, 26, 48, 6, "3. Query Vector Store with Strict Semantic Grounding\nRetrieve Verified Document Chunks with Citations", color="#E8F5E9", edge="#2E7D32")

    draw_arrow(ax, 50, 26, 50, 20)
    draw_box(ax, 26, 14, 48, 6, "4. Mask Sensitive Credentials & Persist Event\nin Audit Trail with Latency & Safety Telemetry", color="#E8F5E9", edge="#2E7D32", bold=True)

    draw_arrow(ax, 50, 14, 50, 7)
    draw_arrow(ax, 84, 10, 53, 4)
    draw_arrow(ax, 18, 10, 47, 4)

    # End node
    end_outer = patches.Circle((50, 3.5), 2.2, facecolor="white", edgecolor="#202124", lw=1.5)
    end_inner = patches.Circle((50, 3.5), 1.4, facecolor="#202124", edgecolor="#202124")
    ax.add_patch(end_outer)
    ax.add_patch(end_inner)

    plt.tight_layout()
    plt.savefig(OUT_DIR / "security_engineering_activity.png", bbox_inches="tight")
    plt.close()
    print("Saved security_engineering_activity.png")


if __name__ == "__main__":
    generate_architecture_diagram()
    generate_data_eng_activity()
    generate_cloud_eng_activity()
    generate_ai_eng_activity()
    generate_security_eng_activity()
    print("All diagrams generated successfully!")
