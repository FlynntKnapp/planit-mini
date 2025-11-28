# tests/e2e/test_admin_login_flow.py

import os
from pathlib import Path  # noqa F401

from playwright.sync_api import sync_playwright, expect

try:
    from dotenv import load_dotenv

    # Load a local .env if present (handy for dev)
    load_dotenv()
except ImportError:
    # If python-dotenv isn't installed, env vars must be set via shell/Heroku
    pass


BASE_URL = os.environ.get(
    "PLANIT_BASE_URL",
    "https://planit-mini-dev-1595bd0e6432.herokuapp.com",
)
USERNAME = os.environ.get("PLANIT_SUPERUSER_USERNAME")
PASSWORD = os.environ.get("PLANIT_SUPERUSER_PASSWORD")


def test_superuser_stays_logged_in_to_admin(tmp_path):
    """
    Reproduce bug:

    1. Go to site root.
    2. Visit /accounts/login/ and log in as superuser.
    3. Visit /admin/.
    4. Try to visit /admin/accounts/customuser/.
    5. Assert we are NOT redirected to admin login again.

    Test also records a video of the session so we can inspect what happens.
    """

    assert USERNAME, "PLANIT_SUPERUSER_USERNAME env var must be set"
    assert PASSWORD, "PLANIT_SUPERUSER_PASSWORD env var must be set"

    video_dir = tmp_path / "playwright-videos"
    video_dir.mkdir(exist_ok=True)

    with sync_playwright() as p:
        # Set headless=False so you can watch it live.
        # Change to True for CI.
        browser = p.chromium.launch(headless=False)

        context = browser.new_context(
            record_video_dir=str(video_dir),
            # If you want, you can also fix video size:
            # record_video_size={"width": 1280, "height": 720},
        )

        page = context.new_page()

        # Capture the Video object now (you can read path after context.close()).
        video = page.video

        try:
            # 1. Go to site root
            page.goto(BASE_URL, wait_until="networkidle")

            # 2. Go to login page (mirrors your described flow)
            page.goto(f"{BASE_URL}/accounts/login/", wait_until="networkidle")

            # Fill in username/password (standard Django auth form field names)
            page.fill('input[name="username"]', USERNAME)
            page.fill('input[name="password"]', PASSWORD)

            # Click the login button.
            # Adjust selector if your template uses something different.
            page.click("input[type='submit'], button[type='submit']")

            # Wait for redirect after login
            page.wait_for_load_state("networkidle")

            # Basic sanity check: verify the session looks logged in.
            # You may want to tweak this selector based on your template.
            # For example, if you have a "Log out" link:
            # expect(page.locator("a[href='/accounts/logout/']")).to_be_visible()
            print("After login current URL:", page.url)

            # 3. Go to admin root
            page.goto(f"{BASE_URL}/admin/", wait_until="networkidle")
            print("Admin root URL:", page.url)

            # Assert we did not get bounced to admin login already
            assert "/admin/login/" not in page.url, (
                "Already got redirected to admin login when visiting /admin/. "
                f"URL was: {page.url}"
            )

            # 4. Try to go directly to CustomUser changelist
            target_url = f"{BASE_URL}/admin/accounts/customuser/"
            page.goto(target_url, wait_until="networkidle")
            print("CustomUser target URL:", page.url)

            # 5. Check if we were redirected back to login with ?next=
            redirected_to_login = (
                "/admin/login/" in page.url
                and "next=/admin/accounts/customuser/" in page.url
            )

            # This is the bug condition we care about:
            assert not redirected_to_login, (
                "BUG: Visiting /admin/accounts/customuser/ caused a redirect "
                f"back to admin login. Final URL was: {page.url}"
            )

            # Extra check: ensure we can actually see the changelist heading.
            # Adjust text if your admin shows something slightly different.
            expect(page.locator("body")).to_contain_text("Select user to change")

        finally:
            # Close context so video is finalized, then print video path
            context.close()
            browser.close()

            # video.path() only works after context.close()
            try:
                video_path = video.path()
                print("Playwright video saved to:", video_path)
            except Exception as e:  # noqa: BLE001
                print("Could not retrieve video path:", e)
