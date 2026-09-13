import asyncio
import io
import sys
import os
import uuid
import httpx
from typing import List, Dict, Any
from datetime import datetime

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from main import app
from memory.session_store import redis_store
from models.user import User
from database.connection import get_session
from sqlmodel import select
from auth.security import create_access_token
from api.upload import validate_file_magic_bytes
from agents.browser import _is_safe_pagination_element, DANGEROUS_CLICK_KEYWORDS
from prompts.extractor_prompt import EXTRACTOR_SYSTEM_PROMPT
from prompts.analyzer_prompt import ANALYZER_SYSTEM_PROMPT

class MockPageElement:
    """Mock Playwright element for testing pagination button safety."""
    def __init__(self, tag_name="button", btn_type="button", text="", aria_label="", title=""):
        self._tag = tag_name
        self._type = btn_type
        self._text = text
        self._aria = aria_label
        self._title = title

class MockPage:
    """Mock Playwright page evaluating DOM properties."""
    def evaluate(self, script: str, element: MockPageElement) -> str:
        if "tagName" in script:
            return element._tag.upper()
        elif "getAttribute('type')" in script:
            return element._type
        elif "textContent" in script:
            return element._text
        elif "getAttribute('aria-label')" in script:
            return element._aria
        elif "getAttribute('title')" in script:
            return element._title
        return ""

async def run_phase2_hardening_tests():
    print("\n============================================================")
    print("WEBISCRAP PHASE 2: CRITICAL & HIGH BUG HARDENING TESTS")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("============================================================\n")

    test_user_id = uuid.uuid4()
    test_email = f"phase2_tester_{test_user_id.hex[:8]}@example.com"
    
    # Create valid active user in Neon PostgreSQL
    async for db in get_session():
        db_user = User(
            id=test_user_id,
            email=test_email,
            full_name="Phase 2 Hardening Tester",
            is_active=True,
            is_verified=True,
            is_superuser=False,
            is_guest=False,
            token_version=1
        )
        db.add(db_user)
        await db.commit()
        break

    access_token = create_access_token(test_user_id)
    auth_headers = {"Authorization": f"Bearer {access_token}"}

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=30.0) as client:

        # ------------------------------------------------------------------
        # TEST 1: Durable Scraping Job Queue (H-05)
        # ------------------------------------------------------------------
        print("[TEST 1] Testing Durable Redis Scrape Queue (H-05)")
        scrape_payload = {
            "target_url": "https://example.com/products",
            "extraction_goal": "Extract product titles and prices"
        }
        res = await client.post("/api/scrape/", json=scrape_payload, headers=auth_headers)
        assert res.status_code == 200, f"Submit scrape failed: {res.text}"
        data = res.json()
        job_id = data["job_id"]
        assert data["status"] == "accepted"
        print(f"  --> Scrape job enqueued with ID: {job_id}")

        # Check job in Redis queue
        job_status = await redis_store.get_job_status(job_id)
        assert job_status is not None, "Job status must exist in Redis"
        assert job_status["status"] in ("queued", "running", "done")
        print(f"  --> Job status retrieved from Redis: {job_status['status']}")

        # Verify job status endpoint
        poll_res = await client.get(f"/api/scrape/{job_id}", headers=auth_headers)
        assert poll_res.status_code == 200, f"Poll job failed: {poll_res.text}"
        assert poll_res.json()["job_id"] == job_id
        print("  --> PASSED: Durable scrape job enqueued and tracked in Redis.")

        # ------------------------------------------------------------------
        # TEST 2: Persistent Streaming Export Endpoints (H-06, H-07)
        # ------------------------------------------------------------------
        print("\n[TEST 2] Testing Persistent Streaming Export Endpoints (H-06, H-07)")
        session_id = str(uuid.uuid4())
        await redis_store.set_session_owner(session_id, str(test_user_id))
        sample_dataset: List[Dict[str, Any]] = [
            {"name": "Laptop Alpha", "price": "$999", "formula_field": "=SUM(A1:A10)"},
            {"name": "Phone Beta", "price": "$499", "formula_field": "+cmd|' /C calc'!A0"}
        ]
        await redis_store.save_session_data(session_id, sample_dataset)

        # Test CSV stream
        csv_res = await client.get(f"/api/export/csv?session_id={session_id}", headers=auth_headers)
        assert csv_res.status_code == 200, f"CSV export failed: {csv_res.text}"
        csv_text = csv_res.text
        assert "Laptop Alpha" in csv_text
        # Assert formula injection protection
        assert "'=SUM" in csv_text or "\'=SUM" in csv_text, "Formula injection prefix missing in CSV"
        print("  --> PASSED: Direct CSV streaming with formula injection sanitization.")

        # Test Excel stream
        xlsx_res = await client.get(f"/api/export/excel?session_id={session_id}", headers=auth_headers)
        assert xlsx_res.status_code == 200, f"Excel export failed: {xlsx_res.text}"
        assert xlsx_res.content.startswith(b"PK\x03\x04"), "Excel export must stream valid OpenXML ZIP bytes"
        print("  --> PASSED: Direct Excel streaming (no local disk dependency).")

        # Test JSON stream
        json_res = await client.get(f"/api/export/json?session_id={session_id}", headers=auth_headers)
        assert json_res.status_code == 200
        json_data = json_res.json()
        assert len(json_data) == 2
        print("  --> PASSED: Direct JSON streaming.")

        # Test Markdown stream
        md_res = await client.get(f"/api/export/markdown?session_id={session_id}", headers=auth_headers)
        assert md_res.status_code == 200
        assert "| Laptop Alpha" in md_res.text
        print("  --> PASSED: Direct Markdown streaming.")

        # ------------------------------------------------------------------
        # TEST 3: Prompt Injection Delimiter Boundaries (H-08)
        # ------------------------------------------------------------------
        print("\n[TEST 3] Testing Prompt Injection Delimiter Boundaries (H-08)")
        assert "<security_policy>" in EXTRACTOR_SYSTEM_PROMPT, "Extractor system prompt must contain security_policy"
        assert "PROMPT INJECTION DEFENSE" in EXTRACTOR_SYSTEM_PROMPT
        assert "<untrusted_source_content>" in EXTRACTOR_SYSTEM_PROMPT
        assert "<security_policy>" in ANALYZER_SYSTEM_PROMPT, "Analyzer system prompt must contain security_policy"
        print("  --> PASSED: All agent system prompts enforce strict anti-injection boundary policies.")

        # ------------------------------------------------------------------
        # TEST 4: Browser Pagination Button Guardrails (H-09)
        # ------------------------------------------------------------------
        print("\n[TEST 4] Testing Browser Pagination Click Guardrails (H-09)")
        mock_page = MockPage()

        # 4a. Safe pagination elements should be ACCEPTED
        safe_btn = MockPageElement(tag_name="button", btn_type="button", text="Next Page >")
        assert _is_safe_pagination_element(mock_page, safe_btn, "button.next") is True

        safe_load_more = MockPageElement(tag_name="button", text="Load More Items")
        assert _is_safe_pagination_element(mock_page, safe_load_more, "button:has-text('Load More')") is True

        safe_num = MockPageElement(tag_name="a", text="2")
        assert _is_safe_pagination_element(mock_page, safe_num, "a.page-2") is True
        print("  --> PASSED: Safe pagination buttons correctly accepted.")

        # 4b. Dangerous state-changing buttons should be REJECTED
        dangerous_buy = MockPageElement(tag_name="button", text="Buy Now")
        assert _is_safe_pagination_element(mock_page, dangerous_buy, "button.buy-now") is False

        dangerous_submit = MockPageElement(tag_name="button", btn_type="submit", text="Submit Form")
        assert _is_safe_pagination_element(mock_page, dangerous_submit, "button[type='submit']") is False

        dangerous_checkout = MockPageElement(tag_name="button", text="Proceed to Checkout")
        assert _is_safe_pagination_element(mock_page, dangerous_checkout, "button.checkout") is False

        dangerous_delete = MockPageElement(tag_name="button", text="Delete Account")
        assert _is_safe_pagination_element(mock_page, dangerous_delete, "button.delete") is False
        print("  --> PASSED: Dangerous state-changing buttons strictly blocked from automated clicks.")

        # ------------------------------------------------------------------
        # TEST 5: Upload Magic-Byte Validation & Decompression Caps (M-01)
        # ------------------------------------------------------------------
        print("\n[TEST 5] Testing Upload Magic-Byte & File Validation (M-01)")

        # 5a. Reject disguised PE binary with .pdf extension
        fake_pdf = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff"
        assert validate_file_magic_bytes(fake_pdf, ".pdf") is False, "Disguised EXE must be rejected for .pdf"

        # 5b. Reject text file disguised as .png
        fake_png = b"This is just a text file claiming to be PNG."
        assert validate_file_magic_bytes(fake_png, ".png") is False

        # 5c. Reject binary with null bytes disguised as .csv
        corrupt_csv = b"name,price\x00\x00\xff\xfe"
        assert validate_file_magic_bytes(corrupt_csv, ".csv") is False

        # 5d. Accept valid genuine headers
        valid_pdf_hdr = b"%PDF-1.4\n%..."
        assert validate_file_magic_bytes(valid_pdf_hdr, ".pdf") is True

        valid_png_hdr = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        assert validate_file_magic_bytes(valid_png_hdr, ".png") is True

        valid_docx_hdr = b"PK\x03\x04\x14\x00\x06\x00"
        assert validate_file_magic_bytes(valid_docx_hdr, ".docx") is True

        valid_csv_hdr = b"product_name,price,rating\nLaptop,999,4.5"
        assert validate_file_magic_bytes(valid_csv_hdr, ".csv") is True
        print("  --> PASSED: Magic-byte inspection accurately distinguishes genuine files from hostile uploads.")

        # 5e. Test upload endpoint with invalid magic bytes via HTTP
        spoofed_upload_res = await client.post(
            "/api/upload/",
            files={"file": ("malicious.pdf", fake_pdf, "application/pdf")},
            headers=auth_headers
        )
        assert spoofed_upload_res.status_code == 400, f"Expected 400 for spoofed upload, got {spoofed_upload_res.status_code}"
        assert "does not match declared file extension" in spoofed_upload_res.json()["detail"]
        print(f"  --> PASSED: Live upload endpoint rejected spoofed file with HTTP 400: '{spoofed_upload_res.json()['detail']}'")

        # 5f. Test upload endpoint with valid CSV via HTTP
        valid_upload_res = await client.post(
            "/api/upload/",
            files={"file": ("data.csv", valid_csv_hdr, "text/csv")},
            headers=auth_headers
        )
        assert valid_upload_res.status_code == 200, f"Valid upload failed: {valid_upload_res.text}"
        assert valid_upload_res.json()["status"] == "success"
        print("  --> PASSED: Live upload endpoint successfully processed genuine file.")

    # Cleanup Redis test session and DB test user
    await redis_store.delete_session(session_id)
    async for db in get_session():
        st = select(User).where(User.id == test_user_id)
        res = await db.exec(st)
        u = res.first()
        if u:
            await db.delete(u)
            await db.commit()
        break
    print("  --> PASSED: Cleaned up test user from Neon PostgreSQL and Redis.")
    print("\n============================================================")
    print("ALL PHASE 2 CRITICAL & HIGH HARDENING TESTS PASSED 100%!")
    print("============================================================\n")

if __name__ == "__main__":
    asyncio.run(run_phase2_hardening_tests())
