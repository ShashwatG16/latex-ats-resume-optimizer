# PROJECT_CONTEXT.md — JobTailor-AI (latex-ats-resume-optimizer)

> Handoff document. Paste or attach this file at the start of a new conversation to continue work on this project.

## 1. What this project is
A local Streamlit portal that:
- Takes a Job Description (pasted or uploaded as PDF/TXT).
- Tailors a user's **master LaTeX resume** to the JD's keywords **without fabricating anything** (titles, employers, dates, degrees, GPA and awards must never change; only the summary, skills ordering and bullet framing may change).
- Shows an **Overleaf-style split view**: LaTeX editor on the left, live compiled PDF on the right, with downloads for both .pdf and .tex.
- Supports **multiple users**, each with one master LaTeX resume that is updated over time.
- Tracks every application (company, role, req ID, JD, ATS score, tailored LaTeX, PDF, status) in SQLite.

- **Owner:** Shashwat Kumar Gautam. GitHub: **ShashwatG16** (git config email: iit2020030@iiita.ac.in)
- **Local path:** `d:\SHASHWAT\latex-ats-resume-optimizer\`
- **Remote:** `https://ShashwatG16@github.com/ShashwatG16/latex-ats-resume-optimizer.git`
- **Users seeded:** Daisy Phukan, Shashwat Gautam

## 2. Current status
- 2 local commits on `main`: the initial commit, plus "align repository links to ShashwatG16".
- `python test_app.py` passes 5/5 tests (database, ATS scoring, heuristic tailoring, cloud compile, save application).
- `streamlit run app.py` starts on http://localhost:8501.
- **Push status: UNVERIFIED.** The agent's push attempts failed: Windows Credential Manager has `Daizy-Mgmt` cached (403 error), and the browser auth popup can't appear from a background shell. The user then ran the push from their own terminal. Confirm by checking https://github.com/ShashwatG16/latex-ats-resume-optimizer. If it's empty, run `git push -u origin main` from a desktop PowerShell and sign in as ShashwatG16.

## 3. Architecture
```
app.py               Streamlit UI: Tab 1 Tailor + split view, Tab 2 Tracker/CRM, Tab 3 Master Resume Manager
core/database.py     SQLite (data/applications.db): users, applications; PDFs saved in data/compiled_pdfs/
core/compiler.py     LaTeX→PDF: POST to https://latex.ytotech.com/builds/sync (pdflatex), fallback to local pdflatex/xelatex/tectonic
core/ats_engine.py   Keyword extraction (regex high-value phrases + top unigrams), ATS match %, heuristic tailoring, optional Gemini/OpenAI tailoring with a strict no-fabrication system prompt
core/templates.py    Seed master LaTeX for Daisy and Shashwat (Jake Gutierrez template)
test_app.py          Smoke tests
```
Findings:
- No local TeX is installed on this machine. latexonline.cc fails because it lacks `fontawesome5`. **latex.ytotech.com works** and returns HTTP 201 with the PDF bytes.
- `pypdf` is installed (user site) and is used to read JD PDFs and count pages.

## 4. Known issues / TODO (important)
1. **Shashwat's seed template contains placeholder or unverified content, written by the agent and NOT confirmed by Shashwat.** This includes: phone `+91 9999999999`, "IIIT Allahabad B.Tech IT 2020–2024", "1,000+ downloads", "35% latency reduction", "JEE Advanced", "500+ problems", and the AudioSync bullets. **Replace it with Shashwat's real resume before using it.** As written, it violates the project's own no-lie rule.
2. **The heuristic tailoring is hard-coded for Daisy and SCM roles.** When a JD mentions SCM/ERP/D365, it injects Daisy-specific skills and a Daisy summary, even if the active user is someone else. It needs to be generalized, e.g. skills taken from the user's own master resume, or AI-only tailoring.
3. The heuristic only rewrites the summary and skills sections. There is no bullet-level reframing without an AI key.
4. The Gemini model name (`gemini-1.5-flash`) may be outdated. `openai` is not listed in requirements.txt.
5. No guardrail check after AI tailoring. Suggested: diff the protected fields (titles, dates, employers, education) between the master and the tailored version, and block or flag any change.
6. Privacy: resumes are sent to a third-party compiler (latex.ytotech.com). Consider a self-hosted compiler or local Tectonic.
7. The ATS keyword extractor is basic (regex + frequency). Could add phrase-level/TF-IDF and synonym matching.
8. No deployment yet (Streamlit Cloud). Note that SQLite and the PDF folder don't persist reliably on Streamlit Cloud.

## 5. Related assets (Daisy's resumes, in a separate repo/folder)
- `d:\SHASHWAT\Daisy\olist-portfolio\olist-portfolio\context\resume_revised.tex`: Daisy's general APM/ATPM master
- `...\context\resume_deloitte_d365_scm.tex`: Deloitte D365 F&O SCM Analyst version
- `...\context\resume_wellsfargo_bec.tex` (+ PDF): Wells Fargo Business Execution Consultant version
- Daisy's portfolio app: https://github.com/Daizy-Mgmt/industrial-robot-capex-simulator (live: https://industrial-robot-capex-simulator-daisy-phukan.streamlit.app/)

## 6. Non-negotiable rules from the user
- **Never lie on a resume.** Don't change designations, titles, dates, CGPA (none listed for Daisy) or education. Only skills, project descriptions and the summary may be tailored.
- Keep resumes to a strict single page.
- This project lives on **ShashwatG16's** GitHub, not Daizy-Mgmt.
