# e2e/tests/repro_405.py
import os
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost:8000")
BUG_PATH = os.getenv(
    "E2E_BUG_PATH", "/accounts/logout/"
)  # the route that 405s when logged in
USERNAME = os.getenv("E2E_USERNAME", "admin")
PASSWORD = os.getenv("E2E_PASSWORD", "password")

ARTIFACTS = Path(__file__).resolve().parents[1] / "artifacts"
ARTIFACTS.mkdir(parents=True, exist_ok=True)


def login(page):
    page.goto(f"{BASE_URL.rstrip('/')}/accounts/login/", wait_until="domcontentloaded")

    # Fill username
    if page.locator("input[name='username']").count():
        page.locator("input[name='username']").fill(USERNAME)
    elif page.get_by_label(re.compile(r"username", re.I)).count():
        page.get_by_label(re.compile(r"username", re.I)).fill(USERNAME)
    else:
        page.locator("input[type='text']").first.fill(USERNAME)

    # Fill password
    if page.locator("input[name='password']").count():
        page.locator("input[name='password']").fill(PASSWORD)
    elif page.get_by_label(re.compile(r"password", re.I)).count():
        page.get_by_label(re.compile(r"password", re.I)).fill(PASSWORD)
    else:
        page.locator("input[type='password']").first.fill(PASSWORD)

    # Submit the form
    login_btn = page.get_by_role("button", name=re.compile(r"(log ?in|sign ?in)", re.I))
    if login_btn.count():
        login_btn.first.click()
    elif page.locator("input[type='submit']").count():
        page.locator("input[type='submit']").first.click()
    else:
        page.press("form", "Enter")

    # Confirm session established
    page.wait_for_load_state("networkidle")
    cookies = page.context.cookies()
    assert any(
        c.get("name") == "sessionid" for c in cookies
    ), "No Django session cookie after login"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # set False to watch it
        context = browser.new_context(
            record_video_dir=str(ARTIFACTS),
            record_har_path=str(ARTIFACTS / "network.har"),
        )
        page = context.new_page()

        # Log 4xx/5xx to the console (helps prove the 405)
        page.on(
            "response",
            lambda r: r.status >= 400
            and print(f"[{r.status}] {r.request.method} {r.url}"),
        )

        # 1) Log in
        login(page)

        # 2) Go to the offending route (e.g., logout)
        page.goto(f"{BASE_URL.rstrip('/')}{BUG_PATH}", wait_until="load")

        # 3) Confirm we actually saw a 405
        try:
            r = page.wait_for_response(lambda resp: resp.status == 405, timeout=5000)
            print(f"Confirmed 405: {r.request.method} {r.url}")
        except Exception:
            print(
                "No 405 observed within 5s—double-check BUG_PATH or increase timeout."
            )

        page.wait_for_timeout(1200)
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
