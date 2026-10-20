"""
app.py
JobTailor-AI: LaTeX ATS Resume Optimizer & Application Tracker
Features Overleaf-style LaTeX/PDF Split View, Zero-Fabrication Tailoring, and Multi-User Support.
"""

import streamlit as st
import pandas as pd
import json
import base64
import os
from datetime import datetime
from pypdf import PdfReader
import io

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

# Set page config
st.set_page_config(
    page_title="JobTailor-AI | ATS Resume Optimizer & Portal",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (Overleaf / Clean Corporate aesthetic)
st.markdown(
    """
    <style>
    .main { background-color: #f8fafc; }
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .metric-card {
        background-color: white;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .badge-matched {
        background-color: #dcfce7;
        color: #15803d;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        margin: 2px;
        display: inline-block;
    }
    .badge-missing {
        background-color: #fee2e2;
        color: #b91c1c;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        margin: 2px;
        display: inline-block;
    }
    .status-badge {
        font-weight: bold;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize database
init_db(default_daisy_tex=DEFAULT_DAISY_TEX, default_shashwat_tex=DEFAULT_SHASHWAT_TEX)

# ----------------- SIDEBAR: MULTI-USER PROFILE -----------------
st.sidebar.title("📄 JobTailor-AI")
st.sidebar.markdown("**ATS Optimization & LaTeX Portal**")
st.sidebar.divider()

users = get_all_users()
if not users:
    st.error("No user profiles found. Please initialize the database.")
    st.stop()

user_names = [u["name"] for u in users] + ["+ Add New User"]
selected_user_name = st.sidebar.selectbox("Select Active Candidate Profile:", user_names, index=0)

if selected_user_name == "+ Add New User":
    st.sidebar.subheader("Create New Profile")
    new_name = st.sidebar.text_input("Full Name")
    new_email = st.sidebar.text_input("Email")
    new_phone = st.sidebar.text_input("Phone")
    new_headline = st.sidebar.text_input("Professional Headline")
    if st.sidebar.button("Save Profile"):
        if new_name:
            new_uid = create_user(new_name, new_email, new_phone, new_headline, DEFAULT_SHASHWAT_TEX)
            st.sidebar.success(f"Profile created for {new_name}!")
            st.rerun()
    st.stop()

# Active user object
active_user = next(u for u in users if u["name"] == selected_user_name)
st.sidebar.info(f"**Candidate:** {active_user['name']}\n\n**Email:** {active_user['email']}\n\n**Headline:** {active_user.get('headline', 'N/A')}")

st.sidebar.divider()
st.sidebar.markdown("### AI Optimizer Settings (Optional)")
ai_provider = st.sidebar.selectbox("Engine:", ["Heuristic Engine (Free / Offline)", "Google Gemini AI", "OpenAI GPT-4o"])
api_key = ""
if ai_provider != "Heuristic Engine (Free / Offline)":
    api_key = st.sidebar.text_input("Enter API Key:", type="password", help="Your API key stays local and is not saved to disk.")

st.sidebar.divider()
st.sidebar.caption("⚡ Built with Streamlit, Python & TeXLive Cloud Engine\n\n🛡️ Strict Zero-Lie Guardrails Enforced")

# ----------------- MAIN TABS -----------------
tab1, tab2, tab3 = st.tabs(["🎯 Tailor & Overleaf View", "📊 Application Tracker & CRM", "👤 Master Resume Manager"])

# ==============================================================================
# TAB 1: TAILOR & OVERLEAF VIEW
# ==============================================================================
with tab1:
    st.markdown("### 🎯 Job Description & ATS Tailoring")
    
    col_meta1, col_meta2, col_meta3 = st.columns([1.5, 1.5, 1])
    with col_meta1:
        company_name = st.text_input("Target Company Name *", placeholder="e.g. Deloitte, Microsoft, Google")
    with col_meta2:
        job_title = st.text_input("Target Role Title *", placeholder="e.g. Analyst | D365 F&O - Functional SCM")
    with col_meta3:
        req_id = st.text_input("Requisition ID / Code", placeholder="e.g. 108410")

    col_meta4, col_meta5 = st.columns([2, 1])
    with col_meta4:
        job_url = st.text_input("Job Posting URL", placeholder="https://deloitte.com/careers/...")
    with col_meta5:
        job_location = st.text_input("Job Location", placeholder="e.g. Bengaluru, India")

    st.markdown("#### 📝 Job Description (JD)")
    uploaded_jd_file = st.file_uploader("Upload JD (PDF or TXT) or paste below:", type=["pdf", "txt"])
    
    default_jd_text = ""
    if uploaded_jd_file:
        if uploaded_jd_file.name.endswith(".pdf"):
            reader = PdfReader(uploaded_jd_file)
            default_jd_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        else:
            default_jd_text = uploaded_jd_file.read().decode("utf-8", errors="ignore")

    jd_input = st.text_area(
        "Paste Full Job Description:",
        value=default_jd_text,
        height=180,
        placeholder="Paste requirements, responsibilities, educational qualifications and key skills...",
    )

    col_btn1, col_btn2 = st.columns([2, 4])
    with col_btn1:
        tailor_clicked = st.button("🚀 Analyze JD & Tailor Resume", use_container_width=True, type="primary")

    # Session state initialization for tailored resume
    if "current_tailored_latex" not in st.session_state:
        st.session_state["current_tailored_latex"] = active_user["master_latex"]
    if "current_pdf_bytes" not in st.session_state:
        st.session_state["current_pdf_bytes"] = None
    if "current_ats_stats" not in st.session_state:
        st.session_state["current_ats_stats"] = None

    if tailor_clicked:
        if not jd_input.strip():
            st.error("Please paste or upload a Job Description to proceed.")
        else:
            with st.spinner("Analyzing JD keywords and tailoring LaTeX code with Zero-Fabrication guardrails..."):
                if ai_provider == "Google Gemini AI" and api_key:
                    new_tex, stats = tailor_resume_with_ai(
                        active_user["master_latex"], jd_input, company_name, job_title, api_key, provider="gemini"
                    )
                elif ai_provider == "OpenAI GPT-4o" and api_key:
                    new_tex, stats = tailor_resume_with_ai(
                        active_user["master_latex"], jd_input, company_name, job_title, api_key, provider="openai"
                    )
                else:
                    new_tex, stats = tailor_resume_heuristically(
                        active_user["master_latex"], jd_input, company_name, job_title
                    )

                st.session_state["current_tailored_latex"] = new_tex
                st.session_state["current_ats_stats"] = stats

                # Compile immediately
                pdf_bytes, err_msg = compile_latex_to_pdf(new_tex)
                if pdf_bytes:
                    st.session_state["current_pdf_bytes"] = pdf_bytes
                    st.success("Resume tailored & compiled successfully!")
                else:
                    st.warning(f"Tailoring complete, but PDF compile warning: {err_msg}")

    # ATS Stats Ribbon if available
    if st.session_state.get("current_ats_stats"):
        stats = st.session_state["current_ats_stats"]
        st.divider()
        st.markdown("#### 📊 ATS Keyword Analysis & Score")
        
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.metric("Base Resume ATS Match", f"{stats['score_before']}%")
        with m_col2:
            delta_val = f"+{round(stats['score_after'] - stats['score_before'], 1)}%"
            st.metric("Tailored Resume ATS Match", f"{stats['score_after']}%", delta=delta_val)
        with m_col3:
            st.metric("Total Extracted JD Keywords", len(stats["matched_keywords"]) + len(stats["missing_keywords"]))

        col_kw1, col_kw2 = st.columns(2)
        with col_kw1:
            st.markdown(f"**✅ Matched Keywords ({len(stats['matched_keywords'])}):**")
            kw_html = "".join([f'<span class="badge-matched">{k}</span>' for k in stats["matched_keywords"][:25]])
            st.markdown(kw_html, unsafe_allow_html=True)
        with col_kw2:
            st.markdown(f"**⚠️ Missing Keywords ({len(stats['missing_keywords'])}):**")
            missing_html = "".join([f'<span class="badge-missing">{k}</span>' for k in stats["missing_keywords"][:25]])
            st.markdown(missing_html, unsafe_allow_html=True)

    st.divider()

    # ----------------- OVERLEAF-STYLE SPLIT SCREEN -----------------
    st.markdown("### 🖥️ Overleaf-Style Split Screen (LaTeX Editor + Live PDF Viewer)")
    editor_col, preview_col = st.columns([1, 1], gap="medium")

    with editor_col:
        st.subheader("📄 LaTeX Source Editor")
        st.caption("You can directly edit the code below and re-compile anytime.")
        
        edited_latex = st.text_area(
            "LaTeX Code",
            value=st.session_state["current_tailored_latex"],
            height=680,
            label_visibility="collapsed",
            key="latex_code_editor",
        )

        btn_c1, btn_c2, btn_c3 = st.columns([1, 1, 1.2])
        with btn_c1:
            if st.button("🔄 Re-Compile PDF", use_container_width=True):
                with st.spinner("Compiling LaTeX to PDF..."):
                    pdf_bytes, err = compile_latex_to_pdf(edited_latex)
                    if pdf_bytes:
                        st.session_state["current_pdf_bytes"] = pdf_bytes
                        st.session_state["current_tailored_latex"] = edited_latex
                        st.success("Re-compiled successfully!")
                        st.rerun()
                    else:
                        st.error(f"Compilation failed: {err}")

        with btn_c2:
            st.download_button(
                label="📥 Download .tex",
                data=edited_latex,
                file_name=f"{company_name or 'Resume'}_{job_title or 'Tailored'}.tex",
                mime="text/x-tex",
                use_container_width=True,
            )

        with btn_c3:
            if st.button("💾 Save to Tracker", use_container_width=True, type="secondary"):
                if not company_name or not job_title:
                    st.error("Please enter Company Name and Target Role Title before saving.")
                else:
                    score = st.session_state.get("current_ats_stats", {}).get("score_after", 0.0)
                    matched_str = json.dumps(st.session_state.get("current_ats_stats", {}).get("matched_keywords", []))
                    missing_str = json.dumps(st.session_state.get("current_ats_stats", {}).get("missing_keywords", []))
                    
                    app_id = save_application(
                        user_id=active_user["id"],
                        company=company_name,
                        job_title=job_title,
                        requisition_id=req_id,
                        location=job_location,
                        job_url=job_url,
                        job_description=jd_input,
                        ats_score=score,
                        matched_keywords=matched_str,
                        missing_keywords=missing_str,
                        tailored_latex=edited_latex,
                        pdf_bytes=st.session_state.get("current_pdf_bytes"),
                        status="Applied",
                        notes=f"Auto-tailored for {company_name}",
                    )
                    st.success(f"Saved application #{app_id} to Tracker!")

    with preview_col:
        st.subheader("📑 Live PDF Preview")
        if st.session_state.get("current_pdf_bytes"):
            pdf_bytes = st.session_state["current_pdf_bytes"]
            
            # Download PDF button on top of viewer
            st.download_button(
                label="📥 Download PDF Document",
                data=pdf_bytes,
                file_name=f"{company_name or active_user['name']}_{job_title or 'Resume'}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary",
            )
            
            # Embed PDF using HTML iframe
            base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
            pdf_display = f"""
                <iframe 
                    src="data:application/pdf;base64,{base64_pdf}#toolbar=1&navpanes=0&scrollbar=1" 
                    width="100%" 
                    height="680" 
                    type="application/pdf"
                    style="border: 1px solid #cbd5e1; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);"
                >
                </iframe>
            """
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.info("No PDF compiled yet. Click **'Analyze JD & Tailor Resume'** or **'Re-Compile PDF'** to generate live preview.")


# ==============================================================================
# TAB 2: APPLICATION TRACKER & CRM
# ==============================================================================
with tab2:
    st.markdown("### 📊 Job Application Tracker & CRM")
    st.caption(f"Tracking all job openings, tailored resumes, and interview stages for **{active_user['name']}**.")

    apps = get_applications_for_user(active_user["id"])

    if not apps:
        st.info("No applications logged yet. Tailor a resume in Tab 1 and click 'Save to Tracker'!")
    else:
        # Metrics summary
        total_apps = len(apps)
        applied_count = sum(1 for a in apps if a["status"] == "Applied")
        interview_count = sum(1 for a in apps if "Interview" in a["status"])
        avg_score = round(sum(a["ats_score"] for a in apps) / total_apps, 1)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Applications", total_apps)
        c2.metric("Active Submissions", applied_count)
        c3.metric("Interviews Scheduled", interview_count)
        c4.metric("Avg ATS Match", f"{avg_score}%")

        st.divider()

        # Filter & Search
        f_col1, f_col2 = st.columns([1, 2])
        with f_col1:
            status_filter = st.selectbox(
                "Filter by Status:",
                ["All", "Applied", "Screening", "Interview Scheduled", "Offer", "Rejected", "Draft"],
            )
        with f_col2:
            search_query = st.text_input("Search Company or Role:", placeholder="e.g. Deloitte, SCM, Microsoft...")

        filtered_apps = apps
        if status_filter != "All":
            filtered_apps = [a for a in filtered_apps if a["status"] == status_filter]
        if search_query:
            q = search_query.lower()
            filtered_apps = [
                a for a in filtered_apps
                if q in a["company"].lower() or q in a["job_title"].lower() or (a["location"] and q in a["location"].lower())
            ]

        st.markdown(f"**Showing {len(filtered_apps)} applications:**")

        for app in filtered_apps:
            with st.expander(f"🏢 **{app['company']}** — {app['job_title']} ({app['applied_date'] or 'Date N/A'}) | ATS: {app['ats_score']}%"):
                col_d1, col_d2 = st.columns([2, 1])
                with col_d1:
                    st.markdown(f"**Requisition ID:** {app.get('requisition_id') or 'N/A'}")
                    st.markdown(f"**Location:** {app.get('location') or 'N/A'}")
                    if app.get("job_url"):
                        st.markdown(f"**Link:** [Job Posting URL]({app['job_url']})")
                    st.markdown(f"**Notes:** {app.get('notes') or 'None'}")
                with col_d2:
                    curr_status = app["status"]
                    status_options = ["Draft", "Applied", "Screening", "Interview Scheduled", "Offer", "Rejected"]
                    new_st = st.selectbox(
                        "Status",
                        status_options,
                        index=status_options.index(curr_status) if curr_status in status_options else 0,
                        key=f"status_sel_{app['id']}",
                    )
                    if new_st != curr_status:
                        update_application_status(app["id"], new_st)
                        st.success(f"Updated to {new_st}")
                        st.rerun()

                st.markdown("---")
                btn_a1, btn_a2, btn_a3 = st.columns([1, 1, 1])
                
                # Check for PDF
                pdf_file_path = os.path.join(PDF_DIR, app["pdf_filename"]) if app.get("pdf_filename") else None
                if pdf_file_path and os.path.exists(pdf_file_path):
                    with open(pdf_file_path, "rb") as f_pdf:
                        pdf_data = f_pdf.read()
                    with btn_a1:
                        st.download_button(
                            label="📥 Download Submitted PDF",
                            data=pdf_data,
                            file_name=f"{app['company']}_{app['job_title']}_Resume.pdf",
                            mime="application/pdf",
                            key=f"dl_pdf_{app['id']}",
                        )
                else:
                    with btn_a1:
                        st.caption("PDF binary not stored on disk.")

                with btn_a2:
                    st.download_button(
                        label="📥 Download LaTeX Code",
                        data=app["tailored_latex"],
                        file_name=f"{app['company']}_{app['job_title']}.tex",
                        mime="text/x-tex",
                        key=f"dl_tex_{app['id']}",
                    )

                with btn_a3:
                    if st.button("🗑️ Delete Application", key=f"del_{app['id']}"):
                        delete_application(app["id"])
                        st.warning(f"Deleted #{app['id']}.")
                        st.rerun()


# ==============================================================================
# TAB 3: MASTER RESUME MANAGER
# ==============================================================================
with tab3:
    st.markdown(f"### 👤 Master Base Resume — {active_user['name']}")
    st.caption("This is your foundational source of truth. The tailoring engine uses this template to customize resumes for specific job descriptions.")

    u_col1, u_col2 = st.columns([1, 1])
    with u_col1:
        st.subheader("Master LaTeX Source")
        master_edit = st.text_area(
            "Master LaTeX",
            value=active_user["master_latex"],
            height=620,
            key="master_tex_area",
        )
        if st.button("💾 Save Master Resume Updates", type="primary"):
            update_user_master_latex(active_user["id"], master_edit)
            st.success("Master resume updated in database!")
            st.rerun()

    with u_col2:
        st.subheader("Master PDF Preview")
        if st.button("🔄 Test Compile Master Resume"):
            with st.spinner("Compiling master resume..."):
                m_pdf, m_err = compile_latex_to_pdf(master_edit)
                if m_pdf:
                    st.session_state["master_pdf_bytes"] = m_pdf
                    st.success("Master resume compiled successfully!")
                else:
                    st.error(f"Error compiling: {m_err}")

        if st.session_state.get("master_pdf_bytes"):
            b64_m = base64.b64encode(st.session_state["master_pdf_bytes"]).decode("utf-8")
            st.markdown(
                f'<iframe src="data:application/pdf;base64,{b64_m}#toolbar=1" width="100%" height="620" type="application/pdf" style="border: 1px solid #cbd5e1; border-radius: 8px;"></iframe>',
                unsafe_allow_html=True,
            )
        else:
            st.info("Click 'Test Compile Master Resume' to view your current master PDF.")
