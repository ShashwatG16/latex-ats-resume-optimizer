"""
server.py
FastAPI + Modern Web UI (Vue.js 3 SPA) for JobTailor-AI.
Provides full REST API + native PDF Blob/Image endpoints + Overleaf-style IDE interface.
"""

import base64
import io
import json
import os
from typing import Optional
from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pypdf import PdfReader
from dotenv import load_dotenv

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
from core.compiler import compile_latex_to_pdf
from core.ats_engine import evaluate_ats_match, tailor_resume_heuristically, tailor_resume_with_ai

# Initialize DB on startup
init_db(default_daisy_tex=DEFAULT_DAISY_TEX, default_shashwat_tex=DEFAULT_SHASHWAT_TEX)

app = FastAPI(title="JobTailor-AI Studio API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateUserRequest(BaseModel):
    name: str
    email: Optional[str] = ""
    phone: Optional[str] = ""
    headline: Optional[str] = ""
    master_latex: Optional[str] = ""


class UpdateMasterRequest(BaseModel):
    master_latex: str
    headline: Optional[str] = None


class TailorRequest(BaseModel):
    user_id: int
    master_latex: Optional[str] = None
    jd_text: str
    company: Optional[str] = ""
    job_title: Optional[str] = ""
    provider: str = "gemini"  # "heuristic", "gemini", "openai"
    model_name: Optional[str] = "gemini-2.5-flash"
    api_key: Optional[str] = ""
    compile_pdf: bool = True


class CompileRequest(BaseModel):
    tex_code: str


class SaveAppRequest(BaseModel):
    user_id: int
    company: str
    job_title: str
    requisition_id: Optional[str] = ""
    location: Optional[str] = ""
    job_url: Optional[str] = ""
    job_description: str
    ats_score: float = 0.0
    matched_keywords: list = []
    missing_keywords: list = []
    tailored_latex: str
    pdf_base64: Optional[str] = None
    status: str = "Applied"
    notes: Optional[str] = ""


class UpdateAppStatusRequest(BaseModel):
    status: str
    notes: Optional[str] = None


class SaveKeyRequest(BaseModel):
    provider: str
    api_key: str


def render_pdf_to_png_b64_list(pdf_bytes: bytes):
    """Converts PDF bytes into high-DPI PNG base64 strings and page count."""
    pages_b64 = []
    page_count = 1
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        page_count = len(reader.pages)
    except Exception:
        pass

    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page_count = len(doc)
        for i in range(len(doc)):
            pix = doc.load_page(i).get_pixmap(dpi=180)
            pages_b64.append(base64.b64encode(pix.tobytes("png")).decode("utf-8"))
        doc.close()
    except Exception:
        pass
    return pages_b64, page_count


@app.get("/api/config")
def get_config():
    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
    openai_key = os.environ.get("OPENAI_API_KEY") or ""
    return {
        "has_gemini_key": bool(gemini_key),
        "has_openai_key": bool(openai_key),
        "default_provider": "gemini" if gemini_key else ("openai" if openai_key else "heuristic"),
        "gemini_models": ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash", "gemini-1.5-flash"],
        "openai_models": ["gpt-4o", "gpt-4o-mini"],
    }


@app.post("/api/config/key")
def save_api_key(req: SaveKeyRequest):
    key_name = "GEMINI_API_KEY" if req.provider == "gemini" else "OPENAI_API_KEY"
    val = req.api_key.strip()
    if not val:
        raise HTTPException(status_code=400, detail="API key cannot be empty")
    lines = []
    if os.path.exists(ENV_FILE_PATH):
        with open(ENV_FILE_PATH, "r", encoding="utf-8") as f:
            lines = [line for line in f.readlines() if not line.strip().startswith(f"{key_name}=")]
    lines.append(f"{key_name}={val}\n")
    with open(ENV_FILE_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)
    os.environ[key_name] = val
    return {"status": "ok", "key_name": key_name}


@app.get("/api/users")
def api_get_users():
    return get_all_users()


@app.post("/api/users")
def api_create_user(req: CreateUserRequest):
    if not req.name.strip():
        raise HTTPException(status_code=400, detail="Name is required")
    tex = req.master_latex.strip() if req.master_latex and req.master_latex.strip() else DEFAULT_SHASHWAT_TEX
    uid = create_user(req.name.strip(), req.email or "", req.phone or "", req.headline or "", tex)
    return get_user_by_id(uid)


@app.put("/api/users/{user_id}/master")
def api_update_master(user_id: int, req: UpdateMasterRequest):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    update_user_master_latex(user_id, req.master_latex, req.headline)
    return get_user_by_id(user_id)


@app.post("/api/extract-jd")
async def api_extract_jd(file: UploadFile = File(...)):
    content = await file.read()
    filename = (file.filename or "").lower()
    if filename.endswith(".pdf"):
        try:
            reader = PdfReader(io.BytesIO(content))
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
            return {"text": text.strip(), "filename": file.filename}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read PDF: {e}")
    else:
        text = content.decode("utf-8", errors="ignore")
        return {"text": text.strip(), "filename": file.filename}


@app.post("/api/compile")
def api_compile_latex(req: CompileRequest):
    if not req.tex_code.strip():
        raise HTTPException(status_code=400, detail="LaTeX code is empty")
    pdf_bytes, msg = compile_latex_to_pdf(req.tex_code)
    if not pdf_bytes:
        return {"success": False, "error": msg}
    pages_png, page_count = render_pdf_to_png_b64_list(pdf_bytes)
    return {
        "success": True,
        "message": msg,
        "pdf_base64": base64.b64encode(pdf_bytes).decode("utf-8"),
        "pages_png": pages_png,
        "page_count": page_count,
    }


@app.post("/api/tailor")
def api_tailor_resume(req: TailorRequest):
    user = get_user_by_id(req.user_id)
    if not user and not req.master_latex:
        raise HTTPException(status_code=404, detail="User not found")
    base_latex = req.master_latex if req.master_latex else user["master_latex"]

    if not req.jd_text.strip():
        raise HTTPException(status_code=400, detail="Job Description is required")

    provider = req.provider.lower()
    effective_key = (req.api_key or "").strip()
    if not effective_key:
        if provider == "gemini":
            effective_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
        elif provider == "openai":
            effective_key = os.environ.get("OPENAI_API_KEY") or ""

    if provider in ("gemini", "openai") and effective_key:
        tailored_tex, stats = tailor_resume_with_ai(
            master_latex=base_latex,
            jd_text=req.jd_text,
            target_company=req.company or "",
            target_role=req.job_title or "",
            api_key=effective_key,
            provider=provider,
            model_name=req.model_name or "",
        )
    else:
        tailored_tex, stats = tailor_resume_heuristically(
            master_latex=base_latex,
            jd_text=req.jd_text,
            target_company=req.company or "",
            target_role=req.job_title or "",
        )
        if provider in ("gemini", "openai") and not effective_key:
            stats["ai_error"] = f"No API key configured for {provider.upper()}. Used Heuristic Engine instead."

    result = {
        "tailored_latex": tailored_tex,
        "stats": stats,
        "pdf_base64": None,
        "pages_png": [],
        "page_count": 1,
        "compile_error": None,
    }

    if req.compile_pdf:
        pdf_bytes, err_msg = compile_latex_to_pdf(tailored_tex)
        if pdf_bytes:
            pages_png, page_count = render_pdf_to_png_b64_list(pdf_bytes)
            result["pdf_base64"] = base64.b64encode(pdf_bytes).decode("utf-8")
            result["pages_png"] = pages_png
            result["page_count"] = page_count
        else:
            result["compile_error"] = err_msg

    return result


@app.post("/api/evaluate-ats")
def api_evaluate_ats(req: TailorRequest):
    eval_res = evaluate_ats_match(req.jd_text, req.master_latex or "")
    return eval_res


@app.get("/api/users/{user_id}/applications")
def api_get_applications(user_id: int):
    apps = get_applications_for_user(user_id)
    for a in apps:
        try:
            a["matched_keywords_list"] = json.loads(a.get("matched_keywords") or "[]")
        except Exception:
            a["matched_keywords_list"] = []
        try:
            a["missing_keywords_list"] = json.loads(a.get("missing_keywords") or "[]")
        except Exception:
            a["missing_keywords_list"] = []
    return apps


@app.post("/api/applications")
def api_save_application(req: SaveAppRequest):
    pdf_bytes = None
    if req.pdf_base64:
        try:
            pdf_bytes = base64.b64decode(req.pdf_base64)
        except Exception:
            pdf_bytes = None

    app_id = save_application(
        user_id=req.user_id,
        company=req.company,
        job_title=req.job_title,
        requisition_id=req.requisition_id or "",
        location=req.location or "",
        job_url=req.job_url or "",
        job_description=req.job_description,
        ats_score=req.ats_score,
        matched_keywords=json.dumps(req.matched_keywords),
        missing_keywords=json.dumps(req.missing_keywords),
        tailored_latex=req.tailored_latex,
        pdf_bytes=pdf_bytes,
        status=req.status or "Applied",
        notes=req.notes or f"Tailored for {req.company}",
    )
    return get_application_by_id(app_id)


@app.patch("/api/applications/{app_id}")
def api_update_app_status(app_id: int, req: UpdateAppStatusRequest):
    update_application_status(app_id, req.status, req.notes)
    return get_application_by_id(app_id)


@app.delete("/api/applications/{app_id}")
def api_delete_app(app_id: int):
    delete_application(app_id)
    return {"status": "deleted", "id": app_id}


@app.get("/api/applications/{app_id}/pdf")
def api_download_app_pdf(app_id: int):
    app_row = get_application_by_id(app_id)
    if not app_row or not app_row.get("pdf_filename"):
        raise HTTPException(status_code=404, detail="PDF not found")
    pdf_path = os.path.join(PDF_DIR, app_row["pdf_filename"])
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file missing on disk")
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"{app_row['company']}_{app_row['job_title']}_Resume.pdf",
    )


FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
os.makedirs(FRONTEND_DIR, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
def serve_spa():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Frontend not found</h1>", status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
