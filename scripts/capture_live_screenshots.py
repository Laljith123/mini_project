"""
Capture authentic, high-resolution working screenshots of the Streamlit application using Playwright.
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

def capture_screenshots():
    out_dir = Path("report_screenshots")
    out_dir.mkdir(exist_ok=True)

    port = 8511
    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app/streamlit_app.py", f"--server.port={port}", "--server.headless=true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(5)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1400, "height": 920})
            page = context.new_page()

            # 1. Overview Dashboard
            print("Capturing Overview...")
            page.goto(f"http://localhost:{port}/?demo_seed=1&view=Overview")
            page.wait_for_timeout(4000)
            page.screenshot(path=str(out_dir / "cloud_eng_overview.png"))

            # 2. Profile View
            print("Capturing Profile View...")
            profile_btn = page.locator('button[data-testid="baseButton-secondary"]:has-text("Profile & Skills"), button:has-text("Profile & Skills")')
            if profile_btn.count() > 0:
                profile_btn.first.click()
            else:
                page.goto(f"http://localhost:{port}/?view=Profile")
            page.wait_for_timeout(3000)
            page.screenshot(path=str(out_dir / "data_eng_profile.png"))

            # 3. JD Generator
            print("Capturing JD Generator...")
            jd_btn = page.locator('button:has-text("JD Generator")')
            if jd_btn.count() > 0:
                jd_btn.first.click()
            else:
                page.goto(f"http://localhost:{port}/?view=JD+Generator")
            page.wait_for_timeout(3000)
            page.screenshot(path=str(out_dir / "ai_eng_jd_generator.png"))

            # 4. Resume Studio
            print("Capturing Resume Studio...")
            cv_btn = page.locator('button:has-text("Resume Studio")')
            if cv_btn.count() > 0:
                cv_btn.first.click()
            else:
                page.goto(f"http://localhost:{port}/?view=Resume+Studio")
            page.wait_for_timeout(3000)
            page.screenshot(path=str(out_dir / "ai_eng_resume_studio.png"))

            # 5. Job Matches
            print("Capturing Job Matches...")
            jobs_btn = page.locator('button:has-text("Job Matches")')
            if jobs_btn.count() > 0:
                jobs_btn.first.click()
            else:
                page.goto(f"http://localhost:{port}/?view=Jobs")
            page.wait_for_timeout(3000)
            page.screenshot(path=str(out_dir / "ai_eng_job_matches.png"))

            # 6. Career Mentor
            print("Capturing Career Mentor...")
            mentor_btn = page.locator('button:has-text("Career Mentor")')
            if mentor_btn.count() > 0:
                mentor_btn.first.click()
            else:
                page.goto(f"http://localhost:{port}/?view=Career+Mentor")
            page.wait_for_timeout(3000)
            page.screenshot(path=str(out_dir / "security_eng_mentor.png"))

            # 7. Evaluation & Telemetry
            print("Capturing Evaluation...")
            eval_btn = page.locator('button:has-text("Evaluation")')
            if eval_btn.count() > 0:
                eval_btn.first.click()
            else:
                page.goto(f"http://localhost:{port}/?view=Evaluation")
            page.wait_for_timeout(3000)
            page.screenshot(path=str(out_dir / "security_eng_telemetry.png"))

            # 8. Settings
            print("Capturing Settings...")
            settings_btn = page.locator('button:has-text("Settings")')
            if settings_btn.count() > 0:
                settings_btn.first.click()
            else:
                page.goto(f"http://localhost:{port}/?view=Settings")
            page.wait_for_timeout(3000)
            page.screenshot(path=str(out_dir / "cloud_eng_settings.png"))

            browser.close()
            print("All rich working screenshots captured successfully!")
    finally:
        proc.terminate()

if __name__ == "__main__":
    capture_screenshots()
