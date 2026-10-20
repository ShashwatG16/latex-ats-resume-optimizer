"""
core/compiler.py
LaTeX to PDF compilation engine with cloud API sync and local compiler fallbacks.
"""

import base64
import os
import shutil
import subprocess
import tempfile
import requests
from typing import Tuple, Optional


def compile_latex_to_pdf(tex_code: str, timeout: int = 45) -> Tuple[Optional[bytes], str]:
    """
    Compiles LaTeX source code to PDF bytes.
    Returns: (pdf_bytes_or_none, log_or_error_message)
    """
    # 1. Primary: Fast sync cloud compiler (handles full TeXLive with fontawesome5, hyperref, titlesec)
    try:
        payload = {
            "compiler": "pdflatex",
            "resources": [
                {"main": True, "content": tex_code}
            ]
        }
        resp = requests.post(
            "https://latex.ytotech.com/builds/sync",
            json=payload,
            headers={"User-Agent": "JobTailor-AI/1.0"},
            timeout=timeout
        )
        if resp.status_code in (200, 201):
            if resp.content.startswith(b"%PDF-"):
                return resp.content, "Compilation successful (via TeXLive Cloud Engine)."
            else:
                return None, f"Compiler returned non-PDF payload: {resp.text[:500]}"
        else:
            cloud_error = resp.text
    except Exception as e:
        cloud_error = str(e)

    # 2. Secondary fallback: Local pdflatex or xelatex if available on system
    local_compiler = shutil.which("pdflatex") or shutil.which("xelatex") or shutil.which("tectonic")
    if local_compiler:
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tex_file = os.path.join(tmpdir, "resume.tex")
                pdf_file = os.path.join(tmpdir, "resume.pdf")
                with open(tex_file, "w", encoding="utf-8") as f:
                    f.write(tex_code)
                
                cmd = [local_compiler, "-interaction=nonstopmode", "-output-directory", tmpdir, tex_file]
                proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
                
                if os.path.exists(pdf_file):
                    with open(pdf_file, "rb") as f:
                        return f.read(), "Compilation successful (via Local TeX Engine)."
                else:
                    return None, f"Local compiler failed:\n{proc.stdout.decode('utf-8', errors='ignore')[:1500]}"
        except Exception as e:
            return None, f"Local compiler execution error: {e}"

    return None, f"Cloud compilation failed: {cloud_error}\nNo local LaTeX compiler found on PATH."


def pdf_to_base64_data_uri(pdf_bytes: bytes) -> str:
    """Encodes PDF bytes to a base64 Data URI for embedding in HTML iframes."""
    b64 = base64.b64encode(pdf_bytes).decode("utf-8")
    return f"data:application/pdf;base64,{b64}"
