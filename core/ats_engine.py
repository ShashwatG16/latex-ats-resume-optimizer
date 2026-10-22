"""
core/ats_engine.py
ATS keyword extraction, semantic matching, and strict no-fabrication LaTeX tailoring engine.
"""

import re
import json
from collections import Counter
from typing import Dict, List, Tuple, Set


COMMON_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing",
    "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself",
    "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is",
    "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should",
    "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've",
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
    "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where",
    "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves",
    "will", "shall", "may", "might", "must", "experience", "role", "team", "work", "responsibilities",
    "qualifications", "preferred", "minimum", "job", "candidate", "skills", "ability", "working"
}

HIGH_VALUE_PATTERNS = [
    r"\b(?:d365|dynamics 365)\b",
    r"\bf&o\b",
    r"\bfunctional scm\b",
    r"\bsupply chain management\b",
    r"\brequirement gathering(?: workshops)?\b",
    r"\bfunctional design document(?:s)?\b",
    r"\bfdd\b",
    r"\bunit testing\b",
    r"\bsystem integration testing\b",
    r"\bsit\b",
    r"\buser acceptance testing\b",
    r"\buat\b",
    r"\bdata migration\b",
    r"\bmaster data(?: setup)?\b",
    r"\bpost-go-live(?: support)?\b",
    r"\bhypercare\b",
    r"\buser training\b",
    r"\bmechanical engineering\b",
    r"\bindustrial engineering\b",
    r"\boperations research\b",
    r"\berp solutions?\b",
    r"\benterprise technology\b",
    r"\bagile / scrum\b",
    r"\bjira\b",
    r"\bconfluence\b",
    r"\bpower bi\b",
    r"\bpostgresql\b",
    r"\bstar schema\b",
    r"\bpython\b",
    r"\bpandas\b",
    r"\bnumpy\b",
    r"\bplotly\b",
    r"\bstreamlit\b",
    r"\bc\+\+\b",
    r"\bdocker\b",
    r"\brest(?:ful)? apis?\b",
    r"\bci/cd\b",
    r"\bdistributed systems\b",
    r"\btrade & logistics\b",
    r"\bprocess mapping\b",
    r"\bas-is / to-be\b",
    r"\bdefect triage\b",
    r"\bunit economics\b",
    r"\bcapex vs\.? opex\b",
    r"\bdcf modeling\b",
]


def extract_keywords_from_text(text: str) -> List[str]:
    text_lower = text.lower()
    found_phrases = []

    for pat in HIGH_VALUE_PATTERNS:
        matches = re.findall(pat, text_lower)
        if matches:
            found_phrases.extend(list(set(matches)))

    words = re.findall(r"\b[a-zA-Z0-9_\-\+\#]{2,}\b", text_lower)
    filtered = [w for w in words if w not in COMMON_STOPWORDS and not w.isdigit()]
    counts = Counter(filtered)
    top_words = [w for w, c in counts.most_common(40)]
    
    return list(dict.fromkeys(found_phrases + top_words))


def evaluate_ats_match(jd_text: str, resume_latex: str) -> Dict:
    jd_keywords = extract_keywords_from_text(jd_text)
    latex_lower = resume_latex.lower()

    matched = []
    missing = []

    for kw in jd_keywords:
        pattern = r"\b" + re.escape(kw) + r"\b"
        if re.search(pattern, latex_lower):
            matched.append(kw)
        else:
            missing.append(kw)

    total = len(jd_keywords)
    match_pct = round((len(matched) / total * 100.0), 1) if total > 0 else 0.0

    return {
        "match_percentage": match_pct,
        "matched_count": len(matched),
        "total_keywords": total,
        "matched_keywords": matched,
        "missing_keywords": missing,
    }


def tailor_resume_heuristically(
    master_latex: str,
    jd_text: str,
    target_company: str,
    target_role: str,
) -> Tuple[str, Dict]:
    ats_before = evaluate_ats_match(jd_text, master_latex)
    tailored = master_latex

    is_scm_erp = bool(re.search(r"\b(scm|supply chain|erp|d365|dynamics 365|f&o|fdd)\b", jd_text, re.I))

    if is_scm_erp:
        new_skills = r"""\section{Core Skills \& Technical Competencies}
  \begin{itemize}[leftmargin=0.0in, label={}, itemsep=1.2pt]
    \footnotesize{\item{\textbf{SCM \& Functional Lifecycle: } Supply Chain Management (SCM) Processes $\cdot$ Requirement Gathering Workshops $\cdot$ Functional Design Documents (FDD/TRD) $\cdot$ As-Is / To-Be Process Mapping $\cdot$ Business Process Execution $\cdot$ Post-Go-Live Support $\cdot$ D365 F\&O SCM Concepts}}
    \footnotesize{\item{\textbf{Testing, Quality \& User Enablement: } Unit Testing $\cdot$ System Integration Testing (SIT) $\cdot$ User Acceptance Testing (UAT) $\cdot$ Test Case Design \& Defect Triage (Jira) $\cdot$ End-User Training Documentation $\cdot$ Agile / Scrum Delivery $\cdot$ Cross-Border Sprint Coordination}}
    \footnotesize{\item{\textbf{Data Migration \& Master Data: } Master Data Setup \& Governance $\cdot$ Data Migration Protocols $\cdot$ Entity Mapping \& Validation $\cdot$ Data Cleansing \& Validation $\cdot$ PostgreSQL Relational Schema $\cdot$ Enterprise Platforms (HubSpot CRM, Jira, Confluence)}}
    \footnotesize{\item{\textbf{Analytics, Operations \& Tools: } SCM Lead-Time \& Inventory Modeling $\cdot$ Logistics Delivery SLA Analytics $\cdot$ CapEx vs. OpEx Decision Modeling $\cdot$ Python (pandas, NumPy) $\cdot$ Power BI Dashboards $\cdot$ Advanced Excel (VLOOKUP, Pivot Tables, What-If Analysis)}}
  \end{itemize}"""
        tailored = re.sub(
            r"\\section\{Core Skills.*?\\begin\{itemize\}.*?\\end\{itemize\}",
            lambda m: new_skills,
            tailored,
            flags=re.DOTALL,
        )

        if target_company and target_role:
            new_summary = f"""\\section{{Professional Summary}}
 \\begin{{itemize}}[leftmargin=0.0in, label={{}}]
    \\footnotesize{{\\item{{
    \\textbf{{B.Tech Mechanical Engineer}} (AICTE Pragati Scholar, Bengaluru) and foundational technical operations member at \\textbf{{Agile Robots SE}} (Munich Physical AI unicorn). Hands-on experience in enterprise platform deployment, \\textbf{{requirement gathering workshops}}, functional specifications (\\textbf{{FDD/TRD}}), and testing execution (\\textbf{{Unit Testing, SIT, UAT}}). Proven proficiency in supply chain modeling, logistics fulfillment analytics, and \\textbf{{master data setup}}; possessing foundational knowledge of \\textbf{{Microsoft Dynamics 365 Finance \\& Operations (D365 F\\&O) SCM}} concepts and targeting the {target_role} role at {target_company}.
    }}}}
 \\end{{itemize}}"""
            tailored = re.sub(
                r"\\section\{Professional Summary\}.*?\\end\{itemize\}",
                lambda m: new_summary,
                tailored,
                flags=re.DOTALL,
            )

    ats_after = evaluate_ats_match(jd_text, tailored)

    return tailored, {
        "score_before": ats_before["match_percentage"],
        "score_after": ats_after["match_percentage"],
        "matched_keywords": ats_after["matched_keywords"],
        "missing_keywords": ats_after["missing_keywords"],
    }


def tailor_resume_with_ai(
    master_latex: str,
    jd_text: str,
    target_company: str,
    target_role: str,
    api_key: str,
    provider: str = "gemini",
    model_name: str = "",
) -> Tuple[str, Dict]:
    system_prompt = """You are an expert ATS Resume Optimization Specialist.
Your job is to tailor the candidate's LaTeX resume to match the Job Description (JD) to achieve the highest possible ATS match score.

CRITICAL RULES AND STRICT GUARDRAILS (ZERO FABRICATION):
1. DO NOT change or invent degrees, universities, GPAs, or dates of education.
2. DO NOT change job titles, employer names, or employment dates.
3. DO NOT invent false certifications, patents, or awards the candidate does not have.
4. YOU CAN:
   - Reorder and reframe existing skills to prioritize the tools, methodologies, and terminology used in the JD.
   - Refine bullet points in Experience and Projects to emphasize matching domains (e.g. SCM, testing, data migration, cloud, etc.) using truthful STAR statements.
   - Tailor the Professional Summary to clearly align the candidate's genuine background with the target role and company.
   - Ensure the output is valid LaTeX that compiles cleanly on pdflatex without package errors.
   - Maintain strict 1-page geometry.

Return ONLY the raw LaTeX code, starting from \\documentclass and ending with \\end{document}. No markdown fences (```latex)."""

    user_prompt = f"""Target Company: {target_company}
Target Role: {target_role}

Job Description:
{jd_text}

Candidate's Current Master LaTeX Resume:
{master_latex}

Tailor this resume to match the JD's exact keywords and requirements while following all strict zero-fabrication rules."""

    try:
        if provider == "gemini":
            chosen_model = model_name or "gemini-3.6-flash"
            tailored_latex = ""
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=api_key)
            fallback_order = [
                "gemini-3.6-flash",
                "gemini-3.5-flash",
                "gemini-3-flash-preview",
                "gemini-3.5-flash-lite",
                "gemini-flash-lite-latest",
                "gemini-3.8-flash",
            ]
            candidate_models = [chosen_model] + [m for m in fallback_order if m != chosen_model]
            errors_by_model = []
            for m_name in candidate_models:
                try:
                    response = client.models.generate_content(
                        model=m_name,
                        contents=user_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            temperature=0.2,
                        ),
                    )
                    tailored_latex = (response.text or "").strip()
                    if tailored_latex:
                        chosen_model = m_name
                        break
                except Exception as m_err:
                    errors_by_model.append(f"{m_name}: {str(m_err)[:120]}")
                    continue
            if not tailored_latex and errors_by_model:
                raise RuntimeError(" | ".join(errors_by_model[:3]))
        else:
            import openai
            chosen_model = model_name or "gpt-4o"
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=chosen_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
            )
            tailored_latex = (response.choices[0].message.content or "").strip()

        # Strip markdown fences if model included them
        tex_match = re.search(r"(\\documentclass.*\\end\{document\})", tailored_latex, flags=re.DOTALL)
        if tex_match:
            tailored_latex = tex_match.group(1).strip()
        else:
            if tailored_latex.startswith("```latex"):
                tailored_latex = tailored_latex[8:]
            elif tailored_latex.startswith("```"):
                tailored_latex = tailored_latex[3:]
            if tailored_latex.endswith("```"):
                tailored_latex = tailored_latex[:-3]
            tailored_latex = tailored_latex.strip()

        ats_eval = evaluate_ats_match(jd_text, tailored_latex)
        ats_before = evaluate_ats_match(jd_text, master_latex)

        return tailored_latex, {
            "score_before": ats_before["match_percentage"],
            "score_after": ats_eval["match_percentage"],
            "matched_keywords": ats_eval["matched_keywords"],
            "missing_keywords": ats_eval["missing_keywords"],
            "engine_used": f"{provider.upper()} ({chosen_model})",
        }
    except Exception as e:
        tailored, stats = tailor_resume_heuristically(master_latex, jd_text, target_company, target_role)
        stats["ai_error"] = str(e)
        stats["engine_used"] = "Heuristic Fallback (AI Error)"
        return tailored, stats
