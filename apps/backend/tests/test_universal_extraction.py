import asyncio
import sys
import os
import uuid
import httpx
from datetime import datetime

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from main import app
from sqlmodel import select
from database.connection import get_session
from models.user import User
from memory.session_store import redis_store

async def run_universal_test():
    test_id = uuid.uuid4().hex[:8]
    test_email = f"universal_tester_{test_id}@example.com"
    test_password = "Password123!"
    created_user_ids = []

    print("\n==========================================")
    print("STARTING UNIVERSAL EXTRACTION PLATFORM TESTS")
    print("Testing Non-E-Commerce URLs, Document Uploads, Clean & Exports")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("==========================================\n")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=120.0) as client:
        # Step 1: User Auth
        print("[TEST 1] Registering and Authenticating Test User...")
        reg_res = await client.post("/api/auth/register", json={
            "email": test_email,
            "password": test_password,
            "full_name": f"Universal Tester {test_id}"
        })
        assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
        user_id = reg_res.json()["id"]
        created_user_ids.append(user_id)

        login_res = await client.post("/api/auth/login", data={
            "username": test_email,
            "password": test_password
        })
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"  --> User authenticated: {test_email}")

        # Step 2: Test Document Context Extraction (PDF / DOCX simulation)
        print("\n[TEST 2] Testing Document Upload Extraction Pipeline (No URL / Non-Web Source)...")
        doc_session_id = f"test_doc_session_{test_id}"
        
        # Seed an uploaded document context in Redis (simulating a parsed PDF/DOCX)
        sample_doc_content = """
        WEBISCRAP System Architecture Report
        
        Component: Multi-Agent Orchestrator | Lead: Backend Core | Status: Active | Version: 2.4.0
        Component: Universal Extractor Engine | Lead: AI Module | Status: Production | Version: 3.1.0
        Component: Neon PostgreSQL Database | Lead: Data Layer | Status: Operational | Version: 15.0
        Component: Upstash Redis State Cache | Lead: Memory Layer | Status: Operational | Version: 7.2
        Component: Next.js Frontend Dashboard | Lead: UI Team | Status: Ready | Version: 14.2
        """
        await redis_store.set_session_owner(doc_session_id, str(user_id))
        await redis_store.add_user_session(str(user_id), doc_session_id)
        await redis_store.save_uploaded_context(
            session_id=doc_session_id,
            file_id="arch_report_01",
            text=sample_doc_content
        )
        print("  --> Seeded parsed document into session memory")

        # Trigger chat pipeline with uploaded context
        doc_chat_res = await client.post("/api/chat/", json={
            "message": "Extract all components with lead, status, and version from the uploaded report",
            "target_url": "", # No URL! Pure document extraction
            "session_id": doc_session_id
        }, headers=headers)
        
        assert doc_chat_res.status_code == 200, f"Document extraction failed: {doc_chat_res.text}"
        doc_result = doc_chat_res.json()
        raw_doc_data = doc_result.get("data", [])
        if isinstance(raw_doc_data, dict):
            doc_extracted = raw_doc_data.get("cleaned_data") or raw_doc_data.get("extracted_data") or []
        else:
            doc_extracted = raw_doc_data
        print(f"  --> Document Extraction Succeeded! Extracted {len(doc_extracted)} records.")
        if doc_extracted:
            print(f"  --> Sample record: {doc_extracted[0]}")

        # Verify Dataset View for Document
        doc_data_res = await client.get(f"/api/chat/{doc_session_id}/data", headers=headers)
        assert doc_data_res.status_code == 200, f"Dataset view failed: {doc_data_res.text}"
        print(f"  --> Dataset View verified for document-extracted data!")

        # Step 3: Test Multi-Format Exports on Document Extraction
        print("\n[TEST 3] Verifying Multi-Format Exports on Universal Data...")
        for fmt in ["csv", "excel", "json", "markdown"]:
            exp_res = await client.get(f"/api/export/{fmt}?session_id={doc_session_id}", headers=headers)
            assert exp_res.status_code == 200, f"Export {fmt} failed with {exp_res.status_code}"
            assert len(exp_res.content) > 0, f"Export {fmt} content is empty"
            print(f"  --> Export '{fmt}' verified ({len(exp_res.content)} bytes)")

        # Step 4: Test Non-E-Commerce URL Extraction (e.g. Wikipedia / Articles)
        print("\n[TEST 4] Testing Universal Web Extraction (Wikipedia / Educational)...")
        wiki_session_id = f"test_wiki_session_{test_id}"
        await redis_store.set_session_owner(wiki_session_id, str(user_id))
        await redis_store.add_user_session(str(user_id), wiki_session_id)
        wiki_url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
        
        wiki_chat_res = await client.post("/api/chat/", json={
            "message": "Extract section titles and descriptions from Python programming language page",
            "target_url": wiki_url,
            "session_id": wiki_session_id
        }, headers=headers)
        
        assert wiki_chat_res.status_code == 200, f"Wiki chat failed: {wiki_chat_res.text}"
        wiki_result = wiki_chat_res.json()
        raw_wiki_data = wiki_result.get("data", [])
        if isinstance(raw_wiki_data, dict):
            wiki_data = raw_wiki_data.get("cleaned_data") or raw_wiki_data.get("extracted_data") or []
        else:
            wiki_data = raw_wiki_data
        print(f"  --> Universal Web Extraction Succeeded! Extracted {len(wiki_data)} records.")
        if wiki_data:
            print(f"  --> Sample Wiki record: {wiki_data[0]}")
            # Ensure no Flipkart or Lenovo remnants exist!
            wiki_str = str(wiki_data).lower()
            assert "lenovo loq" not in wiki_str, "FAIL: Found hardcoded Lenovo LOQ in universal extraction!"
            assert "flipkart.com" not in wiki_str, "FAIL: Found hardcoded flipkart.com in universal extraction!"
            print("  --> PASSED: Clean extraction verified free of any Flipkart/Lenovo hardcoded values!")

        # Step 5: Test Sidebar Sessions
        print("\n[TEST 5] Verifying Sidebar Sessions Contains Both Sessions...")
        sessions_res = await client.get("/api/chat/sessions", headers=headers)
        assert sessions_res.status_code == 200
        active_sessions = sessions_res.json().get("sessions", [])
        active_ids = [s.get("id") if isinstance(s, dict) else s for s in active_sessions]
        assert doc_session_id in active_ids, f"Doc session {doc_session_id} not in sidebar: {active_ids}"
        assert wiki_session_id in active_ids, f"Wiki session {wiki_session_id} not in sidebar: {active_ids}"
        print(f"  --> PASSED: Both document and web extraction sessions visible in sidebar!")

        # Step 6: Cleanup Test Data
        print("\n[TEST 6] Cleaning up test users and sessions...")
        async for db in get_session():
            for uid in created_user_ids:
                st = select(User).where(User.id == uid)
                res = await db.exec(st)
                u = res.first()
                if u:
                    await db.delete(u)
            await db.commit()
            break
        await redis_store.delete_session(doc_session_id)
        await redis_store.delete_session(wiki_session_id)
        print("  --> Test data cleaned up successfully.")

    print("\n==========================================")
    print("ALL UNIVERSAL EXTRACTION PLATFORM TESTS PASSED 100%!")
    print("==========================================\n")

if __name__ == "__main__":
    asyncio.run(run_universal_test())
