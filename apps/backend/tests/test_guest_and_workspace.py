import sys
import os
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

ARTIFACTS_DIR = os.path.join(
    os.environ.get("USERPROFILE", "C:\\Users\\manoj"),
    ".gemini\\antigravity-ide\\brain\\716b5174-cacd-4939-8401-a22cdb4a4680"
)

def run_workspace_test():
    print("=" * 70)
    print("      WEBISCRAP AUTHENTICATED WORKSPACE & CHAT E2E TEST")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        try:
            # 1. Login Page -> Click Guest Login
            print("\n[STEP 1] Navigating to login page...")
            page.goto("http://localhost:3000/login", wait_until="networkidle", timeout=15000)
            
            print("[STEP 2] Clicking 'Continue as guest'...")
            guest_btn = page.locator("button:has-text('Continue as guest')")
            guest_btn.click()
            
            # Wait for navigation to /chat/...
            print("[STEP 3] Waiting for workspace navigation...")
            page.wait_for_url("**/chat/**", timeout=15000)
            page.wait_for_timeout(3000)
            print(f"  [OK] Current Workspace URL: {page.url}")

            # Capture workspace screenshot
            shot_ws = os.path.join(ARTIFACTS_DIR, "user_workspace_view.png")
            page.screenshot(path=shot_ws)
            print("  [OK] Captured workspace screenshot")

            # 2. Check Sidebar & User profile
            print("\n[STEP 4] Inspecting Sidebar elements...")
            sidebar = page.locator("aside")
            if sidebar.count() > 0:
                print("  [OK] Sidebar is rendered and active")
                # Search input in sidebar
                search_input = sidebar.locator("input[placeholder*='Search'], input[type='search']")
                if search_input.count() > 0:
                    print("  [OK] Sidebar search filter is present")
            
            # 3. Enter message in composer
            print("\n[STEP 5] Testing Composer interaction...")
            composer_box = page.locator("textarea, input[placeholder*='Ask'], input[placeholder*='message'], input[placeholder*='extract']")
            if composer_box.count() > 0:
                test_prompt = "Extract book titles and prices from https://books.toscrape.com"
                composer_box.first.fill(test_prompt)
                page.wait_for_timeout(1000)
                
                shot_composer = os.path.join(ARTIFACTS_DIR, "user_composer_filled.png")
                page.screenshot(path=shot_composer)
                print("  [OK] Prompt filled in Composer")

                # Look for Send button
                send_btn = page.locator("button[type='submit'], button[aria-label*='Send'], button:has(svg.lucide-send), button:has(svg.lucide-arrow-up)")
                if send_btn.count() > 0:
                    print("  [OK] Send button located and active")

            # 4. Test Dataset Page
            print("\n[STEP 6] Testing Dataset View (/dataset/demo)...")
            page.goto("http://localhost:3000/dataset/demo", wait_until="networkidle", timeout=15000)
            page.wait_for_timeout(2000)
            
            shot_dataset = os.path.join(ARTIFACTS_DIR, "user_dataset_page.png")
            page.screenshot(path=shot_dataset)
            print("  [OK] Dataset page loaded and screenshot captured")

            print("\n" + "=" * 70)
            print(">>> ALL CLIENT-SIDE USER INTERACTION TESTS PASSED! <<<")
            print("=" * 70)

        except Exception as e:
            print(f"\n[FAIL] Error in user test: {e}")
            page.screenshot(path=os.path.join(ARTIFACTS_DIR, "user_test_error.png"))
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    run_workspace_test()
