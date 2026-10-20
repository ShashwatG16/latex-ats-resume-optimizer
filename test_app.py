"""
test_app.py
Smoke test for database, compiler, ATS engine, and templates.
"""

import unittest
from core.database import init_db, get_all_users, get_user_by_id, save_application, get_applications_for_user
from core.templates import DEFAULT_DAISY_TEX, DEFAULT_SHASHWAT_TEX
from core.compiler import compile_latex_to_pdf
from core.ats_engine import evaluate_ats_match, tailor_resume_heuristically


class TestJobTailorPortal(unittest.TestCase):
    def setUp(self):
        init_db(default_daisy_tex=DEFAULT_DAISY_TEX, default_shashwat_tex=DEFAULT_SHASHWAT_TEX)

    def test_database_initialization_and_users(self):
        users = get_all_users()
        self.assertGreaterEqual(len(users), 2)
        names = [u["name"] for u in users]
        self.assertIn("Daisy Phukan", names)
        self.assertIn("Shashwat Gautam", names)

    def test_ats_match_evaluation(self):
        sample_jd = """
        Deloitte Touche Tohmatsu India LLP
        Analyst | D365 F&O - Functional SCM | Bengaluru
        Requirements:
        - Requirement gathering workshops with consultants
        - Functional Design Document (FDD)
        - Unit Testing, System Integration Testing (SIT), User Acceptance Testing (UAT)
        - Master data setup and data migration
        - Mechanical Engineering / BE
        """
        eval_res = evaluate_ats_match(sample_jd, DEFAULT_DAISY_TEX)
        self.assertIn("match_percentage", eval_res)
        self.assertIn("matched_keywords", eval_res)
        self.assertIn("missing_keywords", eval_res)
        self.assertGreater(eval_res["total_keywords"], 5)

    def test_heuristic_tailoring_zero_fabrication(self):
        sample_jd = "Analyst D365 F&O Functional SCM requirement gathering FDD SIT UAT"
        tailored_tex, stats = tailor_resume_heuristically(
            DEFAULT_DAISY_TEX,
            sample_jd,
            "Deloitte",
            "Analyst | D365 F&O - Functional SCM"
        )
        self.assertIn("Deloitte", tailored_tex)
        self.assertIn("FDD", tailored_tex)
        # Verify candidate degree is NOT changed
        self.assertIn("Bachelor of Technology (B.Tech) in Mechanical Engineering", tailored_tex)
        # Verify no false CGPA was injected
        self.assertNotIn("CGPA: 8.42", tailored_tex)

    def test_cloud_latex_compilation(self):
        sample_tex = r"\documentclass{article}\begin{document}Testing JobTailor Portal\end{document}"
        pdf_bytes, msg = compile_latex_to_pdf(sample_tex)
        self.assertIsNotNone(pdf_bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))

    def test_save_and_retrieve_application(self):
        user = get_all_users()[0]
        app_id = save_application(
            user_id=user["id"],
            company="Test Corp",
            job_title="Software Systems Engineer",
            requisition_id="REQ-999",
            location="Remote",
            job_url="https://testcorp.com/jobs/999",
            job_description="Python, Docker, Distributed Systems",
            ats_score=85.0,
            matched_keywords='["python", "docker"]',
            missing_keywords='["distributed systems"]',
            tailored_latex=user["master_latex"],
            pdf_bytes=b"%PDF-1.4 dummy",
            status="Applied",
            notes="Test application notes"
        )
        self.assertGreater(app_id, 0)
        user_apps = get_applications_for_user(user["id"])
        saved_app = next(a for a in user_apps if a["id"] == app_id)
        self.assertEqual(saved_app["company"], "Test Corp")
        self.assertEqual(saved_app["status"], "Applied")


if __name__ == "__main__":
    unittest.main()
