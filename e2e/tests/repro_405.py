# e2e/tests/repro_405.py
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost:8000")
BUG_PATH = os.getenv("E2E_BUG_PATH", "/accounts/logout/")  # e.g. /accounts/some-action/

ARTIFACTS = Path(__file__).resolve().parents[1] / "artifacts"
ARTIFACTS.mkdir(parents=True, exist_ok=True)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir=str(ARTIFACTS),
            record_har_path=str(ARTIFACTS / "network.har"),
        )
        page = context.new_page()

        # Log any 4xx/5xx so the run clearly shows the 405
        def log_bad(resp):
            if resp.status >= 400:
                print(f"[{resp.status}] {resp.request.method} {resp.url}")

        page.on("response", log_bad)

        page.goto(BASE_URL, wait_until="networkidle")
        page.goto(f"{BASE_URL.rstrip('/')}{BUG_PATH}", wait_until="load")

        # Optional: assert we actually saw a 405 on any request
        try:
            resp = page.wait_for_response(lambda r: r.status == 405, timeout=3000)
            print(f"Confirmed 405: {resp.request.method} {resp.url}")
        except Exception:
            print("No 405 response observed within 3s — check path or timing.")

        page.wait_for_timeout(1200)  # give the video a beat to show the result
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
