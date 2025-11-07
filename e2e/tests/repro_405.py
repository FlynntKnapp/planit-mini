# e2e/tests/repro_405.py
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

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

    # Try common Django field names; adjust if your template uses different names/ids
    if page.locator("input[name='username']").count():
        page.locator("input[name='username']").fill(USERNAME)
    elif page.get_by_label("Username").count():
        page.get_by_label("Username").fill(USERNAME)
    else:
        page.fill("input[type='text']", USERNAME)

    if page.locator("input[name='password']").count():
        page.locator("input[name='password']").fill(PASSWORD)
    elif page.get_by_label("Password").count():
        page.get_by_label("Password").fill(PASSWORD)
    else:
        page.fill("input[type='password']", PASSWORD)

    # Submit (try a few common selectors)
    if page.get_by_role(
        "button", name=lambda n: "log in" in n.lower() or "sign in" in n.lower()
    ).count():
        page.get_by_role(
            "button", name=lambda n: "log in" in n.lower() or "sign in" in n.lower()
        ).click()
    elif page.locator("input[type='submit']").count():
        page.locator("input[type='submit']").click()
    else:
        page.press("form", "Enter")

    # Sanity: you should be redirected to a logged-in page and get a session cookie
    page.wait_for_load_state("networkidle")
    assert any(
        c["name"] == "sessionid" for c in page.context.cookies()
    ), "No Django session cookie after login"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir=str(ARTIFACTS),
            record_har_path=str(ARTIFACTS / "network.har"),
        )
        page = context.new_page()

        # Log 4xx/5xx to console so we catch the 405 in terminal output too
        page.on(
            "response",
            lambda r: r.status >= 400
            and print(f"[{r.status}] {r.request.method} {r.url}"),
        )

        # 1) Log in
        login(page)

        # 2) Navigate to the route that requires auth (e.g., logout)
        page.goto(f"{BASE_URL.rstrip('/')}{BUG_PATH}", wait_until="load")

        # 3) Confirm we actually saw a 405 somewhere (page load or subrequest)
        try:
            r = page.wait_for_response(lambda resp: resp.status == 405, timeout=3000)
            print(f"Confirmed 405: {r.request.method} {r.url}")
        except Exception:
            print(
                "No 405 observed within 3s—double-check BUG_PATH or add a longer timeout."
            )

        page.wait_for_timeout(1200)  # gives the video a clear end frame
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
