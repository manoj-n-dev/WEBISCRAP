import requests
import time

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def pr(name, result, ok):
    tag = "[PASS]" if ok else "[FAIL]"
    print(f"{tag} {name}: {result}")

# =====================
# BACKEND API TESTS
# =====================
print("=" * 60)
print("BACKEND API TESTS")
print("=" * 60)

# 1. Guest Login
try:
    res = requests.post(f"{BASE_URL}/api/auth/guest", timeout=15)
    guest_token = res.json().get("access_token")
    pr("Guest Login", f"Token received ({len(guest_token)} chars)" if guest_token else "No token", bool(guest_token))
except Exception as e:
    pr("Guest Login", str(e), False)
    guest_token = None

# 2. Register with STRONG password (meets new validation)
email = f"fulltest_{int(time.time())}@example.com"
strong_password = "StrongPass1"
try:
    res = requests.post(f"{BASE_URL}/api/auth/register", json={"email": email, "password": strong_password})
    pr("Register (strong pwd)", f"Status {res.status_code} - {res.json().get('email', res.text[:80])}", res.status_code == 200)
except Exception as e:
    pr("Register (strong pwd)", str(e), False)

# 3. Register with WEAK password (should fail)
try:
    res = requests.post(f"{BASE_URL}/api/auth/register", json={"email": "weak@test.com", "password": "123"})
    pr("Register (weak pwd rejected)", f"Status {res.status_code}", res.status_code == 400)
except Exception as e:
    pr("Register (weak pwd rejected)", str(e), False)

# 4. Login (Email/Password)
try:
    res = requests.post(f"{BASE_URL}/api/auth/login", data={"username": email, "password": strong_password})
    user_token = res.json().get("access_token")
    pr("Login (Email/Password)", f"Token received ({len(user_token)} chars)" if user_token else "No token", bool(user_token))
except Exception as e:
    pr("Login (Email/Password)", str(e), False)
    user_token = None

# 5. Extraction Pipeline
sid = None
if guest_token:
    try:
        headers = {"Authorization": f"Bearer {guest_token}"}
        payload = {"message": "https://example.com extract the main heading", "target_url": "https://example.com"}
        res = requests.post(f"{BASE_URL}/api/chat/", json=payload, headers=headers, timeout=30)
        sid = res.json().get("session_id")
        pr("Extraction Pipeline", f"Session {sid}" if sid else res.text[:80], res.status_code == 200)
    except Exception as e:
        pr("Extraction Pipeline", str(e), False)

# 6. Health / Docs endpoint
try:
    res = requests.get(f"{BASE_URL}/docs")
    pr("Swagger Docs (/docs)", f"Status {res.status_code}", res.status_code == 200)
except Exception as e:
    pr("Swagger Docs (/docs)", str(e), False)

# =====================
# FRONTEND PAGE TESTS
# =====================
print()
print("=" * 60)
print("FRONTEND PAGE TESTS")
print("=" * 60)

pages = {
    "Landing Page (/)": "/",
    "Login Page (/login)": "/login",
    "Signup Page (/signup)": "/signup",
    "Terms Page (/terms)": "/terms",
    "Privacy Page (/privacy)": "/privacy",
}

for name, path in pages.items():
    try:
        res = requests.get(f"{FRONTEND_URL}{path}", timeout=10)
        has_content = len(res.text) > 500
        pr(name, f"Status {res.status_code}, Size {len(res.text)} bytes", res.status_code == 200 and has_content)
    except Exception as e:
        pr(name, str(e), False)

# Check chat page (requires session ID)
try:
    res = requests.get(f"{FRONTEND_URL}/chat/new", timeout=10)
    pr("Chat Page (/chat/new)", f"Status {res.status_code}, Size {len(res.text)} bytes", res.status_code == 200)
except Exception as e:
    pr("Chat Page (/chat/new)", str(e), False)

# Check dataset page
if sid:
    try:
        res = requests.get(f"{FRONTEND_URL}/dataset/{sid}", timeout=10)
        pr(f"Dataset Page (/dataset/{sid[:8]}...)", f"Status {res.status_code}, Size {len(res.text)} bytes", res.status_code == 200)
    except Exception as e:
        pr("Dataset Page", str(e), False)

print()
print("=" * 60)
print("CONTENT VERIFICATION")
print("=" * 60)

# Verify landing page has key elements
try:
    res = requests.get(f"{FRONTEND_URL}/")
    html = res.text.lower()
    checks = {
        "Landing: Has title": "webiscrap" in html,
        "Landing: Has Sign In link": "sign in" in html or "signin" in html or "/login" in html,
        "Landing: Has View Examples": "view examples" in html or "examples" in html,
    }
    for name, passed in checks.items():
        pr(name, "Found" if passed else "Not found", passed)
except Exception as e:
    pr("Landing Content Check", str(e), False)

# Verify login page has Google and Phone buttons
try:
    res = requests.get(f"{FRONTEND_URL}/login")
    html = res.text.lower()
    checks = {
        "Login: Has Google button": "google" in html,
        "Login: Has Phone OTP button": "phone" in html,
        "Login: Has signup link": "sign up" in html or "/signup" in html,
        "Login: Has password field": "password" in html,
    }
    for name, passed in checks.items():
        pr(name, "Found" if passed else "Not found", passed)
except Exception as e:
    pr("Login Content Check", str(e), False)

# Verify dynamic copyright year
try:
    res = requests.get(f"{FRONTEND_URL}/")
    current_year = str(time.localtime().tm_year)
    pr(f"Landing: Copyright year ({current_year})", "Found" if current_year in res.text else "Not found", current_year in res.text)
except Exception as e:
    pr("Copyright Year Check", str(e), False)

print()
print("=" * 60)
print("TEST COMPLETE")
print("=" * 60)
