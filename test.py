import requests
import json
import sys
import subprocess
import time
import socket
import os

BASE_URL = "http://localhost:8000"

def is_backend_running():
    # Check if port 8000 is open
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', 8000)) == 0

def start_backend_server():
    print("Backend server is not running. Starting it automatically...")
    
    # Path to backend folder
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apps", "backend")
    
    # Locate virtual environment python or uvicorn
    if os.name == 'nt':  # Windows
        uvicorn_path = os.path.join(backend_dir, "venv", "Scripts", "uvicorn.exe")
    else:  # macOS/Linux
        uvicorn_path = os.path.join(backend_dir, "venv", "bin", "uvicorn")
        
    if not os.path.exists(uvicorn_path):
        print(f"[ERROR] Could not find virtual environment uvicorn at {uvicorn_path}")
        print("Please verify your backend is installed correctly in apps/backend/venv")
        sys.exit(1)
        
    # Start uvicorn in a background process
    try:
        process = subprocess.Popen(
            [uvicorn_path, "main:app", "--reload", "--port", "8000"],
            cwd=backend_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("FastAPI backend server launched in background.")
        
        # Wait until port 8000 is open
        retries = 15
        while retries > 0:
            if is_backend_running():
                print("Backend server is ready and responding!")
                return process
            time.sleep(1)
            retries -= 1
            
        print("[ERROR] Timeout waiting for backend server to start.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to launch backend server: {e}")
        sys.exit(1)

def get_guest_token():
    print("Connecting to backend to get guest session token...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/guest")
        response.raise_for_status()
        data = response.json()
        print("Successfully authenticated as guest!")
        return data["access_token"]
    except Exception as e:
        print(f"\n[ERROR] Failed to authenticate: {e}")
        sys.exit(1)

def run_extraction_chat(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    session_id = None
    
    print("\n" + "="*50)
    print("  WEBISCRAP Backend Integration Tester")
    print("="*50)
    
    while True:
        print("\n--- New Extraction Request ---")
        target_url = input("Enter Target URL (e.g. https://books.toscrape.com): ").strip()
        message = input("Describe what you want to extract: ").strip()
        
        if not message:
            print("Extraction prompt cannot be empty.")
            continue
            
        payload = {
            "message": message,
            "target_url": target_url
        }
        if session_id:
            payload["session_id"] = session_id
        
        print("\nSending request to 9-agent backend pipeline...")
        print("This runs the Planner, Browser, Extractor, Cleaner, and Validator agents.")
        print("Please wait...")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat/", 
                json=payload, 
                headers=headers,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            
            # Save session id for subsequent follow-up chats
            session_id = result.get("session_id")
            
            print("\n--- RAW BACKEND RESPONSE ---")
            print(json.dumps(result, indent=2, default=str))
            print("="*50)
            
            # Check for pipeline error
            if result.get("status") == "error":
                print("\n[PIPELINE ERROR]")
                print(result.get("message", "Unknown error"))
                cont = input("\nDo you want to run another query? (y/n): ").strip().lower()
                if cont != 'y':
                    break
                continue
            
            # Print conversation response
            data_payload = result.get("data", {})
            conv_resp = data_payload.get("conversation_response", {})
            
            response_text = ""
            if isinstance(conv_resp, dict):
                response_text = conv_resp.get("response_text", "")
            elif isinstance(conv_resp, str):
                response_text = conv_resp
            else:
                response_text = result.get("message", "")
                
            if response_text:
                print(response_text)
            else:
                print("Extraction complete. Pipeline returned data successfully.")
            
            # Print extracted data if present
            extracted_data = data_payload.get("cleaned_data") or data_payload.get("extracted_data") or (conv_resp.get("filtered_data") if isinstance(conv_resp, dict) else None)
            if extracted_data and isinstance(extracted_data, list):
                print(f"\nExtracted Data ({len(extracted_data)} items):")
                if len(extracted_data) > 0 and isinstance(extracted_data[0], dict):
                    keys = list(extracted_data[0].keys())
                    # Print Header
                    print(" | ".join(keys))
                    print("-" * (sum(len(k) for k in keys) + 3*len(keys)))
                    # Print Rows
                    for row in extracted_data[:10]: # limit to 10 rows
                        print(" | ".join(str(row.get(k, "")) for k in keys))
                    if len(extracted_data) > 10:
                        print(f"... and {len(extracted_data) - 10} more rows.")
            elif isinstance(extracted_data, dict):
                print("\nExtracted Data:")
                print(json.dumps(extracted_data, indent=2))
            
            # Log any steps
            pipeline_steps = result.get("steps")
            if pipeline_steps:
                print("\nPipeline Steps Executed:")
                for step in pipeline_steps:
                    print(f" - {step.get('name')}: {step.get('status')}")
                    
        except Exception as e:
            print(f"\n[ERROR] Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Details: {e.response.text}")
                
        cont = input("\nDo you want to run another query? (y/n): ").strip().lower()
        if cont != 'y':
            break

if __name__ == "__main__":
    backend_proc = None
    if not is_backend_running():
        backend_proc = start_backend_server()
        
    try:
        token = get_guest_token()
        run_extraction_chat(token)
    finally:
        # Keep background server running if we spawned it, or terminate if desired.
        # Usually it's nice to keep it running, but we can print status.
        if backend_proc:
            print("\nBackend server remains running in the background on port 8000.")
