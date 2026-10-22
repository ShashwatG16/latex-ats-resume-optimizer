"""
core/job_scraper.py
Job Posting URL Intelligence Engine.
Extracts Company Name, Target Role Title, Requisition ID, Location, and full Job Description
directly from a job posting URL using:
1. Direct HTTP fetch + Schema.org JSON-LD (`JobPosting`), OpenGraph meta tags, and DOM extraction.
2. Jina Reader API (`https://r.jina.ai/<url>`) fallback for JS-rendered / SPA career portals (Workday, Greenhouse, Lever, etc.).
3. Optional AI Structured Extraction (Gemini / OpenAI) to cleanly parse any raw page text into structured fields.
"""

import html
import json
import re
from typing import Dict, Optional
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup


BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def _clean_html_fragment(raw_html: str) -> str:
    """Converts HTML description (often inside JSON-LD) into clean readable plain text."""
    if not raw_html:
        return ""
    unescaped = html.unescape(raw_html)
    soup = BeautifulSoup(unescaped, "html.parser")
    for li in soup.find_all("li"):
        li.insert_before("• ")
        li.insert_after("\n")
    for br in soup.find_all(["br", "p", "div", "h1", "h2", "h3", "h4"]):
        br.insert_after("\n")
    text = soup.get_text(separator=" ")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join([line for line in lines if line])


def _extract_jsonld_job_posting(soup: BeautifulSoup) -> Dict[str, str]:
    """Looks for Schema.org JobPosting JSON-LD blocks in the page."""
    result = {
        "company": "",
        "job_title": "",
        "requisition_id": "",
        "location": "",
        "job_description": "",
    }
    scripts = soup.find_all("script", attrs={"type": re.compile(r"ld\+json", re.I)})
    for script in scripts:
        raw = script.string or script.get_text()
        if not raw:
            continue
        try:
            data = json.loads(raw.strip())
        except Exception:
            continue

        candidates = []
        if isinstance(data, list):
            candidates.extend(data)
        elif isinstance(data, dict):
            if "@graph" in data and isinstance(data["@graph"], list):
                candidates.extend(data["@graph"])
            else:
                candidates.append(data)

        for item in candidates:
            if not isinstance(item, dict):
                continue
            item_type = str(item.get("@type", ""))
            if "JobPosting" not in item_type:
                continue

            if item.get("title") and not result["job_title"]:
                result["job_title"] = html.unescape(str(item["title"])).strip()

            org = item.get("hiringOrganization")
            if isinstance(org, dict) and org.get("name") and not result["company"]:
                result["company"] = html.unescape(str(org["name"])).strip()
            elif isinstance(org, str) and not result["company"]:
                result["company"] = org.strip()

            ident = item.get("identifier")
            if isinstance(ident, dict) and ident.get("value"):
                result["requisition_id"] = str(ident["value"]).strip()
            elif isinstance(ident, (str, int)):
                result["requisition_id"] = str(ident).strip()
            elif item.get("reqId"):
                result["requisition_id"] = str(item["reqId"]).strip()

            # Location parsing
            loc = item.get("jobLocation")
            loc_parts = []
            if isinstance(loc, list) and loc:
                loc = loc[0]
            if isinstance(loc, dict):
                addr = loc.get("address")
                if isinstance(addr, dict):
                    for k in ("addressLocality", "addressRegion", "addressCountry"):
                        val = addr.get(k)
                        if isinstance(val, dict):
                            val = val.get("name")
                        if val and str(val).strip():
                            loc_parts.append(str(val).strip())
                elif isinstance(addr, str):
                    loc_parts.append(addr.strip())
            if loc_parts and not result["location"]:
                result["location"] = ", ".join(dict.fromkeys(loc_parts))

            # Description parsing
            desc_parts = []
            for field in ("description", "responsibilities", "qualifications", "skills", "experienceRequirements"):
                val = item.get(field)
                if val and isinstance(val, str):
                    desc_parts.append(_clean_html_fragment(val))
            if desc_parts and not result["job_description"]:
                result["job_description"] = "\n\n".join(desc_parts)

    return result


def _guess_company_from_url(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower()
        host = re.sub(r"^www\.", "", host)
        # Handle workday e.g. deloitte.wd1.myworkdayjobs.com
        if "myworkdayjobs.com" in host:
            return host.split(".")[0].capitalize()
        parts = host.split(".")
        if parts[0] in ("jobs", "careers", "apply", "boards", "job-boards") and len(parts) > 1:
            if parts[1] not in ("greenhouse", "lever", "ashbyhq", "smartrecruiters", "workable"):
                return parts[1].capitalize()
        if parts[0] not in ("greenhouse", "lever", "linkedin", "indeed", "naukri", "glassdoor", "wellfound"):
            return parts[0].capitalize()
    except Exception:
        pass
    return ""


def _guess_req_id(url: str, text: str) -> str:
    # Check URL patterns first (e.g., JR108410, R-12345, /jobs/123456)
    url_match = re.search(r"\b((?:JR|REQ|R|JOB)[-_]?\d{4,10}|\d{5,10})\b", url, re.I)
    if url_match:
        return url_match.group(1)
    text_match = re.search(
        r"(?:Requisition\s*(?:ID|Number|#)?|Job\s*(?:ID|Number|Code|#)|Req\s*(?:ID|#))\s*[:\-]?\s*([A-Z0-9\-_]{3,20})",
        text,
        re.I,
    )
    if text_match:
        return text_match.group(1).strip()
    return ""


def _fetch_via_jina_reader(url: str, timeout: int = 20) -> str:
    """Uses r.jina.ai reader to render JS-heavy career pages into clean markdown."""
    try:
        jina_url = f"https://r.jina.ai/{url}"
        resp = requests.get(
            jina_url,
            headers={"User-Agent": BROWSER_HEADERS["User-Agent"], "X-Return-Format": "markdown"},
            timeout=timeout,
        )
        if resp.status_code == 200 and len(resp.text.strip()) > 120:
            return resp.text.strip()
    except Exception:
        pass
    return ""


def _refine_with_ai(
    raw_text: str,
    url: str,
    current_data: Dict[str, str],
    api_key: str,
    provider: str = "gemini",
    model_name: str = "",
) -> Dict[str, str]:
    """Uses Gemini or OpenAI to extract clean structured job metadata & full JD from raw scraped page text."""
    system_prompt = """You are an expert Job Posting Parser.
Given the URL and raw extracted text from a job posting webpage, extract the exact details into a valid JSON object with these keys:
- "company": The hiring company name (string)
- "job_title": The exact role/job title (string)
- "requisition_id": The job ID / requisition code if mentioned, else "" (string)
- "location": The job location (e.g. "Bengaluru, India" or "Remote"), else "" (string)
- "job_description": The complete, clean job description including summary, responsibilities, requirements, qualifications, and skills. Do NOT truncate important requirements or skills (string).

Return ONLY a valid JSON object without markdown fences."""

    user_prompt = f"""Job URL: {url}
Preliminary parsed metadata: {json.dumps({k: v for k, v in current_data.items() if k != 'job_description'})}

Raw Webpage Content:
{raw_text[:22000]}"""

    try:
        raw_json_str = ""
        if provider == "gemini":
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=api_key)
            fallback_order = [
                model_name or "gemini-3.6-flash",
                "gemini-3.6-flash",
                "gemini-3.5-flash",
                "gemini-3.5-flash-lite",
                "gemini-flash-lite-latest",
                "gemini-3-flash-preview",
            ]
            seen = []
            for m in fallback_order:
                if m and m not in seen:
                    seen.append(m)
            for m_name in seen:
                try:
                    resp = client.models.generate_content(
                        model=m_name,
                        contents=user_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            temperature=0.1,
                        ),
                    )
                    raw_json_str = (resp.text or "").strip()
                    if raw_json_str:
                        break
                except Exception:
                    continue
        elif provider == "openai":
            import openai
            client = openai.OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model=model_name or "gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
            )
            raw_json_str = (resp.choices[0].message.content or "").strip()

        if raw_json_str:
            json_match = re.search(r"(\{.*\})", raw_json_str, flags=re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(1))
                for k in ("company", "job_title", "requisition_id", "location", "job_description"):
                    val = parsed.get(k)
                    if isinstance(val, str) and val.strip():
                        current_data[k] = val.strip()
    except Exception:
        pass

    return current_data


def extract_job_from_url(
    url: str,
    api_key: str = "",
    provider: str = "gemini",
    model_name: str = "",
) -> Dict[str, str]:
    """
    Fetches a job posting URL and returns a dictionary:
    {
        "success": True/False,
        "company": str,
        "job_title": str,
        "requisition_id": str,
        "location": str,
        "job_description": str,
        "job_url": str,
        "error": str (if any)
    }
    """
    clean_url = (url or "").strip()
    if not clean_url:
        return {"success": False, "error": "Please enter a valid Job Posting URL."}
    if not clean_url.startswith(("http://", "https://")):
        clean_url = "https://" + clean_url

    extracted = {
        "success": False,
        "company": "",
        "job_title": "",
        "requisition_id": "",
        "location": "",
        "job_description": "",
        "job_url": clean_url,
        "error": "",
    }

    page_text = ""
    soup = None

    # Step 1: Direct HTTP request + BeautifulSoup + JSON-LD JobPosting
    try:
        resp = requests.get(clean_url, headers=BROWSER_HEADERS, timeout=15, allow_redirects=True)
        if resp.status_code == 200 and resp.text:
            soup = BeautifulSoup(resp.text, "html.parser")
            jsonld_data = _extract_jsonld_job_posting(soup)
            for k, v in jsonld_data.items():
                if v:
                    extracted[k] = v

            # OpenGraph & Meta tags fallback
            og_title = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "twitter:title"})
            og_site = soup.find("meta", property="og:site_name")
            title_tag = soup.title.string.strip() if (soup.title and soup.title.string) else ""
            raw_title = (og_title.get("content", "").strip() if og_title else "") or title_tag

            if og_site and og_site.get("content") and not extracted["company"]:
                extracted["company"] = og_site["content"].strip()

            if raw_title and not extracted["job_title"]:
                # Often formatted as "Role Title - Company Name" or "Role Title | Company"
                parts = re.split(r"\s+(?:\||—|–|-|at)\s+", raw_title)
                if parts:
                    extracted["job_title"] = parts[0].strip()
                    if len(parts) > 1 and not extracted["company"]:
                        extracted["company"] = parts[-1].replace("Careers", "").replace("Jobs", "").strip()

            # Remove noisy tags before body text extraction
            for tag in soup(["script", "style", "noscript", "svg", "footer", "nav", "header"]):
                tag.decompose()
            page_text = _clean_html_fragment(str(soup.body or soup))
    except Exception:
        pass

    # Step 2: If direct fetch yielded very little text (e.g. Workday/SPA shell or anti-bot), use Jina Reader
    if len(extracted["job_description"]) < 250 and len(page_text) < 400:
        jina_md = _fetch_via_jina_reader(clean_url)
        if jina_md:
            page_text = jina_md
            # Parse Jina Title line if present
            title_m = re.search(r"^Title:\s*(.+)$", jina_md, re.M)
            if title_m and not extracted["job_title"]:
                raw_t = title_m.group(1).strip()
                parts = re.split(r"\s+(?:\||—|–|-|at)\s+", raw_t)
                extracted["job_title"] = parts[0].strip()
                if len(parts) > 1 and not extracted["company"]:
                    extracted["company"] = parts[-1].replace("Careers", "").replace("Jobs", "").strip()

    # Step 3: Populate fallback company / req_id / description from heuristics
    if not extracted["company"]:
        extracted["company"] = _guess_company_from_url(clean_url)

    combined_text = extracted["job_description"] or page_text
    if not extracted["requisition_id"] and combined_text:
        extracted["requisition_id"] = _guess_req_id(clean_url, combined_text)

    if not extracted["job_description"] and page_text:
        extracted["job_description"] = page_text[:15000].strip()

    # Step 4: If AI key is available, refine & structure the fields cleanly
    raw_for_ai = page_text if len(page_text) > len(extracted["job_description"]) else extracted["job_description"]
    if api_key and raw_for_ai and len(raw_for_ai) > 100:
        extracted = _refine_with_ai(
            raw_text=raw_for_ai,
            url=clean_url,
            current_data=extracted,
            api_key=api_key,
            provider=provider,
            model_name=model_name,
        )

    if extracted["job_description"] or extracted["job_title"]:
        extracted["success"] = True
    else:
        extracted["error"] = (
            "Could not automatically read job details from this URL (the site may require login or block automated access). "
            "Please paste the Job Description text below."
        )

    return extracted
