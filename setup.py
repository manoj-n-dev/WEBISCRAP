import subprocess
import sys
import os
import time
from threading import Thread

def run_backend():
    print("Starting FastAPI Backend...")
    # Using shell=True for Windows compatibility with venv scripts if needed
    backend_dir = os.path.join(os.path.dirname(__file__), "apps", "backend")
    
    # Try to use python from active environment, otherwise just use python
    env = os.environ.copy()
    
    try:
        # Install backend dependencies
        print("Installing backend dependencies...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            cwd=backend_dir,
            env=env,
            check=True
        )
        
        print("Starting FastAPI server...")
        subprocess.run(
            [sys.executable, "main.py"],
            cwd=backend_dir,
            env=env,
            check=True
        )
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Backend process exited: {e}")

def run_frontend():
    print("Starting Next.js Frontend...")
    frontend_dir = os.path.join(os.path.dirname(__file__), "apps", "frontend")
    
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    
    try:
        # Check if node_modules exists, if not run npm install
        if not os.path.exists(os.path.join(frontend_dir, "node_modules")):
            print("Installing frontend dependencies...")
            subprocess.run([npm_cmd, "install"], cwd=frontend_dir, check=True)
            
        subprocess.run(
            [npm_cmd, "run", "dev"],
            cwd=frontend_dir,
            check=True
        )
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Frontend process exited: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("Starting WEBISCRAP Platform")
    print("=" * 50)
    
    # Start threads
    backend_thread = Thread(target=run_backend)
    frontend_thread = Thread(target=run_frontend)
    
    # Set as daemon so they exit when main script exits
    backend_thread.daemon = True
    frontend_thread.daemon = True
    
    backend_thread.start()
    
    # Give backend a small head start
    time.sleep(2)
    
    frontend_thread.start()
    
    print("\n[+] Both services are starting.")
    print("[+] Backend API will be available at: http://localhost:8000")
    print("[+] Frontend UI will be available at: http://localhost:3000")
    print("[+] Press Ctrl+C to stop both services.\n")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
        sys.exit(0)
