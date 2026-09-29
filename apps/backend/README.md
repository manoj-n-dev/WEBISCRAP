# WEBISCRAP Backend API & Worker Engine

FastAPI asynchronous REST API and autonomous multi-agent pipeline engine powering WEBISCRAP.

---

## 💻 Tech Stack

- **Framework:** FastAPI (Python 3.11+, async/await, Uvicorn)
- **Database ORM:** SQLModel + SQLAlchemy (asyncpg)
- **Primary Database:** PostgreSQL on Neon Serverless
- **Session Memory & Cache:** Upstash Redis with `z1` zlib payload compression
- **Headless Browser:** Playwright (Chromium) with SSRF and DNS-rebinding interception
- **AI Engine:** Groq (LLaMA 3 70B) with automatic multi-key pool rotation and per-model cooldown
- **Authentication:** In-memory access tokens, HttpOnly secure refresh cookies, Google OAuth with cryptographic nonce verification
- **Document Parsers:** PyPDF, python-docx, openpyxl, pandas, pytesseract (OCR)

---

## 📁 Directory Structure

```
apps/backend/
├── agents/             # 9-Agent Pipeline (orchestrator, planner, analyzer, browser, extractor, ...)
├── ai/                 # Groq client, dynamic key rotation pool, retry backoff
├── api/                # REST endpoints (/api/auth, /api/chat, /api/scrape, /api/export, /api/upload)
├── auth/               # JWT token utilities, Google OAuth, Brevo HTTPS email service
├── core/               # App configuration, rate limiter, structured audit logger, health probes
├── database/           # Async PostgreSQL engine, connection pooling, lifecycle management
├── memory/             # Redis session store (z1 compression, JTI blacklist, atomic claims)
├── models/             # SQLModel database schemas (User, Session, Token)
├── parsers/            # Multi-format document parsers (PDF, DOCX, CSV, Excel, OCR)
├── prompts/            # Specialized system prompts per agent
├── tests/              # Comprehensive test suites (84 tests, SSRF, auth, pipeline, parsers)
├── workers/            # Durable Redis background scrape worker
├── main.py             # Application entrypoint & middleware registration
└── requirements.txt    # Pinned production Python dependencies
```

---

## 🚀 Getting Started

### 1. Environment Setup

```bash
cd apps/backend
python -m venv venv

# Windows:
.\venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

### 2. Configuration

Ensure environment variables are configured in `.env` (or project root `.env`):

```env
GROQ_API_KEYS=gsk_key1,gsk_key2
DATABASE_URL=postgresql+asyncpg://user:pass@host/db?ssl=require
REDIS_URL=rediss://default:pass@host:6379
JWT_SECRET=your-32-character-secret-key-here
FRONTEND_URL=http://localhost:3000
```

### 3. Run the Development Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive OpenAPI documentation is available at `http://localhost:8000/docs` in development mode.

---

## 🧪 Running Tests

```bash
# Run the complete test suite
python tests/run_all_tests.py

# Or run specific test modules
python -m unittest tests.test_ssrf_and_proxy -v
python -m unittest tests.test_api_endpoints -v
python -m unittest tests.test_private_url_handling -v
```
