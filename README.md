# JobTailor-AI: LaTeX ATS Resume Optimizer & Application Portal

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

> **A dual-view ATS resume optimization portal and job application tracker. Upload any Job Description (JD), instantly tailor your master LaTeX resume to pass applicant tracking systems with ZERO fabrications, and preview/download compiled PDFs and LaTeX source in an Overleaf-style split workspace.**

**Author:** Shashwat Kumar Gautam ([@ShashwatG16](https://github.com/ShashwatG16))  
**Stack:** Python, Streamlit, SQLite, TeXLive Cloud Engine, PyPDF, Regex AST Keyword Matcher  

---

## 📌 Problem & Why This Exists

1. **The ATS Keyword Barrier:** Top tech and enterprise roles filter candidates through Applicant Tracking Systems (Workday, Greenhouse, Taleo) that rank candidates by exact keyword and domain terminology frequency.
2. **The "Hallucination" Trap:** Standard AI resume tools invent false experiences, change graduation dates, or fabricate certifications, leading to instant disqualification during technical interviews.
3. **The Compilation Friction:** Traditional LaTeX resumes require heavy local TeXLive/MikTeX setups (>5 GB) or tedious Overleaf copy-pasting for every application.
4. **Scattered Application Tracking:** Job seekers lose track of which specific resume variant was submitted to which company, causing embarrassing mismatches when interviewers reference submitted bullets.

**JobTailor-AI** solves this by unifying **Intelligent ATS Keyword Tailoring**, **Zero-Lie Guardrails**, **Instant Cloud LaTeX-to-PDF Compilation**, and a **Full Application CRM** in one local portal.

---

## ✨ Core Features

### 1. 🖥️ Overleaf-Style Split Screen (LaTeX Editor + Live PDF Viewer)
- **Left Panel:** Full LaTeX source editor with line-level control and instant `🔄 Re-Compile PDF` button.
- **Right Panel:** Live rendered PDF preview embedded via interactive viewer (zoom, inspect, scroll).
- **Dual One-Click Downloads:** Download the final submission-ready `.pdf` or the raw `.tex` source code.
- **Zero Local TeX Installation Required:** Powered by an ultra-fast TeXLive cloud sync compiler (sub-3s compilation) that fully supports `fontawesome5`, `hyperref`, `titlesec`, and custom geometry.

### 2. 🛡️ Strict Zero-Fabrication Guardrails
- **100% Factual Integrity:** The engine mathematically separates styling/keyword framing from factual ground truths:
  - ❌ **NEVER** alters candidate degrees, university names, GPAs, or graduation dates.
  - ❌ **NEVER** changes employer names, job titles, or dates of employment.
  - ❌ **NEVER** invents fake certifications, awards, or patents.
  - ✅ **Re-prioritizes & reframes** genuine skills, methodologies, testing types, and project bullets to mirror the JD's exact vocabulary.

### 3. 📊 ATS Match Scorer & Missing Keyword Breakdown
- Real-time pre- and post-tailoring ATS match percentage delta (e.g. `42% → 88%`).
- Visual keyword pills highlighting **Matched Keywords** (green) and high-priority **Missing Keywords** (red).

### 4. 👥 Multi-User Profile Support
- Manage separate profiles (e.g. Daisy Phukan, Shashwat Gautam, or any custom candidate).
- Each candidate has their own persistent **Master Base Resume** in the database.
- Easily test-compile and update master resumes at any time.

### 5. 🗄️ Application Tracker & CRM (SQLite Persistence)
- Automatically saves every customized resume to a local SQLite database (`data/applications.db`).
- Tracks:
  - Target Company & Role Title
  - Requisition ID, Location & Job URL
  - Applied Date & ATS Match %
  - Full Job Description text & tailored LaTeX code
  - Compiled PDF saved directly to disk (`data/compiled_pdfs/`)
  - Application Status (`Draft`, `Applied`, `Screening`, `Interview Scheduled`, `Offer`, `Rejected`)
- Search and filter applications by company name, role, or stage.

---

## 🛠️ Repository Architecture

```text
latex-ats-resume-optimizer/
│
├── app.py                      # Main Streamlit web application & Overleaf-style UI
├── core/
│   ├── database.py             # SQLite persistence for Users, Master Resumes & Applications
│   ├── compiler.py             # LaTeX-to-PDF sync cloud engine + local compiler fallback
│   ├── ats_engine.py           # ATS keyword analyzer, scorer & strict no-lie tailoring logic
│   └── templates.py            # Pre-seeded master LaTeX templates
├── data/
│   ├── applications.db         # Persistent SQLite database (auto-generated)
│   └── compiled_pdfs/          # Local storage for compiled application PDFs
├── requirements.txt            # Minimal, production-pinned Python dependencies
├── .gitignore                  # Clean git ignore rules
└── README.md                   # System documentation & setup guide
```

---

## 💻 Quickstart & Local Execution

### 1. Clone Repository & Setup
```bash
git clone https://github.com/ShashwatG16/latex-ats-resume-optimizer.git
cd latex-ats-resume-optimizer

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch Application
```bash
streamlit run app.py
```
The portal will launch in your default browser at `http://localhost:8501`.

---

## 📄 License & Attribution

Distributed under the **MIT License**. Created by [Shashwat Kumar Gautam](https://github.com/ShashwatG16) for transparent, high-integrity job application optimization.
