"""
core/guardrails.py
Hard Programmatic Zero-Fabrication Guardrail & Slot-Based LaTeX Protector.

Instead of allowing the LLM to freely rewrite the entire LaTeX document (where it can
accidentally or intentionally alter job titles, company names, dates, headline, education,
or honors), this module:
1. Masks every immutable factual structure in the Master LaTeX with numbered tokens
   (__IMMUTABLE_HEADER_BLOCK__, __IMMUTABLE_SUBHEADING_0__, __IMMUTABLE_PROJECT_0__,
   __IMMUTABLE_EDUCATION_SECTION__, __IMMUTABLE_HONORS_SECTION__) BEFORE sending to the AI.
2. Restores those exact tokens verbatim from the Master LaTeX AFTER the AI responds.
3. Even if the AI ignores tokens and outputs raw LaTeX macros, `enforce_factual_guardrails`
   parses and overwrites every header, `\resumeSubheading`, `\resumeProjectHeading`,
   Education section, and Honors section with the exact strings from `master_latex`.
"""

import re
from typing import Dict, List, Tuple


def find_balanced_macro_calls(text: str, macro_name: str, num_args: int) -> List[Tuple[int, int, List[str], str]]:
    """
    Finds all occurrences of \\macro_name{arg1}{arg2}...{argN} in `text` using balanced brace parsing.
    Returns list of tuples: (start_idx, end_idx, [arg1, ..., argN], raw_full_match).
    """
    results = []
    pattern = re.compile(r"\\" + re.escape(macro_name) + r"\b")
    for m in pattern.finditer(text):
        start_idx = m.start()
        idx = m.end()
        args = []
        valid = True
        for _ in range(num_args):
            while idx < len(text) and text[idx].isspace():
                idx += 1
            if idx >= len(text) or text[idx] != "{":
                valid = False
                break
            depth = 0
            arg_start = idx + 1
            while idx < len(text):
                if text[idx] == "{" and (idx == 0 or text[idx - 1] != "\\"):
                    depth += 1
                elif text[idx] == "}" and (idx == 0 or text[idx - 1] != "\\"):
                    depth -= 1
                    if depth == 0:
                        args.append(text[arg_start:idx])
                        idx += 1
                        break
                idx += 1
            else:
                valid = False
                break
        if valid and len(args) == num_args:
            results.append((start_idx, idx, args, text[start_idx:idx]))
    return results


def mask_immutable_facts_for_ai(master_latex: str) -> Tuple[str, Dict[str, str]]:
    """
    Replaces immutable factual blocks in `master_latex` with read-only placeholder tokens
    so the LLM physically cannot see or rewrite job titles, employers, dates, education, or honors.
    """
    token_map: Dict[str, str] = {}
    masked = master_latex

    # 1. Lock Education section completely
    edu_pattern = re.compile(
        r"(%-----------EDUCATION-----------\s*\\section\{Education\}.*?|\s*\\section\{Education\}.*?)(?=%-----------|\s*\\section\{|\\end\{document\})",
        flags=re.DOTALL | re.IGNORECASE,
    )
    m_edu = edu_pattern.search(masked)
    if m_edu:
        tok = "% __IMMUTABLE_EDUCATION_SECTION__"
        token_map[tok] = m_edu.group(1)
        masked = masked[: m_edu.start(1)] + tok + "\n" + masked[m_edu.end(1) :]

    # 2. Lock Leadership / Honors / Achievements section completely
    hon_pattern = re.compile(
        r"(%-----------(?:LEADERSHIP|HONORS).*?\\section\{(?:Leadership|Honors).*?|\s*\\section\{(?:Leadership|Honors).*?)(?=\\end\{document\})",
        flags=re.DOTALL | re.IGNORECASE,
    )
    m_hon = hon_pattern.search(masked)
    if m_hon:
        tok = "% __IMMUTABLE_HONORS_SECTION__"
        token_map[tok] = m_hon.group(1)
        masked = masked[: m_hon.start(1)] + tok + "\n" + masked[m_hon.end(1) :]

    # 3. Lock Preamble + Top Candidate Heading block (everything from start of file up to first \section)
    header_m = re.search(r"^(\s*.*?\\begin\{document\}.*?)(?=%-----------SUMMARY|\\section\{)", masked, flags=re.DOTALL)
    if header_m:
        tok = "% __IMMUTABLE_PREAMBLE_AND_HEADER__"
        token_map[tok] = header_m.group(1)
        masked = tok + "\n" + masked[header_m.end(1) :]

    # 4. Lock every \resumeSubheading{Company}{Dates}{Actual Role Title}{Location}
    subs = find_balanced_macro_calls(masked, "resumeSubheading", 4)
    for idx in range(len(subs) - 1, -1, -1):
        s_start, s_end, args, raw_call = subs[idx]
        # Provide context comment so AI knows which experience block this is without being able to edit the macro
        tok = f"% __IMMUTABLE_SUBHEADING_{idx}__ [LOCKED ROLE: {args[2].strip()} @ {args[0].strip()} ({args[1].strip()})]"
        token_map[f"__IMMUTABLE_SUBHEADING_{idx}__"] = raw_call
        masked = masked[:s_start] + tok + masked[s_end:]

    # 5. Lock every \resumeProjectHeading{Project Title}{Tech Stack}{Links/Year}
    projs = find_balanced_macro_calls(masked, "resumeProjectHeading", 3)
    for idx in range(len(projs) - 1, -1, -1):
        p_start, p_end, args, raw_call = projs[idx]
        tok = f"% __IMMUTABLE_PROJECT_HEADING_{idx}__ [LOCKED PROJECT: {args[0].strip()}]"
        token_map[f"__IMMUTABLE_PROJECT_HEADING_{idx}__"] = raw_call
        masked = masked[:p_start] + tok + masked[p_end:]

    return masked, token_map


def restore_immutable_tokens(ai_output: str, token_map: Dict[str, str]) -> str:
    """Restores all placeholder tokens back to their exact master LaTeX strings."""
    restored = ai_output

    # Restore indexed subheadings and project headings even if AI stripped the comment text after the token
    for key, original_val in token_map.items():
        if key.startswith("__IMMUTABLE_SUBHEADING_") or key.startswith("__IMMUTABLE_PROJECT_HEADING_"):
            line_pattern = re.compile(r"%?\s*" + re.escape(key) + r"[^\n]*")
            if line_pattern.search(restored):
                restored = line_pattern.sub(lambda _: original_val, restored)
        else:
            core_token = key.replace("% ", "").strip()
            line_pattern = re.compile(r"%?\s*" + re.escape(core_token) + r"[^\n]*")
            if line_pattern.search(restored):
                restored = line_pattern.sub(lambda _: original_val, restored)

    return restored


def enforce_factual_guardrails(master_latex: str, tailored_latex: str) -> Tuple[str, List[str]]:
    """
    Post-processing AST/Macro structural lock.
    Even if the AI bypassed tokens and wrote raw LaTeX, this function forces:
    1. Top Preamble & Candidate Header / Headline (before first \\section) to match `master_latex` 100%.
    2. Every \\resumeSubheading{Employer}{Dates}{Job Title}{Location} to match `master_latex` 100%.
    3. Every \\resumeProjectHeading{Project Name}{Tech}{Links} to match `master_latex` 100%.
    4. Education and Honors/Leadership sections to match `master_latex` 100%.
    """
    restored_notices: List[str] = []
    safe_tex = tailored_latex

    # 1. Force Preamble + Top Candidate Heading block (everything up to first \section)
    master_header_m = re.search(r"^(\s*.*?\\begin\{document\}.*?)(?=%-----------SUMMARY|\\section\{)", master_latex, flags=re.DOTALL)
    tailored_header_m = re.search(r"^(\s*.*?\\begin\{document\}.*?)(?=%-----------SUMMARY|\\section\{)", safe_tex, flags=re.DOTALL)
    if master_header_m and tailored_header_m:
        if master_header_m.group(1).strip() != tailored_header_m.group(1).strip():
            safe_tex = master_header_m.group(1) + safe_tex[tailored_header_m.end(1) :]
            restored_notices.append("Locked candidate name, headline designation & contact header")
    elif master_header_m and "\\begin{document}" not in safe_tex:
        safe_tex = master_header_m.group(1) + "\n" + safe_tex
        restored_notices.append("Restored missing preamble & candidate header")

    # 2. Force Education section verbatim
    edu_pattern = re.compile(
        r"(\\section\{Education\}.*?)(?=%-----------|\s*\\section\{|\\end\{document\})",
        flags=re.DOTALL | re.IGNORECASE,
    )
    m_edu = edu_pattern.search(master_latex)
    t_edu = edu_pattern.search(safe_tex)
    if m_edu and t_edu:
        if m_edu.group(1).strip() != t_edu.group(1).strip():
            safe_tex = safe_tex[: t_edu.start(1)] + m_edu.group(1) + safe_tex[t_edu.end(1) :]
            restored_notices.append("Locked Education section verbatim")
    elif m_edu and not t_edu and "\\end{document}" in safe_tex:
        safe_tex = safe_tex.replace("\\end{document}", m_edu.group(1) + "\n\\end{document}")
        restored_notices.append("Restored Education section")

    # 3. Force Leadership / Honors / Achievements section verbatim
    honors_pattern = re.compile(
        r"(\\section\{(?:Leadership|Honors).*?)(?=\\end\{document\})",
        flags=re.DOTALL | re.IGNORECASE,
    )
    m_hon = honors_pattern.search(master_latex)
    t_hon = honors_pattern.search(safe_tex)
    if m_hon and t_hon:
        if m_hon.group(1).strip() != t_hon.group(1).strip():
            safe_tex = safe_tex[: t_hon.start(1)] + m_hon.group(1) + safe_tex[t_hon.end(1) :]
            restored_notices.append("Locked Honors & Leadership section verbatim")
    elif m_hon and not t_hon and "\\end{document}" in safe_tex:
        safe_tex = safe_tex.replace("\\end{document}", m_hon.group(1) + "\n\\end{document}")
        restored_notices.append("Restored Honors & Leadership section")

    # 4. Force every \resumeSubheading{Company/Uni}{Dates}{Actual Role/Degree}{Location}
    master_subs = find_balanced_macro_calls(master_latex, "resumeSubheading", 4)
    tailored_subs = find_balanced_macro_calls(safe_tex, "resumeSubheading", 4)
    if master_subs and tailored_subs:
        count = min(len(master_subs), len(tailored_subs))
        for idx in range(count - 1, -1, -1):
            _, _, m_args, m_raw = master_subs[idx]
            t_start, t_end, t_args, _ = tailored_subs[idx]
            if [a.strip() for a in m_args] != [a.strip() for a in t_args]:
                safe_tex = safe_tex[:t_start] + m_raw + safe_tex[t_end:]
                restored_notices.append(f"Locked actual role title '{m_args[2].strip()}' at '{m_args[0].strip()}'")

    # 5. Force every \resumeProjectHeading{Project Title}{Tech Stack}{Links/Year}
    master_projs = find_balanced_macro_calls(master_latex, "resumeProjectHeading", 3)
    tailored_projs = find_balanced_macro_calls(safe_tex, "resumeProjectHeading", 3)
    if master_projs and tailored_projs:
        count = min(len(master_projs), len(tailored_projs))
        for idx in range(count - 1, -1, -1):
            _, _, m_args, m_raw = master_projs[idx]
            t_start, t_end, t_args, _ = tailored_projs[idx]
            if [a.strip() for a in m_args] != [a.strip() for a in t_args]:
                safe_tex = safe_tex[:t_start] + m_raw + safe_tex[t_end:]
                restored_notices.append(f"Locked project heading '{m_args[0].strip()}'")

    return safe_tex, restored_notices
