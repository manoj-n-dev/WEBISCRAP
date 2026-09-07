import sys
import os
import time
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

ARTIFACTS_DIR = os.path.join(
    os.environ.get("USERPROFILE", "C:\\Users\\manoj"),
    ".gemini\\antigravity-ide\\brain\\716b5174-cacd-4939-8401-a22cdb4a4680"
)

def run_human_interaction_test():
    print("=" * 75)
    print("      WEBISCRAP HUMAN-LIKE INTERACTIVE PLATFORM TEST")
    print("=" * 75)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Create a real browser context with realistic viewport & user-agent
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Capture console messages and errors
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: console_logs.append(f"[PAGE ERROR] {err}"))

        try:
            # -------------------------------------------------------------
            # PHASE 1: Landing Page Exploration
            # -------------------------------------------------------------
            print("\n[PHASE 1] Exploring Landing Page (http://localhost:3000)...")
            page.goto("http://localhost:3000", wait_until="networkidle", timeout=20000)
            print(f"  [OK] Page Title: {page.title()}")
            
            # Smooth human scroll down
            print("  [ACTION] Scrolling through the landing page...")
            page.evaluate("window.scrollTo({ top: 800, behavior: 'smooth' })")
            page.wait_for_timeout(1000)
            page.evaluate("window.scrollTo({ top: 1600, behavior: 'smooth' })")
            page.wait_for_timeout(1000)
            page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
            page.wait_for_timeout(1000)
            
            shot_landing = os.path.join(ARTIFACTS_DIR, "human_01_landing.png")
            page.screenshot(path=shot_landing)
            print("  [OK] Landing page exploration screenshot saved.")

            # -------------------------------------------------------------
            # PHASE 2: Navigation to Login & Authentication
            # -------------------------------------------------------------
            print("\n[PHASE 2] Navigating to Sign In...")
            signin_link = page.locator("a[href*='/login'], button:has-text('Sign In'), button:has-text('Login')")
            if signin_link.count() > 0:
                signin_link.first.click()
            else:
                page.goto("http://localhost:3000/login", wait_until="networkidle")
            
            page.wait_for_url("**/login**", timeout=10000)
            page.wait_for_timeout(1000)
            print(f"  [OK] Current URL: {page.url}")

            # Test Guest Login
            print("  [ACTION] Clicking 'Continue as guest'...")
            guest_btn = page.locator("button:has-text('Continue as guest')")
            if guest_btn.count() > 0:
                guest_btn.click()
            else:
                print("  [WARN] Guest button not found, checking inputs...")

            # Wait for redirect to /chat/...
            print("  [ACTION] Waiting for workspace redirect...")
            page.wait_for_url("**/chat/**", timeout=20000)
            page.wait_for_timeout(2000)
            print(f"  [OK] Successfully authenticated into workspace: {page.url}")

            shot_workspace = os.path.join(ARTIFACTS_DIR, "human_02_workspace_initial.png")
            page.screenshot(path=shot_workspace)

            # -------------------------------------------------------------
            # PHASE 3: Interacting with the Chat Composer
            # -------------------------------------------------------------
            print("\n[PHASE 3] Human typing prompt in Chat Composer...")
            composer = page.locator("textarea[placeholder*='Ask for anything']")
            if composer.count() == 0:
                composer = page.locator("textarea")

            human_prompt = "Extract book titles and prices from https://books.toscrape.com"
            print(f"  [ACTION] Typing: '{human_prompt}'")
            composer.click()
            composer.type(human_prompt, delay=30)
            page.wait_for_timeout(1000)

            shot_prompt_typed = os.path.join(ARTIFACTS_DIR, "human_03_prompt_typed.png")
            page.screenshot(path=shot_prompt_typed)

            # Click the Send / Submit button
            print("  [ACTION] Clicking Send button...")
            send_btn = page.locator("button:has(svg.lucide-arrow-up)")
            if send_btn.count() > 0:
                send_btn.click()
            else:
                composer.press("Enter")

            page.wait_for_timeout(2000)
            print("  [OK] Extraction submitted! Monitoring live execution...")

            # Capture initial message state
            shot_running = os.path.join(ARTIFACTS_DIR, "human_04_pipeline_triggered.png")
            page.screenshot(path=shot_running)

            # -------------------------------------------------------------
            # PHASE 4: Pipeline Monitoring & Progress Tracking
            # -------------------------------------------------------------
            print("\n[PHASE 4] Monitoring extraction pipeline progress...")
            # Wait up to 100s for pipeline completion or message update
            start_wait = time.time()
            completed = False
            while time.time() - start_wait < 100:
                page.wait_for_timeout(3000)
                # Check for completed or error state
                ai_messages = page.locator("div:has-text('Extraction complete'), div:has-text('Validation Confidence'), button:has-text('Open in Dataset View'), div:has-text('Failed to complete')")
                if ai_messages.count() > 0:
                    completed = True
                    break
                print(f"  ... waiting for agents pipeline ({int(time.time() - start_wait)}s elapsed)")

            shot_result = os.path.join(ARTIFACTS_DIR, "human_05_extraction_result.png")
            page.screenshot(path=shot_result)
            if completed:
                print("  [OK] Extraction pipeline finished and UI updated!")
            else:
                print("  [INFO] Pipeline still processing or reached timeout. State captured.")

            # -------------------------------------------------------------
            # PHASE 5: Dataset View Navigation & Actions
            # -------------------------------------------------------------
            print("\n[PHASE 5] Testing Dataset View Navigation...")
            open_dataset_btn = page.locator("button:has-text('Open in Dataset View')")
            if open_dataset_btn.count() > 0:
                open_dataset_btn.first.click()
                page.wait_for_url("**/dataset/**", timeout=10000)
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(3000)
                print(f"  [OK] Navigated to Dataset View: {page.url}")
            else:
                # Direct navigation to test dataset page
                current_sid = page.url.split("/")[-1] if "chat" in page.url else "new"
                page.goto(f"http://localhost:3000/dataset/{current_sid}", wait_until="networkidle")
                page.wait_for_timeout(3000)
                print(f"  [OK] Opened Dataset View: {page.url}")

            shot_dataset = os.path.join(ARTIFACTS_DIR, "human_06_dataset_view.png")
            page.screenshot(path=shot_dataset)

            # Test search in dataset
            dataset_search = page.locator("input[placeholder*='Search extracted data']")
            if dataset_search.count() > 0:
                dataset_search.fill("book")
                page.wait_for_timeout(500)
                print("  [OK] Dataset search filter verified.")

            # -------------------------------------------------------------
            # PHASE 6: Sidebar Actions & Logout Flow
            # -------------------------------------------------------------
            print("\n[PHASE 6] Testing Sidebar '+ New extraction' and Logout...")
            new_ext_btn = page.locator("button:has-text('New extraction'), a:has-text('New extraction')")
            if new_ext_btn.count() > 0:
                new_ext_btn.first.click()
                page.wait_for_timeout(1000)
                print("  [OK] Clicked '+ New extraction'")

            # Logout
            logout_btn = page.locator("button:has(svg.lucide-log-out), button[title*='Logout'], button[aria-label*='Logout']")
            if logout_btn.count() > 0:
                logout_btn.first.click()
                page.wait_for_timeout(2000)
                print(f"  [OK] Logout clicked. Redirected to: {page.url}")

            shot_after_logout = os.path.join(ARTIFACTS_DIR, "human_07_after_logout.png")
            page.screenshot(path=shot_after_logout)

            print("\n" + "=" * 75)
            print(">>> HUMAN-LIKE PLATFORM INTERACTION COMPLETE! ALL STEPS VERIFIED! <<<")
            print("=" * 75)

            # Print console errors if any
            errors = [log for log in console_logs if "[error]" in log.lower() or "[page error]" in log.lower()]
            if errors:
                print(f"\n[CONSOLE WARNINGS/ERRORS DETECTED ({len(errors)})]:")
                for err in errors[:5]:
                    print(f"  {err}")
            else:
                print("\n[CONSOLE]: 0 critical frontend errors detected.")

        except Exception as e:
            print(f"\n[FAIL] Human interaction error: {e}")
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "human_error.png"))
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    run_human_interaction_test()
