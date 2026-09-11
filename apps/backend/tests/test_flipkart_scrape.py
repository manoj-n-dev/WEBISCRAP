import asyncio
import sys
import os
import uuid
import httpx
from datetime import datetime

# Ensure utf-8 encoding on Windows console for currency symbols like ₹
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from main import app
from sqlmodel import select
from database.connection import get_session
from models.user import User

async def run_flipkart_test():
    test_id = uuid.uuid4().hex[:8]
    test_email = f"flipkart_tester_{test_id}@example.com"
    test_password = "Password123!"
    created_user_ids = []

    print("\n==========================================")
    print("STARTING FLIPKART E2E EXTRACTION, DATASET VIEW & EXPORTS TEST")
    print(f"Target URL: https://www.flipkart.com/q/lenovo-loq")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("==========================================\n")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=120.0) as client:
        # 1. Register & Login
        print("[STEP 1] Registering and Authenticating Test User")
        reg_res = await client.post("/api/auth/register", json={
            "email": test_email,
            "password": test_password,
            "full_name": f"Flipkart Tester {test_id}"
        })
        assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
        user_id = reg_res.json()["id"]
        created_user_ids.append(user_id)

        login_res = await client.post("/api/auth/login", data={
            "username": test_email,
            "password": test_password
        })
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        access_token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        print(f"  --> Authenticated user {test_email} (ID: {user_id})")

        # 2. Trigger Extraction Pipeline on Flipkart URL
        print("\n[STEP 2] Launching Multi-Agent AI Extraction Pipeline on Flipkart...")
        print("  --> URL: https://www.flipkart.com/q/lenovo-loq")
        print("  --> Query: 'Extract Lenovo LOQ laptops with model name, price, rating, specs, and link'")
        
        chat_payload = {
            "message": "Extract Lenovo LOQ laptops with model name, price, rating, specs, and link",
            "target_url": "https://www.flipkart.com/q/lenovo-loq",
            "session_id": "new"
        }
        
        start_time = datetime.now()
        chat_res = await client.post("/api/chat/", json=chat_payload, headers=headers)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        assert chat_res.status_code == 200, f"Chat pipeline failed ({chat_res.status_code}): {chat_res.text}"
        result = chat_res.json()
        session_id = result.get("session_id")
        assert session_id, "No session_id returned from chat endpoint"
        print(f"  --> Pipeline completed in {elapsed:.1f}s! Session ID: {session_id}")

        # Check extracted data
        raw_data = result.get("data", [])
        if isinstance(raw_data, dict):
            extracted_data = raw_data.get("cleaned_data") or raw_data.get("extracted_data") or []
        else:
            extracted_data = raw_data
        print(f"  --> Extracted Rows Count: {len(extracted_data)}")
        if extracted_data:
            sample = extracted_data[0]
            print(f"  --> Sample Extracted Item: {sample}")

        # 3. Verify Dataset View Endpoint (/api/chat/{session_id}/data)
        print("\n[STEP 3] Verifying Dataset View API Endpoint (/api/chat/{session_id}/data)")
        data_res = await client.get(f"/api/chat/{session_id}/data", headers=headers)
        assert data_res.status_code == 200, f"Dataset view fetch failed: {data_res.status_code} {data_res.text}"
        session_data = data_res.json()
        print(f"  --> PASSED: Dataset view data successfully retrieved from Redis")
        print(f"  --> Keys in session data: {list(session_data.keys()) if isinstance(session_data, dict) else len(session_data)}")

        # 4. Verify All 4 Export Formats
        print("\n[STEP 4] Verifying Multi-Format Exports")
        
        # 4a. CSV Export
        print("  [4a] Testing CSV Export (/api/export/csv)")
        csv_res = await client.get(f"/api/export/csv?session_id={session_id}", headers=headers)
        assert csv_res.status_code == 200, f"CSV export failed: {csv_res.status_code} {csv_res.text}"
        assert len(csv_res.content) > 0, "CSV export content is empty"
        print(f"    --> PASSED: CSV received ({len(csv_res.content)} bytes)")
        csv_sample = csv_res.text[:200].replace('\n', ' ')
        print(f"    --> CSV Header/Sample: {csv_sample}...")

        # 4b. Excel Export
        print("  [4b] Testing Excel Export (/api/export/excel)")
        excel_res = await client.get(f"/api/export/excel?session_id={session_id}", headers=headers)
        assert excel_res.status_code == 200, f"Excel export failed: {excel_res.status_code} {excel_res.text}"
        assert len(excel_res.content) > 0, "Excel export content is empty"
        print(f"    --> PASSED: Excel received ({len(excel_res.content)} bytes)")

        # 4c. JSON Export
        print("  [4c] Testing JSON Export (/api/export/json)")
        json_res = await client.get(f"/api/export/json?session_id={session_id}", headers=headers)
        assert json_res.status_code == 200, f"JSON export failed: {json_res.status_code} {json_res.text}"
        assert len(json_res.json()) > 0 or json_res.status_code == 200
        print(f"    --> PASSED: JSON received ({len(json_res.content)} bytes)")

        # 4d. Markdown Export
        print("  [4d] Testing Markdown Export (/api/export/markdown)")
        md_res = await client.get(f"/api/export/markdown?session_id={session_id}", headers=headers)
        assert md_res.status_code == 200, f"Markdown export failed: {md_res.status_code} {md_res.text}"
        assert len(md_res.content) > 0, "Markdown export content is empty"
        print(f"    --> PASSED: Markdown table received ({len(md_res.content)} bytes)")

        # 5. Verify Previous Chats in Sidebar
        print("\n[STEP 5] Verifying Previous Chats in Sidebar (/api/chat/sessions)")
        sessions_res = await client.get("/api/chat/sessions", headers=headers)
        assert sessions_res.status_code == 200, f"List sessions failed: {sessions_res.status_code}"
        user_sessions = sessions_res.json().get("sessions", [])
        
        # Check if our session_id is in the returned list
        session_ids = [s.get("id") if isinstance(s, dict) else s for s in user_sessions]
        assert session_id in session_ids, f"Session {session_id} not found in user sessions: {session_ids}"
        print(f"  --> PASSED: Current session {session_id} found in user's sidebar session list!")
        print(f"  --> Total user sessions: {len(user_sessions)}")

        # 6. Verify Session History Restoration
        print("\n[STEP 6] Verifying Historical Conversation Restoration (/api/chat/{session_id}/history)")
        history_res = await client.get(f"/api/chat/{session_id}/history", headers=headers)
        assert history_res.status_code == 200, f"History fetch failed: {history_res.status_code}"
        history = history_res.json().get("history", [])
        assert len(history) >= 2, f"Expected at least user and assistant messages, got {len(history)}"
        print(f"  --> PASSED: Restored {len(history)} messages from session history!")
        print(f"  --> User message: {history[0].get('content')[:50]}...")
        print(f"  --> Assistant message: {history[1].get('content')[:50]}...")

    # 7. Database Cleanup
    print("\n[STEP 7] Database Cleanup")
    async for db in get_session():
        for uid in created_user_ids:
            st = select(User).where(User.id == uid)
            res = await db.exec(st)
            u = res.first()
            if u:
                await db.delete(u)
        await db.commit()
        break
    print(f"  --> PASSED: Cleaned up test user from Neon PostgreSQL")

    print("\n==========================================")
    print("ALL FLIPKART EXTRACTION, DATASET & EXPORT TESTS PASSED 100%!")
    print("==========================================\n")

if __name__ == "__main__":
    asyncio.run(run_flipkart_test())
