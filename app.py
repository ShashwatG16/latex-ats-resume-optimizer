"""
app.py
JobTailor-AI Studio: Modern Overleaf-Style ATS Resume Optimizer & Application CRM
Redesigned UI for Streamlit with Dark/Glass Studio Header, Code-IDE Split Screen,
High-DPI Live PDF Canvas, and Responsive CRM Table.
"""

import streamlit as st
import pandas as pd
import json
import base64
import os
import io
from datetime import datetime
from pypdf import PdfReader
from dotenv import load_dotenv

# Load environment variables from .env (project root or user home)
ENV_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(ENV_FILE_PATH)
load_dotenv(os.path.expanduser("~/.env"))

from core.database import (
    init_db,
    get_all_users,
    get_user_by_id,
    update_user_master_latex,
    create_user,
    save_application,
    get_applications_for_user,
    get_application_by_id,
    update_application_status,
    update_application_resume,
    delete_application,
    PDF_DIR,
)
from core.templates import DEFAULT_DAISY_TEX, DEFAULT_SHASHWAT_TEX
from core.compiler import compile_latex_to_pdf, pdf_to_base64_data_uri
from core.ats_engine import evaluate_ats_match, tailor_resume_heuristically, tailor_resume_with_ai

# Page configuration
st.set_page_config(
    page_title="JobTailor-AI Studio | ATS Resume Optimizer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database
init_db(default_daisy_tex=DEFAULT_DAISY_TEX, default_shashwat_tex=DEFAULT_SHASHWAT_TEX)

# ==============================================================================
# MODERN STUDIO CSS DESIGN SYSTEM
# ==============================================================================
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

    <style>
    :root {
        color-scheme: light dark;
        --brand-indigo: #6366f1;
        --brand-violet: #8b5cf6;
        --emerald-accent: #10b981;
        --scrollbar-thumb: light-dark(#cbd5e1, #334155);
        --scrollbar-track: light-dark(#f1f5f9, #0f172a);
        accent-color: var(--brand-indigo);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Reduce excessive top padding in Streamlit main container */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 97% !important;
    }

    /* Sleek Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0b0f19 0%, #111827 100%) !important;
        border-right: 1px solid #1e293b !important;
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div,
    [data-testid="stSidebar"] .stTextInput input {
        background-color: #1e293b !important;
        border-color: #334155 !important;
        color: #f8fafc !important;
        border-radius: 10px !important;
    }

    /* Top Hero Studio Banner */
    .studio-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 60%, #311042 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 18px 24px;
        margin-bottom: 18px;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        box-shadow: 0 10px 30px -10px rgba(79, 70, 229, 0.25);
    }
    .studio-brand {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .studio-logo {
        width: 42px;
        height: 42px;
        border-radius: 12px;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 16px;
        color: #ffffff;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.45);
    }
    .studio-title {
        color: #ffffff;
        font-size: 1.25rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .studio-pill {
        font-size: 11px;
        font-weight: 600;
        padding: 2px 10px;
        border-radius: 999px;
        background: rgba(99, 102, 241, 0.2);
        border: 1px solid rgba(129, 140, 248, 0.4);
        color: #c7d2fe;
    }
    .studio-sub {
        color: #94a3b8;
        font-size: 0.8rem;
        margin: 2px 0 0 0;
    }
    .studio-badges {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
    }
    .studio-stat-pill {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(148, 163, 184, 0.2);
        padding: 6px 14px;
        border-radius: 12px;
        font-size: 12px;
        color: #e2e8f0;
        font-weight: 500;
    }

    /* Modern Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: light-dark(#f1f5f9, #111827);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid light-dark(#e2e8f0, #1f2937);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px !important;
        padding: 8px 18px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3) !important;
    }

    /* Buttons */
    .stButton > button, .stDownloadButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        padding: 0.45rem 1rem !important;
        transition: all 0.18s ease !important;
    }
    .stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35) !important;
    }
    .stButton > button[kind="primary"]:hover, .stDownloadButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.5) !important;
    }

    /* Overleaf Dark Monospace Editor Styling */
    div[data-testid="stTextArea"] textarea[aria-label="LaTeX Code"],
    div[data-testid="stTextArea"] textarea[aria-label="Master LaTeX"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12.8px !important;
        line-height: 1.55 !important;
        background-color: #090d16 !important;
        color: #e2e8f0 !important;
        border: 1px solid #1e293b !important;
        border-radius: 0 0 12px 12px !important;
        padding: 16px !important;
        color-scheme: dark;
        accent-color: var(--brand-indigo);
    }

    /* IDE Pane Header Bar */
    .ide-header {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-bottom: none;
        border-radius: 12px 12px 0 0;
        padding: 10px 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: #e2e8f0;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: -8px;
    }
    .ide-dots {
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .ide-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
    }

    /* Keyword Chips */
    .kw-chip-matched {
        background: rgba(16, 185, 129, 0.14);
        color: light-dark(#047857, #34d399);
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 11.5px;
        font-weight: 600;
        margin: 3px;
        display: inline-block;
    }
    .kw-chip-missing {
        background: rgba(244, 63, 94, 0.12);
        color: light-dark(#be123c, #fb7185);
        border: 1px solid rgba(244, 63, 94, 0.3);
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 11.5px;
        font-weight: 600;
        margin: 3px;
        display: inline-block;
    }

    /* KPI Glass Cards */
    .kpi-card {
        background: light-dark(#ffffff, #111827);
        border: 1px solid light-dark(#e2e8f0, #1f2937);
        border-radius: 14px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    .kpi-label {
        font-size: 11.5px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: light-dark(#64748b, #94a3b8);
    }
    .kpi-value {
        font-size: 1.65rem;
        font-weight: 800;
        margin-top: 4px;
        color: light-dark(#0f172a, #f8fafc);
    }

    /* Responsive Accessible CRM Table (modern-web-guidance: responsive-table) */
    .table-wrapper {
        overflow: auto;
        max-inline-size: 100%;
        max-block-size: min(500px, 75vh);
        container-type: inline-size;
        border: 1px solid light-dark(#e2e8f0, #1f2937);
        border-radius: 12px;
        background: light-dark(#ffffff, #111827);
        margin-bottom: 1rem;
    }
    .crm-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 13px;
    }
    .crm-table thead {
        position: sticky;
        inset-block-start: 0;
        z-index: 2;
        background: light-dark(#f1f5f9, #1e293b);
    }
    .crm-table th, .crm-table td {
        padding: 10px 14px;
        text-align: left;
        border-bottom: 1px solid light-dark(#e2e8f0, #1f2937);
    }
    .crm-table tbody th {
        position: sticky;
        inset-inline-start: 0;
        z-index: 1;
        background: light-dark(#ffffff, #111827);
        font-weight: 700;
    }
    @container (width < 600px) {
        .crm-table, .crm-table thead, .crm-table tbody, .crm-table tr, .crm-table th, .crm-table td {
            display: block;
        }
        .crm-table thead { display: none; }
        .crm-table tr { margin-block-end: 1rem; border: 1px solid #334155; }
        .crm-table tbody th { position: sticky; inset-block-start: 0; z-index: 2; background: #1e293b; }
        .crm-table {
            --label-2: "Role";
            --label-3: "Req ID";
            --label-4: "ATS Match";
            --label-5: "Stage";
            --label-6: "Date";
        }
        .crm-table td:nth-child(2)::before { content: var(--label-2) ": "; font-weight: 600; }
        .crm-table td:nth-child(3)::before { content: var(--label-3) ": "; font-weight: 600; }
        .crm-table td:nth-child(4)::before { content: var(--label-4) ": "; font-weight: 600; }
        .crm-table td:nth-child(5)::before { content: var(--label-5) ": "; font-weight: 600; }
        .crm-table td:nth-child(6)::before { content: var(--label-6) ": "; font-weight: 600; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def save_key_to_dotenv(key_name: str, key_val: str):
    """Saves an API key to the local .env file (which is gitignored)."""
    lines = []
    if os.path.exists(ENV_FILE_PATH):
        with open(ENV_FILE_PATH, "r", encoding="utf-8") as f:
            lines = [line for line in f.readlines() if not line.strip().startswith(f"{key_name}=")]
    lines.append(f"{key_name}={key_val.strip()}\n")
    with open(ENV_FILE_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)
    os.environ[key_name] = key_val.strip()


def render_pdf_preview(pdf_bytes: bytes, height: int = 680, key_prefix: str = "pdf"):
    """
    Renders PDF bytes in a sleek paper-card preview using high-DPI PNG rendering (via PyMuPDF)
    or Streamlit's interactive st.pdf viewer.
    """
    num_pages = 1
    try:
        doc_reader = PdfReader(io.BytesIO(pdf_bytes))
        num_pages = len(doc_reader.pages)
    except Exception:
        pass

    top_c1, top_c2 = st.columns([1.3, 1.7])
    with top_c1:
        if num_pages == 1:
            st.markdown(
                '<span style="background:rgba(16,185,129,0.15);color:#10b981;border:1px solid rgba(16,185,129,0.35);padding:4px 10px;border-radius:999px;font-size:12px;font-weight:700;">✓ Strict 1-Page Verified</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<span style="background:rgba(245,158,11,0.15);color:#f59e0b;border:1px solid rgba(245,158,11,0.35);padding:4px 10px;border-radius:999px;font-size:12px;font-weight:700;">⚠️ {num_pages} Pages (Exceeds 1-Page Target)</span>',
                unsafe_allow_html=True,
            )
    with top_c2:
        view_mode = st.radio(
            "Renderer:",
            ["High-DPI Paper Canvas", "Interactive PDF Viewer"],
            horizontal=True,
            label_visibility="collapsed",
            key=f"{key_prefix}_view_mode",
        )

    if view_mode == "Interactive PDF Viewer":
        try:
            st.pdf(pdf_bytes, height=height, key=f"{key_prefix}_st_pdf")
            return
        except Exception:
            pass

    # Default High-DPI Paper Canvas via PyMuPDF (fitz) — 100% immune to browser iframe blocking
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page_idx in range(len(doc)):
            page = doc.load_page(page_idx)
            pix = page.get_pixmap(dpi=200)
            img_b64 = base64.b64encode(pix.tobytes("png")).decode("utf-8")
            st.markdown(
                f"""
                <div style="background:#1e293b; padding:14px; border-radius:14px; border:1px solid #334155; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.25); margin-top:6px;">
                    <img src="data:image/png;base64,{img_b64}" style="width:100%; height:auto; border-radius:6px; display:block; background:white;" alt="Compiled Resume Page {page_idx + 1}" />
                </div>
                """,
                unsafe_allow_html=True,
            )
        doc.close()
    except Exception:
        st.pdf(pdf_bytes, height=height, key=f"{key_prefix}_fallback_pdf")


# ==============================================================================
# SIDEBAR: PROFILE & AI ENGINE CONTROL CENTER
# ==============================================================================
st.sidebar.markdown(
    """
    <div style="display:flex;align-items:center;gap:10px;padding-bottom:8px;">
        <div style="width:34px;height:34px;border-radius:10px;background:linear-gradient(135deg,#6366f1,#a855f7);display:flex;align-items:center;justify-content:center;font-weight:800;color:white;">JT</div>
        <div>
            <div style="font-weight:800;font-size:15px;line-height:1.1;">JobTailor-AI</div>
            <div style="font-size:11px;color:#94a3b8;">Studio v2.0 · Zero-Fabrication</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.divider()

users = get_all_users()
if not users:
    st.error("No user profiles found. Please initialize the database.")
    st.stop()

user_names = [u["name"] for u in users] + ["+ Add New Candidate"]
selected_user_name = st.sidebar.selectbox("👤 Active Candidate Profile", user_names, index=0)

if selected_user_name == "+ Add New Candidate":
    st.sidebar.subheader("Create Candidate Profile")
    new_name = st.sidebar.text_input("Full Name *")
    new_email = st.sidebar.text_input("Email")
    new_phone = st.sidebar.text_input("Phone")
    new_headline = st.sidebar.text_input("Professional Headline")
    if st.sidebar.button("✨ Create Profile", type="primary", use_container_width=True):
        if new_name:
            create_user(new_name, new_email, new_phone, new_headline, DEFAULT_SHASHWAT_TEX)
            st.sidebar.success(f"Profile created for {new_name}!")
            st.rerun()
    st.stop()

active_user = next(u for u in users if u["name"] == selected_user_name)

# Auto-compile master PDF on first load or user switch so the split screen is immediately populated!
if st.session_state.get("active_user_id") != active_user["id"]:
    st.session_state["active_user_id"] = active_user["id"]
    st.session_state["current_tailored_latex"] = active_user["master_latex"]
    st.session_state["latex_code_editor"] = active_user["master_latex"]
    st.session_state["current_ats_stats"] = None
    st.session_state["master_pdf_bytes"] = None
    init_pdf, _ = compile_latex_to_pdf(active_user["master_latex"])
    st.session_state["current_pdf_bytes"] = init_pdf

st.sidebar.markdown(
    f"""
    <div style="background:#1e293b;border:1px solid #334155;border-radius:12px;padding:12px;font-size:12px;margin-top:4px;">
        <div style="font-weight:700;font-size:13px;color:#f8fafc;">{active_user['name']}</div>
        <div style="color:#94a3b8;margin-top:2px;">📧 {active_user['email']}</div>
        <div style="color:#cbd5e1;margin-top:6px;font-size:11.5px;line-height:1.35;">{active_user.get('headline', 'N/A')}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.divider()
st.sidebar.markdown("#### 🤖 AI Tailoring Engine")

env_gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
env_openai_key = os.environ.get("OPENAI_API_KEY") or ""

default_engine_idx = 1 if env_gemini_key else (2 if env_openai_key else 0)
ai_provider = st.sidebar.selectbox(
    "Optimization Engine",
    ["Heuristic Engine (Free / Offline)", "Google Gemini AI", "OpenAI GPT-4o"],
    index=default_engine_idx,
)
api_key = ""
model_name = ""

if ai_provider == "Google Gemini AI":
    model_name = st.sidebar.selectbox(
        "Gemini Model",
        ["gemini-3.8-flash", "gemini-4-argon", "gemini-flash-latest", "gemini-3.7-flash", "gemini-3.5-flash", "gemini-3.1-pro-preview"],
        index=0,
    )
    if env_gemini_key:
        st.sidebar.markdown(
            '<div style="background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.35);color:#34d399;padding:6px 10px;border-radius:8px;font-size:11.5px;font-weight:600;margin-bottom:6px;">✓ Gemini API Key Active (.env)</div>',
            unsafe_allow_html=True,
        )
    api_key_input = st.sidebar.text_input(
        "Gemini API Key Override",
        value=env_gemini_key,
        type="password",
        help="Loaded automatically from .env",
    )
    api_key = api_key_input.strip()
    if api_key and api_key != env_gemini_key:
        if st.sidebar.button("💾 Save Key to .env", use_container_width=True):
            save_key_to_dotenv("GEMINI_API_KEY", api_key)
            st.sidebar.success("Saved GEMINI_API_KEY to .env!")
elif ai_provider == "OpenAI GPT-4o":
    model_name = st.sidebar.selectbox("OpenAI Model", ["gpt-4o", "gpt-4o-mini"], index=0)
    api_key_input = st.sidebar.text_input("OpenAI API Key", value=env_openai_key, type="password")
    api_key = api_key_input.strip()
    if api_key and api_key != env_openai_key:
        if st.sidebar.button("💾 Save Key to .env", use_container_width=True):
            save_key_to_dotenv("OPENAI_API_KEY", api_key)
            st.sidebar.success("Saved OPENAI_API_KEY to .env!")

st.sidebar.divider()
st.sidebar.caption("🛡️ **Zero-Lie Guardrail Active**\nTitles, employers, dates, degrees & GPA are strictly preserved.")

# ==============================================================================
# TOP STUDIO HERO HEADER
# ==============================================================================
user_apps = get_applications_for_user(active_user["id"])
engine_badge_label = f"Gemini ({model_name})" if ai_provider == "Google Gemini AI" else (f"OpenAI ({model_name})" if ai_provider == "OpenAI GPT-4o" else "Heuristic Engine")

st.markdown(
    f"""
    <div class="studio-banner">
        <div class="studio-brand">
            <div class="studio-logo">JT</div>
            <div>
                <div class="studio-title">
                    JobTailor-AI Studio
                    <span class="studio-pill">Overleaf Split-IDE</span>
                </div>
                <p class="studio-sub">Zero-Fabrication LaTeX ATS Resume Optimizer &amp; Multi-Candidate Application CRM</p>
            </div>
        </div>
        <div class="studio-badges">
            <div class="studio-stat-pill">👤 <strong>{active_user['name']}</strong></div>
            <div class="studio-stat-pill">🤖 Engine: <strong>{engine_badge_label}</strong></div>
            <div class="studio-stat-pill">📂 Tracked Apps: <strong>{len(user_apps)}</strong></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# MAIN STUDIO TABS
# ==============================================================================
tab1, tab2, tab3 = st.tabs([
    "🎯 Tailor & Overleaf Studio",
    f"📊 Application CRM ({len(user_apps)})",
    "👤 Master LaTeX Manager",
])

# ==============================================================================
# TAB 1: TAILOR & OVERLEAF STUDIO
# ==============================================================================
with tab1:
    with st.expander("📋 **Step 1: Target Job Opportunity & JD Input** (Click to collapse/expand for full-screen IDE)", expanded=True):
        r1_c1, r1_c2, r1_c3, r1_c4, r1_c5 = st.columns([1.4, 1.5, 0.9, 1.1, 1.3])
        with r1_c1:
            company_name = st.text_input("Target Company *", placeholder="e.g. Deloitte, Google, Microsoft")
        with r1_c2:
            job_title = st.text_input("Target Role Title *", placeholder="e.g. Analyst | D365 F&O SCM")
        with r1_c3:
            req_id = st.text_input("Req ID", placeholder="e.g. 108410")
        with r1_c4:
            job_location = st.text_input("Location", placeholder="Bengaluru / Remote")
        with r1_c5:
            job_url = st.text_input("Job Posting URL", placeholder="https://...")

        jd_col_left, jd_col_right = st.columns([2.3, 1], gap="medium")
        with jd_col_right:
            uploaded_jd_file = st.file_uploader("📎 Upload JD (.pdf or .txt)", type=["pdf", "txt"])
            default_jd_text = ""
            if uploaded_jd_file:
                if uploaded_jd_file.name.endswith(".pdf"):
                    reader = PdfReader(uploaded_jd_file)
                    default_jd_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                else:
                    default_jd_text = uploaded_jd_file.read().decode("utf-8", errors="ignore")

            tailor_clicked = st.button(
                "🚀 Analyze JD & Tailor Resume",
                use_container_width=True,
                type="primary",
            )

        with jd_col_left:
            jd_input = st.text_area(
                "Paste Full Job Description (Responsibilities, Skills & Qualifications):",
                value=default_jd_text,
                height=145,
                placeholder="Paste the complete job description here to extract high-value ATS keywords and tailor your LaTeX resume...",
            )

    # Trigger Tailoring
    if tailor_clicked:
        if not jd_input.strip():
            st.error("Please paste or upload a Job Description first.")
        elif ai_provider != "Heuristic Engine (Free / Offline)" and not api_key:
            st.error(f"Please configure your **{ai_provider} API Key** in the left sidebar.")
        else:
            with st.spinner(f"Tailoring resume via {engine_badge_label} & compiling PDF via TeXLive..."):
                if ai_provider == "Google Gemini AI" and api_key:
                    new_tex, stats = tailor_resume_with_ai(
                        active_user["master_latex"], jd_input, company_name, job_title, api_key, provider="gemini", model_name=model_name
                    )
                elif ai_provider == "OpenAI GPT-4o" and api_key:
                    new_tex, stats = tailor_resume_with_ai(
                        active_user["master_latex"], jd_input, company_name, job_title, api_key, provider="openai", model_name=model_name
                    )
                else:
                    new_tex, stats = tailor_resume_heuristically(
                        active_user["master_latex"], jd_input, company_name, job_title
                    )

                st.session_state["current_tailored_latex"] = new_tex
                st.session_state["latex_code_editor"] = new_tex
                st.session_state["current_ats_stats"] = stats

                if stats.get("ai_error"):
                    st.warning(f"⚠️ AI Notice (fell back to Heuristic Engine): {stats['ai_error']}")

                pdf_bytes, err_msg = compile_latex_to_pdf(new_tex)
                if pdf_bytes:
                    st.session_state["current_pdf_bytes"] = pdf_bytes
                    st.toast("Resume tailored & compiled to PDF!", icon="✅")
                else:
                    st.warning(f"Tailoring complete, but PDF compile warning: {err_msg}")

    # ATS Score & Keyword Pills Ribbon
    if st.session_state.get("current_ats_stats"):
        stats = st.session_state["current_ats_stats"]
        delta_num = round(stats["score_after"] - stats["score_before"], 1)
        delta_sign = f"+{delta_num}%" if delta_num >= 0 else f"{delta_num}%"

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(
                f'<div class="kpi-card"><div class="kpi-label">Base Master Match</div><div class="kpi-value">{stats["score_before"]}%</div></div>',
                unsafe_allow_html=True,
            )
        with k2:
            st.markdown(
                f'<div class="kpi-card"><div class="kpi-label">Tailored ATS Score</div><div class="kpi-value" style="color:#10b981;">{stats["score_after"]}% <span style="font-size:14px;background:rgba(16,185,129,0.15);padding:3px 8px;border-radius:99px;">{delta_sign}</span></div></div>',
                unsafe_allow_html=True,
            )
        with k3:
            st.markdown(
                f'<div class="kpi-card"><div class="kpi-label">Matched Keywords</div><div class="kpi-value" style="color:#6366f1;">{len(stats["matched_keywords"])}</div></div>',
                unsafe_allow_html=True,
            )
        with k4:
            st.markdown(
                f'<div class="kpi-card"><div class="kpi-label">Missing Keywords</div><div class="kpi-value" style="color:#f43f5e;">{len(stats["missing_keywords"])}</div></div>',
                unsafe_allow_html=True,
            )

        with st.expander("🔍 **View Matched & Missing ATS Keywords Breakdown**", expanded=True):
            kw_c1, kw_c2 = st.columns(2)
            with kw_c1:
                st.caption(f"✅ **Matched in Tailored Resume ({len(stats['matched_keywords'])})**")
                matched_chips = "".join([f'<span class="kw-chip-matched">✓ {k}</span>' for k in stats["matched_keywords"][:35]])
                st.markdown(matched_chips or "None", unsafe_allow_html=True)
            with kw_c2:
                st.caption(f"⚠️ **Unmatched JD Keywords ({len(stats['missing_keywords'])})**")
                missing_chips = "".join([f'<span class="kw-chip-missing">+ {k}</span>' for k in stats["missing_keywords"][:35]])
                st.markdown(missing_chips or "None!", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ==============================================================================
    # OVERLEAF-STYLE SPLIT WORKSPACE (LEFT IDE + RIGHT LIVE PAPER PREVIEW)
    # ==============================================================================
    editor_col, preview_col = st.columns([1.02, 0.98], gap="medium")

    with editor_col:
        # Action Bar above IDE
        act1, act2, act3 = st.columns([1.1, 0.9, 1.1])
        with act1:
            recompile_clicked = st.button("▶ Re-Compile PDF", use_container_width=True, type="primary")
        with act2:
            st.download_button(
                label="📥 Download .tex",
                data=st.session_state.get("current_tailored_latex", active_user["master_latex"]),
                file_name=f"{company_name or active_user['name']}_{job_title or 'Resume'}.tex".replace(" ", "_"),
                mime="text/x-tex",
                use_container_width=True,
            )
        with act3:
            save_crm_clicked = st.button("💾 Save to CRM Tracker", use_container_width=True)

        line_count = len(st.session_state.get("current_tailored_latex", "").splitlines())
        st.markdown(
            f"""
            <div class="ide-header">
                <div class="ide-dots">
                    <span class="ide-dot" style="background:#ef4444;"></span>
                    <span class="ide-dot" style="background:#f59e0b;"></span>
                    <span class="ide-dot" style="background:#10b981;"></span>
                    <span style="margin-left:8px;font-family:'JetBrains Mono',monospace;">resume_tailored.tex</span>
                </div>
                <span style="color:#64748b;font-family:'JetBrains Mono',monospace;">{line_count} lines · UTF-8 · LaTeX</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        edited_latex = st.text_area(
            "LaTeX Code",
            value=st.session_state["current_tailored_latex"],
            height=720,
            label_visibility="collapsed",
            key="latex_code_editor",
        )

        if recompile_clicked:
            with st.spinner("Compiling LaTeX via TeXLive pdflatex..."):
                pdf_bytes, err = compile_latex_to_pdf(edited_latex)
                if pdf_bytes:
                    st.session_state["current_pdf_bytes"] = pdf_bytes
                    st.session_state["current_tailored_latex"] = edited_latex
                    st.toast("Re-compiled PDF successfully!", icon="✅")
                    st.rerun()
                else:
                    st.error(f"Compilation failed:\n{err}")

        if save_crm_clicked:
            if not company_name or not job_title:
                st.error("Please enter **Target Company** and **Target Role Title** in Step 1 before saving to CRM.")
            else:
                score = (st.session_state.get("current_ats_stats") or {}).get("score_after", 0.0)
                matched_str = json.dumps((st.session_state.get("current_ats_stats") or {}).get("matched_keywords", []))
                missing_str = json.dumps((st.session_state.get("current_ats_stats") or {}).get("missing_keywords", []))

                app_id = save_application(
                    user_id=active_user["id"],
                    company=company_name,
                    job_title=job_title,
                    requisition_id=req_id,
                    location=job_location,
                    job_url=job_url,
                    job_description=jd_input or "Manual Tailor",
                    ats_score=score,
                    matched_keywords=matched_str,
                    missing_keywords=missing_str,
                    tailored_latex=edited_latex,
                    pdf_bytes=st.session_state.get("current_pdf_bytes"),
                    status="Applied",
                    notes=f"Tailored via {engine_badge_label}",
                )
                st.toast(f"Saved application #{app_id} ({company_name}) to CRM!", icon="🎉")
                st.success(f"Saved application #{app_id} ({company_name} — {job_title}) to Application CRM!")

    with preview_col:
        if st.session_state.get("current_pdf_bytes"):
            pdf_bytes = st.session_state["current_pdf_bytes"]
            st.download_button(
                label="📥 Download Compiled PDF Document",
                data=pdf_bytes,
                file_name=f"{company_name or active_user['name']}_{job_title or 'Resume'}.pdf".replace(" ", "_"),
                mime="application/pdf",
                use_container_width=True,
                type="primary",
            )
            render_pdf_preview(pdf_bytes, height=700, key_prefix="tailored_pdf")
        else:
            if st.button("⚡ Compile Current LaTeX to Live PDF", use_container_width=True, type="primary"):
                with st.spinner("Compiling LaTeX to PDF..."):
                    pdf_bytes, err = compile_latex_to_pdf(edited_latex)
                    if pdf_bytes:
                        st.session_state["current_pdf_bytes"] = pdf_bytes
                        st.rerun()
                    else:
                        st.error(f"Compilation failed: {err}")


# ==============================================================================
# TAB 2: APPLICATION TRACKER & CRM
# ==============================================================================
with tab2:
    apps = get_applications_for_user(active_user["id"])

    if not apps:
        st.info("No applications logged yet. Tailor a resume in the **Tailor & Overleaf Studio** tab and click **'💾 Save to CRM Tracker'**!")
    else:
        total_apps = len(apps)
        applied_count = sum(1 for a in apps if a["status"] in ("Applied", "Screening"))
        interview_count = sum(1 for a in apps if "Interview" in a["status"] or a["status"] == "Offer")
        avg_score = round(sum(a["ats_score"] for a in apps) / total_apps, 1)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Applications</div><div class="kpi-value">{total_apps}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Active Pipeline</div><div class="kpi-value" style="color:#6366f1;">{applied_count}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Interviews & Offers</div><div class="kpi-value" style="color:#10b981;">{interview_count}</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Average ATS Score</div><div class="kpi-value">{avg_score}%</div></div>', unsafe_allow_html=True)

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        f_col1, f_col2 = st.columns([1, 2])
        with f_col1:
            status_filter = st.selectbox(
                "Filter Stage",
                ["All", "Applied", "Screening", "Interview Scheduled", "Offer", "Rejected", "Draft"],
            )
        with f_col2:
            search_query = st.text_input("🔍 Search Company, Role, or Location", placeholder="e.g. Deloitte, D365, Bengaluru...")

        filtered_apps = apps
        if status_filter != "All":
            filtered_apps = [a for a in filtered_apps if a["status"] == status_filter]
        if search_query:
            q = search_query.lower()
            filtered_apps = [
                a for a in filtered_apps
                if q in a["company"].lower() or q in a["job_title"].lower() or (a["location"] and q in a["location"].lower())
            ]

        # Accessible Responsive Summary Table
        rows_html = ""
        for a in filtered_apps:
            rows_html += f"""
            <tr>
                <th>{a['company']}</th>
                <td>{a['job_title']}</td>
                <td>{a.get('requisition_id') or '—'} · {a.get('location') or '—'}</td>
                <td><span class="kw-chip-matched">{a['ats_score']}%</span></td>
                <td><strong>{a['status']}</strong></td>
                <td>{a.get('applied_date') or '—'}</td>
            </tr>
            """
        st.markdown(
            f"""
            <div tabindex="0" role="region" aria-labelledby="crm-caption" class="table-wrapper">
                <table class="crm-table">
                    <caption id="crm-caption" style="display:none;">Applications for {active_user['name']}</caption>
                    <thead>
                        <tr>
                            <th>Company</th>
                            <th>Target Role</th>
                            <th>Req ID &amp; Location</th>
                            <th>ATS Score</th>
                            <th>Stage</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### 🛠️ Manage Individual Applications & Download Submissions")
        for app in filtered_apps:
            with st.expander(f"🏢 **{app['company']}** — {app['job_title']}  |  ATS: **{app['ats_score']}%**  |  Stage: **{app['status']}**"):
                col_d1, col_d2 = st.columns([2, 1])
                with col_d1:
                    st.markdown(f"**Requisition ID:** `{app.get('requisition_id') or 'N/A'}`  ·  **Location:** {app.get('location') or 'N/A'}")
                    if app.get("job_url"):
                        st.markdown(f"**Job Posting:** [{app['job_url']}]({app['job_url']})")
                    st.markdown(f"**Notes:** {app.get('notes') or 'None'}")
                with col_d2:
                    curr_status = app["status"]
                    status_options = ["Draft", "Applied", "Screening", "Interview Scheduled", "Offer", "Rejected"]
                    new_st = st.selectbox(
                        "Update Stage",
                        status_options,
                        index=status_options.index(curr_status) if curr_status in status_options else 0,
                        key=f"status_sel_{app['id']}",
                    )
                    if new_st != curr_status:
                        update_application_status(app["id"], new_st)
                        st.toast(f"Updated {app['company']} to {new_st}", icon="✅")
                        st.rerun()

                btn_a1, btn_a2, btn_a3, btn_a4 = st.columns([1, 1, 1, 1])
                pdf_file_path = os.path.join(PDF_DIR, app["pdf_filename"]) if app.get("pdf_filename") else None
                with btn_a1:
                    if pdf_file_path and os.path.exists(pdf_file_path):
                        with open(pdf_file_path, "rb") as f_pdf:
                            pdf_data = f_pdf.read()
                        st.download_button(
                            label="📥 Download PDF",
                            data=pdf_data,
                            file_name=f"{app['company']}_{app['job_title']}_Resume.pdf",
                            mime="application/pdf",
                            key=f"dl_pdf_{app['id']}",
                            use_container_width=True,
                        )
                    else:
                        st.caption("No PDF stored")
                with btn_a2:
                    st.download_button(
                        label="📥 Download .tex",
                        data=app["tailored_latex"],
                        file_name=f"{app['company']}_{app['job_title']}.tex",
                        mime="text/x-tex",
                        key=f"dl_tex_{app['id']}",
                        use_container_width=True,
                    )
                with btn_a3:
                    if st.button("🎯 Load into Studio", key=f"load_studio_{app['id']}", use_container_width=True):
                        st.session_state["current_tailored_latex"] = app["tailored_latex"]
                        st.session_state["latex_code_editor"] = app["tailored_latex"]
                        pdf_b, _ = compile_latex_to_pdf(app["tailored_latex"])
                        st.session_state["current_pdf_bytes"] = pdf_b
                        st.toast(f"Loaded {app['company']} resume into Studio tab!", icon="🎯")
                        st.rerun()
                with btn_a4:
                    if st.button("🗑️ Delete", key=f"del_{app['id']}", use_container_width=True):
                        delete_application(app["id"])
                        st.rerun()


# ==============================================================================
# TAB 3: MASTER RESUME MANAGER
# ==============================================================================
with tab3:
    st.markdown(f"#### 👤 Master Base LaTeX Resume — **{active_user['name']}**")
    st.caption("Your single source of truth. Any updates saved here become the base template for future JD tailoring.")

    u_col1, u_col2 = st.columns([1.02, 0.98], gap="medium")
    with u_col1:
        m_btn1, m_btn2 = st.columns(2)
        with m_btn1:
            save_master_btn = st.button("💾 Save Master LaTeX to DB", type="primary", use_container_width=True)
        with m_btn2:
            compile_master_btn = st.button("🔄 Compile & Preview Master PDF", use_container_width=True)

        st.markdown(
            """
            <div class="ide-header">
                <div class="ide-dots">
                    <span class="ide-dot" style="background:#ef4444;"></span>
                    <span class="ide-dot" style="background:#f59e0b;"></span>
                    <span class="ide-dot" style="background:#10b981;"></span>
                    <span style="margin-left:8px;font-family:'JetBrains Mono',monospace;">master_resume.tex</span>
                </div>
                <span style="color:#64748b;font-family:'JetBrains Mono',monospace;">Source of Truth</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        master_edit = st.text_area(
            "Master LaTeX",
            value=active_user["master_latex"],
            height=660,
            label_visibility="collapsed",
            key="master_tex_area",
        )

        if save_master_btn:
            update_user_master_latex(active_user["id"], master_edit)
            st.session_state["current_tailored_latex"] = master_edit
            st.session_state["latex_code_editor"] = master_edit
            st.toast("Master resume updated in database!", icon="✅")
            st.rerun()

        if compile_master_btn:
            with st.spinner("Compiling master resume..."):
                m_pdf, m_err = compile_latex_to_pdf(master_edit)
                if m_pdf:
                    st.session_state["master_pdf_bytes"] = m_pdf
                else:
                    st.error(f"Error compiling: {m_err}")

    with u_col2:
        master_pdf_to_show = st.session_state.get("master_pdf_bytes") or st.session_state.get("current_pdf_bytes")
        if master_pdf_to_show:
            render_pdf_preview(master_pdf_to_show, height=660, key_prefix="master_pdf")
        else:
            st.info("Click **'🔄 Compile & Preview Master PDF'** to render your master resume.")
