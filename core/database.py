"""
core/database.py
SQLite persistence layer for Users, Master LaTeX Resumes, and Job Applications.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "applications.db")
PDF_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "compiled_pdfs")

os.makedirs(PDF_DIR, exist_ok=True)


def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(default_daisy_tex: str = "", default_shashwat_tex: str = ""):
    conn = get_connection()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                email TEXT,
                phone TEXT,
                headline TEXT,
                master_latex TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                company TEXT NOT NULL,
                job_title TEXT NOT NULL,
                requisition_id TEXT,
                location TEXT,
                job_url TEXT,
                job_description TEXT NOT NULL,
                ats_score REAL DEFAULT 0.0,
                matched_keywords TEXT,
                missing_keywords TEXT,
                tailored_latex TEXT NOT NULL,
                pdf_filename TEXT,
                status TEXT DEFAULT 'Draft',
                applied_date TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)

    # Seed default user profiles if not present
    if default_daisy_tex:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE name = ?", ("Daisy Phukan",))
        if not cursor.fetchone():
            cursor.execute(
                """
                INSERT INTO users (name, email, phone, headline, master_latex)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    "Daisy Phukan",
                    "daisyphukan6004@gmail.com",
                    "+91 6003617978",
                    "Technical Project Manager -- Trainee | B.Tech Mechanical Engineering | Systems & Analytics",
                    default_daisy_tex,
                ),
            )
            conn.commit()

    if default_shashwat_tex:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE name = ?", ("Shashwat Gautam",))
        if not cursor.fetchone():
            cursor.execute(
                """
                INSERT INTO users (name, email, phone, headline, master_latex)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    "Shashwat Gautam",
                    "iit2020030@iiita.ac.in",
                    "+91 9999999999",
                    "Software Systems Engineer | IIIT Allahabad | Full Stack & Optimization",
                    default_shashwat_tex,
                ),
            )
            conn.commit()
    conn.close()


def get_all_users() -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_by_id(user_id: int) -> Optional[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_user_master_latex(user_id: int, new_latex: str, headline: str = None):
    conn = get_connection()
    with conn:
        if headline:
            conn.execute(
                "UPDATE users SET master_latex = ?, headline = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (new_latex, headline, user_id),
            )
        else:
            conn.execute(
                "UPDATE users SET master_latex = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (new_latex, user_id),
            )


def create_user(name: str, email: str, phone: str, headline: str, master_latex: str) -> int:
    conn = get_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (name, email, phone, headline, master_latex)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, email, phone, headline, master_latex),
        )
        user_id = cursor.lastrowid
    return user_id


def save_application(
    user_id: int,
    company: str,
    job_title: str,
    requisition_id: str,
    location: str,
    job_url: str,
    job_description: str,
    ats_score: float,
    matched_keywords: str,
    missing_keywords: str,
    tailored_latex: str,
    pdf_bytes: Optional[bytes] = None,
    status: str = "Draft",
    applied_date: str = "",
    notes: str = "",
) -> int:
    pdf_filename = None
    if pdf_bytes:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_co = "".join(c for c in company if c.isalnum() or c in ("-", "_")).rstrip()
        safe_role = "".join(c for c in job_title if c.isalnum() or c in ("-", "_")).rstrip()
        pdf_filename = f"{user_id}_{safe_co}_{safe_role}_{timestamp}.pdf"
        pdf_path = os.path.join(PDF_DIR, pdf_filename)
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)

    if not applied_date:
        applied_date = datetime.now().strftime("%Y-%m-%d")

    conn = get_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO applications (
                user_id, company, job_title, requisition_id, location, job_url,
                job_description, ats_score, matched_keywords, missing_keywords,
                tailored_latex, pdf_filename, status, applied_date, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                company,
                job_title,
                requisition_id,
                location,
                job_url,
                job_description,
                ats_score,
                matched_keywords,
                missing_keywords,
                tailored_latex,
                pdf_filename,
                status,
                applied_date,
                notes,
            ),
        )
        app_id = cursor.lastrowid
    return app_id


def get_applications_for_user(user_id: int) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM applications 
        WHERE user_id = ? 
        ORDER BY created_at DESC
        """,
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_application_by_id(app_id: int) -> Optional[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_application_status(app_id: int, new_status: str, notes: str = None):
    conn = get_connection()
    with conn:
        if notes is not None:
            conn.execute(
                "UPDATE applications SET status = ?, notes = ? WHERE id = ?",
                (new_status, notes, app_id),
            )
        else:
            conn.execute(
                "UPDATE applications SET status = ? WHERE id = ?",
                (new_status, app_id),
            )


def update_application_resume(app_id: int, tailored_latex: str, pdf_bytes: Optional[bytes] = None):
    conn = get_connection()
    pdf_filename = None
    if pdf_bytes:
        app = get_application_by_id(app_id)
        if app:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_co = "".join(c for c in app["company"] if c.isalnum() or c in ("-", "_")).rstrip()
            pdf_filename = f"{app['user_id']}_{safe_co}_{timestamp}.pdf"
            pdf_path = os.path.join(PDF_DIR, pdf_filename)
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)

    with conn:
        if pdf_filename:
            conn.execute(
                "UPDATE applications SET tailored_latex = ?, pdf_filename = ? WHERE id = ?",
                (tailored_latex, pdf_filename, app_id),
            )
        else:
            conn.execute(
                "UPDATE applications SET tailored_latex = ? WHERE id = ?",
                (tailored_latex, app_id),
            )


def delete_application(app_id: int):
    conn = get_connection()
    app = get_application_by_id(app_id)
    if app and app.get("pdf_filename"):
        pdf_path = os.path.join(PDF_DIR, app["pdf_filename"])
        if os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
            except Exception:
                pass
    with conn:
        conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))
