# WEBISCRAP 🕸️

<div align="center">
  <table>
    <tr>
      <td align="center" style="padding: 10px;">
        <img src="https://raw.githubusercontent.com/manoj-n-dev/WEBISCRAP/main/apps/frontend/public/assets/branding-logo.png" alt="WEBISCRAP Branding Logo" width="300" />
        <br />
        <strong>Branding Logo</strong>
      </td>
      <td align="center" style="padding: 10px;">
        <img src="https://raw.githubusercontent.com/manoj-n-dev/WEBISCRAP/main/apps/frontend/public/assets/inner-logo.png" alt="WEBISCRAP Inner Logo" width="150" />
        <br />
        <strong>Inner Logo</strong>
      </td>
    </tr>
  </table>
</div>

### *Extract Anything. Ask Naturally. Export Instantly.*

**WEBISCRAP** is a conversational, AI-powered web data extraction platform that replaces traditional scraping workflows — CSS selectors, XPath, brittle scripts — with plain natural language. Paste a URL, describe what you want in your own words (English, Telugu, Hindi, Tamil, Hinglish, or mixed), and a team of nine specialized AI agents plans, browses, extracts, cleans, validates, and exports the data for you.

Not a scraping tool. Not a selector builder. **A research assistant that happens to understand websites.**

![License: All Rights Reserved](https://img.shields.io/badge/License-All%20Rights%20Reserved-red?style=flat-square)
![Made in India](https://img.shields.io/badge/Made%20in-India%20%F0%9F%87%AE%F0%9F%87%B3-ff6b35?style=flat-square)
![Status](https://img.shields.io/badge/Status-Complete-00ff78?style=flat-square)

> *"Paste a link. Ask in your own words. Get your data."*

---

## 📑 Table of Contents

- [Current Status](#-current-status)
- [Overview](#-overview)
- [System Architecture (Pin-to-Pin)](#-system-architecture-pin-to-pin)
  - [1. Frontend (Next.js 16)](#1-frontend-nextjs-16)
  - [2. Backend (FastAPI)](#2-backend-fastapi)
  - [3. Database & Caching](#3-database--caching)
- [The 9-Agent AI Pipeline](#-the-9-agent-ai-pipeline)
- [Security & Production Hardening](#-security--production-hardening)
- [Comprehensive Code Audit & Verification Matrix](#️-comprehensive-code-audit--verification-matrix)
- [Package Architecture & Module Resolution](#️-package-architecture--module-resolution)
- [Folder Structure](#-folder-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#️-configuration)
- [Roadmap](#️-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Team](#-team)

---

## 🚀 Current Status

**Where we are:**
- ✅ The **FastAPI Backend** is 100% complete, hardened, and verified with zero import errors or circular module shadowing.
- ✅ The **9-Agent AI Pipeline** runs exclusively on **Groq** (LLaMA 3.3 70B) with automatic key rotation and failover.
- ✅ **Authentication**: Email/Password, Google OAuth, Firebase Phone OTP, and Guest Mode. Access tokens are stored strictly **in-memory** (XSS protection) with automatic silent refresh via secure `httpOnly` cookies.
- ✅ **Token Security**: Refresh token rotation automatically blacklists old JTIs in Redis to prevent reuse attacks.
- ✅ **10-key rotation** with automatic failover, cooldown, and load balancing for Groq.
- ✅ Successfully tested on both **static** (HackerNews) and **dynamic/JS** (Quotes to Scrape) websites using Playwright.
- ✅ **Frontend UI** fully built in Next.js 16 (Turbopack) with a highly customized cinematic HUD glassmorphism design.
- ✅ **Production & Security Hardening**:
  - Fail-closed IDOR session authorization across all endpoints.
  - SSRF protection with DNS-rebinding TOCTOU mitigation via Playwright request rewriting.
  - Reverse-proxy-aware sliding-window IP rate limiting (`TRUST_PROXY_HEADERS`) and audit logging middleware.
  - Registration duplicate-email race condition handling with graceful 400 responses.
  - Upload context persistence associating document text with active chat sessions in Redis.
  - Automated Playwright browser installation built directly into `setup.py`.
- ✅ **Dataset View Fix & High-Reliability Data Binding**:
  - Direct route-keyed session fetching on navigation eliminating cross-session Zustand store masking.
  - Safe fallback resolution on "Open in Dataset View" navigation ensuring valid UUID routing.
  - Robust payload unwrapping supporting both flat and nested backend dictionary structures (`cleaned_data`, `data.cleaned_data`, `extracted_data`, arrays).
  - Safe TanStack Table column accessors (`accessorFn`) and cell formatting for nested objects and nullish values.
- ✅ **Verified Dependency & Environment Cleanliness**:
  - Clean Python virtual environment (`apps/backend/venv`) with 100% passing test suite (37/37 tests).
  - Clean Next.js 16 build (`npm run build`) with zero TypeScript errors.
  - Clean repository with zero uncommitted or lingering runtime artifacts in `uploads/` or `exports/`.
- ✅ **Audit 3 Bug Report Fixes Completed**: All critical (C1-C6), high (H1-H6), medium (M1-M7), and low (L1-L3) issues resolved and verified.

---

## ⚡ Overview

WEBISCRAP is built on one idea —

> **Scraping is a side effect of conversation, not the main interaction.**

There's no dashboard, no manual selector builder, no scrape-configuration screen. The chat interface **is** the product.

```
"Extract all laptop names, prices, ratings, and images from this site"

  Planner Agent        →  Understands intent, builds a plan
  Website Analyzer     →  Reads the DOM, finds repeating structures
  Browser Automation   →  Renders JS-heavy pages with Playwright
  Extraction Agent     →  Pulls the requested fields
  Cleaning Agent        →  Normalizes and dedupes
  Validation Agent     →  Scores confidence, flags gaps

  Structured table + export options → Delivered in chat. Done.
```

**No selectors. No scripts. No re-scraping for follow-up questions.**

---

## 🏗️ System Architecture (Pin-to-Pin)

WEBISCRAP is divided into a strictly uncoupled Backend API and a Client-Side Rendered frontend.

### 1. Frontend (Next.js 16)
- **Framework**: Next.js 16 App Router using Turbopack for compilation.
- **State Management**: `Zustand` (`src/lib/store/chat.ts`) handles the global session state. When a user pastes a URL, it stores the message, assigns a temporary placeholder message for the AI response, marks the status as "running", and fires off the async fetch request. When the backend completes, Zustand updates the state to "completed" and injects the resulting JSON array.
- **Styling**: Tailwind CSS v4 configured exclusively through CSS variables mapped in `globals.css`. We use a custom "cinematic HUD" glassmorphism theme characterized by `signal-500` accents, hairline borders (`bg-hair`), and backdrop blurs (`backdrop-blur-md`).
- **Data Fetching**: A custom `ApiClient` (`src/lib/api/client.ts`) handles REST communications with automatic refresh-token retry on 401s. The extraction endpoint (`POST /api/chat/`) accepts JSON to submit the prompt and target URL, passing along the `Authorization: Bearer <token>` in headers.

### 2. Backend (FastAPI)
- **Framework**: FastAPI (Python 3.11+). Runs asynchronously using Uvicorn.
- **Authentication**: JWT-based auth (`api/auth_routes.py`). Passwords are hashed with `passlib` (bcrypt). Includes password strength validation (min 8 chars, 1 uppercase, 1 number), refresh token rotation via `/api/auth/refresh` with JTI revocation, in-memory client storage, and guest mode issuing anonymous JWTs.
- **Middleware**: 
  - `AuditLoggingMiddleware`: Logs proxy-aware client IP, endpoint, response time, and HTTP status of every incoming request.
  - `CORSMiddleware`: Locked down to the `FRONTEND_URL` environment variable to prevent cross-origin abuse.
- **Rate Limiting**: Custom Redis-backed Sliding Window rate limiter (`core/rate_limit.py`). Automatically prevents LLM abuse by throttling IPs to a customizable limit (default 10 requests/minute) with reverse-proxy header support.

### 3. Database & Caching
- **Database (PostgreSQL)**: Managed via Neon. Mapped via `SQLModel` and `SQLAlchemy`. Stores `User` records, hashed passwords, and OAuth IDs. Timestamps use timezone-aware UTC datetime.
- **Caching (Redis)**: Managed via Upstash. Redis powers core system workflows:
  1. **Rate Limiting**: Sliding window token bucket.
  2. **Session Memory**: Once an extraction is completed, the resulting JSON schema is cached in Redis using the `session_id`. When a user asks a follow-up question (e.g. "sort by price"), the memory agent retrieves the data directly from Redis, bypassing the entire scraping pipeline.
  3. **Pipeline Progress**: Live step-by-step progress tracking for the frontend `PipelineStrip`.
  4. **JTI Blacklist**: Revoked refresh tokens for secure token rotation.
  5. **Uploaded Document Context**: Associated document text for active extraction sessions.

---

## 🧠 The 9-Agent AI Pipeline

The beating heart of WEBISCRAP is the Orchestrator (`apps/backend/agents/orchestrator.py`), which passes state across 9 specialized AI Agents. Every agent calls the Groq API (LLaMA 3 70B) utilizing a 10-key rotation pool (`ai.key_manager`) to prevent rate limits.

| # | Agent | Role | What It Does (Technical Depth) |
|---|-------|------|---------------|
| 1 | 🧭 **Planner Agent** | Orchestrator | Interprets intent using prompt engineering. Decides if a new scrape is needed or if this is a follow-up query against the cache. Outputs a JSON workflow plan. |
| 2 | 🔬 **Website Analyzer Agent** | Structure | Analyzes raw DOM/HTML (minified). It detects repeating `<li>`, `<tr>`, or `<div>` card layouts to determine where the data lies. |
| 3 | 🌐 **Browser Automation Agent** | Automation | Uses `Playwright` to spawn a headless Chromium instance. It navigates to the URL, waits for network idle, scrolls to the bottom to trigger lazy-loaded JS elements, and captures the final rendered HTML. Implements DNS-rebinding TOCTOU mitigation and SSRF defenses. The HTML is passed through a minifier to strip `<script>`, `<style>`, and SVG tags to fit within context. |
| 4 | 📦 **Extraction Agent** | Extraction | Receives the minified HTML and the Planner's field list. Forces a `json_object` response format via the LLM to guarantee structured output matching the requested schema. |
| 5 | 🧹 **Cleaning Agent** | Data Quality | A post-processing LLM pass. Dedupes identical rows, normalizes currencies/dates, and resolves relative URLs to absolute URLs. |
| 6 | ✅ **Validation Agent** | Trust | Compares output against schema. Calculates a `confidence_score` (0.0 to 1.0) and flags missing/null fields. Surfaced live in the dataset view. |
| 7 | 🧠 **Memory Agent** | Session Memory | `agents/memory_agent.py`. Saves validated JSON to Redis (`session_data:{id}`). For follow-ups, retrieves cached dataset. |
| 8 | 💬 **Conversation Agent** | Follow-ups | Takes follow-up natural language queries, hoists export/filter parameters, and prompts the LLM to filter, sort, or modify the JSON. |
| 9 | 📤 **Export Agent** | Output | Translates JSON array into raw string formats (CSV, Excel, JSON, Markdown). Sanitizes formula injections. |

---

## 🔒 Security & Production Hardening

- **In-Memory Access Tokens (XSS Mitigation)**: Access tokens are stored exclusively in client memory, while refresh tokens remain in secure `httpOnly`, `sameSite: lax` cookies. Page refreshes seamlessly use silent refresh (`/api/auth/refresh`).
- **Refresh Token Blacklisting**: During refresh token rotation, the old token's JTI is revoked in Redis via `blacklist_jti()` for its remaining lifetime, preventing replay attacks.
- **Fail-Closed IDOR Authorization**: Endpoints verify session ownership defensively (`if not owner_id or owner_id != current_user.id`), denying access to expired or unmapped ownership records.
- **SSRF & DNS Rebinding Defenses**: Playwright intercepts all outgoing requests, resolves the host IP, validates against private/internal/cloud metadata ranges, and rewrites the request URL to the validated literal IP while preserving the original `Host` header.
- **Reverse-Proxy Awareness**: Rate limiting and audit logging read real client IPs via `TRUST_PROXY_HEADERS`, supporting deployments behind Vercel, Render, or custom reverse proxies.
- **Key Rotation**: `apps/backend/ai/key_manager.py` manages a round-robin rotation pool across all keys provided in `GROQ_API_KEYS`. If a key hits a 429 Rate Limit, it enters a 60-second cooldown and the next key is tried automatically.
- **Audit Logs**: Every API request is tracked by `AuditLoggingMiddleware` with proxy-resolved IP, endpoint, response time, and status.
- **Strict CORS**: `allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"]` with credentials allowed safely.
- **Upload Hardening & Association**: File uploads are restricted to 20MB max and an allowlist of extensions (`.pdf`, `.docx`, `.csv`, `.png`, `.jpg`, `.jpeg`). Uploaded text is saved directly to the active session context in Redis.
- **Password Strength Validation**: Server-side enforcement of minimum 8 characters, at least 1 uppercase letter, and at least 1 number.

---

## 🛡️ Comprehensive Code Audit & Verification Matrix

WEBISCRAP underwent a full security and architectural audit across both backend and frontend. All 17 identified issues (Critical, High, and Medium) have been remediated, tested, and verified:

| ID | Severity | Area | Problem | Resolution |
|:---|:---:|:---|:---|:---|
| **C1** | 🔴 Critical | `orchestrator.py` | Missing `redis_store` import causing `NameError` on pipeline execution. | Correctly imported `redis_store` and verified all progress setex and cleanup call sites. |
| **C2** | 🔴 Critical | `session_store.py` | `RedisStore` had no `.redis` attribute (only `.redis_client`), breaking progress, JTI blacklist, and token refresh. | Added `@property redis` returning `redis_client`, ensured auto-connect on all attribute calls. |
| **C3** | 🔴 Critical | `chat.py` / `session_store.py` | `/sessions` called nonexistent `get_user_sessions()`, breaking sidebar history. | Implemented `get_user_sessions()` and user-session indexing via Redis sets (`user_sessions:{user_id}`). |
| **C4** | 🔴 Critical | `conversation.py` / `exporter.py` | Export parameters nested inside `conversation_response` never reached the exporter. | Hoisted `export_requested` and `filtered_data` to top-level input dictionary. |
| **C5** | 🔴 Critical | `base.py` / `chat.py` | `BaseAgent._emit_progress()` was a stub; pipeline strip polled empty keys. | Integrated Redis progress publication with stage names, percentages, and status payloads. |
| **H1** | 🟠 High | `chat.py` | IDOR fail-open vulnerability if session owner key expired in Redis. | Migrated to fail-closed authorization: `if not owner_id or owner_id != current_user.id: raise 403`. |
| **H2** | 🟠 High | `auth_routes.py` | Refresh token rotation did not invalidate old token JTI. | Added Redis JTI revocation (`blacklist_jti`) during `/api/auth/refresh` rotation. |
| **H3** | 🟠 High | `client.ts` / Auth Pages | Access token stored in `localStorage` exposing sessions to XSS. | Migrated access token storage strictly to in-memory variables with silent refresh via `httpOnly` cookie. |
| **H4** | 🟠 High | `browser.py` | Playwright SSRF validation vulnerable to DNS-rebinding TOCTOU attack. | Rewrote Chromium network requests to validated literal IP while retaining original `Host` header. |
| **H5** | 🟠 High | `auth_routes.py` | Concurrent duplicate-email registrations caused unhandled `IntegrityError` 500s. | Wrapped commit in `try/except IntegrityError`, returning clean 400 "Email already registered". |
| **M1** | 🟡 Medium | `dataset/[sessionId]/page.tsx` | Dataset page direct load showed `undefined%` confidence and `0` flagged fields. | Surfaced `data.validation.confidence_score` and `flagged_rows_count` directly in UI. |
| **M2** | 🟡 Medium | `Sidebar.tsx` | Hardcoded mock user identity ("Manoj", "MN"). | Bound user block dynamically to authenticated user data from `GET /api/auth/me`. |
| **M3** | 🟡 Medium | Multiple Frontend Pages | Decorative inputs (session search, data search, composer loading state). | Implemented real-time filtering for sessions/data and bound composer UI to pipeline status. |
| **M4** | 🟡 Medium | `upload.py` | `session_id` query param ignored during file upload. | Added `session_id` parameter to upload route, saving parsed text directly to Redis session context. |
| **M5** | 🟡 Medium | `models/base.py` | `updated_at` timestamp never updated on record modification. | Configured automatic timestamp refresh hooks for database updates. |
| **M6** | 🟡 Medium | `base.py` / `security.py` | Inconsistent naive vs. timezone-aware datetimes (`utcnow` vs `now(timezone.utc)`). | Standardized all datetime operations across backend to timezone-aware UTC. |
| **M7** | 🟡 Medium | `rate_limit.py` / `main.py` | Rate limiter and audit logger lacked reverse-proxy IP handling. | Added `TRUST_PROXY_HEADERS` support with trusted proxy header parsing (`X-Forwarded-For`). |
| **M8** | 🟡 Medium | `setup.py` | Missing automated Playwright Chromium browser binary installation. | Added `playwright install chromium` step to backend setup runner. |

---

## 🏛️ Package Architecture & Module Resolution

To ensure seamless execution and zero language-server / IDE warning noise across all platforms, package imports have been restructured:
- **Module Shadowing Elimination**:
  - Renamed `apps/backend/agents/memory.py` → `apps/backend/agents/memory_agent.py` to eliminate namespace collision with top-level `apps/backend/memory/` package.
  - Renamed `apps/backend/api/auth.py` → `apps/backend/api/auth_routes.py` to eliminate namespace collision with top-level `apps/backend/auth/` security package.
- **Python Path Injection**: Configured `pyrightconfig.json` with `extraPaths: ["apps/backend"]` and dynamic `sys.path` bootstrapping in `main.py` for effortless local development and production containerization.


---

## 📁 Folder Structure

```
webiscrap/
│
├── apps/
│   ├── frontend/              # Next.js 16 UI
│   │   ├── src/app            # App Router (login, signup, chat, dataset layouts)
│   │   ├── src/components     # Custom HUD UI Components (Sidebar, DataTable, Composer, etc.)
│   │   ├── src/lib/store      # Zustand global state (chat.ts)
│   │   └── src/lib/api        # ApiClient class (in-memory token, silent refresh)
│   │
│   └── backend/               # FastAPI
│       ├── agents/             # 9-Agent Pipeline (orchestrator, planner, memory_agent, etc.)
│       ├── ai/                 # Groq Client, Key Manager, AI Router
│       ├── api/                # Route handlers (auth_routes, chat, scrape, export, upload)
│       ├── auth/               # JWT security, Google OAuth, Firebase Phone OTP
│       ├── core/               # App config & Redis Rate Limiter
│       ├── database/           # Async PostgreSQL connection (SQLModel)
│       ├── memory/             # Redis session store & token blacklisting
│       ├── models/             # Database ORM models (User, BaseUUIDModel)
│       ├── parsers/            # Document parsers (PDF, DOCX, CSV, Image/OCR)
│       ├── prompts/            # System prompts for each AI agent
│       └── main.py             # FastAPI entry point
│
├── pyrightconfig.json         # Python language server search path configuration
├── .env.example               # Environment variable template
├── .gitignore
└── README.md
```

---

## 🔧 Prerequisites

Before you start, make sure you have:

- **Python** 3.11+
- **Node.js** v20+
- **Git**
- **Groq API Key(s)** — [Get them free at console.groq.com](https://console.groq.com)
- **PostgreSQL** — use [Neon](https://neon.tech) free tier (managed)
- **Redis** — use [Upstash](https://upstash.com) free tier (managed)

---

## 🚀 Installation

```bash
# 1. Clone the repo
git clone https://github.com/manoj-n-dev/WEBISCRAP.git
cd WEBISCRAP

# 2. Set up the backend
cd apps/backend
python -m venv venv
.\venv\Scripts\activate     # Windows
# source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
playwright install chromium

# 3. Configure environment
cd ../..
cp .env.example .env
# Edit .env with your Groq API keys, database URL, and Redis URL

# 4. Quick Start (Run Both Backend & Frontend)
python setup.py
```

The API will be available at `http://localhost:8000` and the UI at `http://localhost:3000`.

Alternatively, you can run them manually:
```bash
# Terminal 1: Backend
cd apps/backend
uvicorn main:app --reload

# Terminal 2: Frontend
cd apps/frontend
npm run dev
```

---

## ⚙️ Configuration

Create a `.env` file in the **project root**:

```env
# AI Provider (Groq) — comma-separated keys for 10-key rotation
GROQ_API_KEYS=gsk_key1,gsk_key2,gsk_key3,...

# Database (Neon PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@host/dbname?sslmode=require

# Redis (Upstash)
REDIS_URL=rediss://default:password@host:6379

# JWT
JWT_SECRET=generate_a_strong_random_secret_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Security & Proxy
FRONTEND_URL=http://localhost:3000
RATE_LIMIT_PER_MINUTE=10
TRUST_PROXY_HEADERS=false
```

> **Note:** Set `TRUST_PROXY_HEADERS=true` only when deployed behind a reverse proxy you control (e.g. Vercel/Render). The current `.env.example` contains development placeholders only.

---

## 🗺️ Roadmap

- [x] PRD finalized
- [x] FastAPI backend skeleton + PostgreSQL schema
- [x] Authentication (Email/Password, Google OAuth, Phone OTP, Guest Mode)
- [x] API Key Manager (10-key Groq rotation with auto-failover)
- [x] Planner Agent
- [x] Website Analyzer Agent
- [x] Browser Automation Agent (Playwright + HTML minifier)
- [x] Extraction Agent
- [x] Cleaning Agent
- [x] Validation Agent
- [x] Memory Agent (`agents/memory_agent.py` + Redis session caching)
- [x] Conversation Agent (follow-up queries without re-scraping)
- [x] Export Agent (CSV, Excel, JSON, Markdown)
- [x] Multi-language prompt support (10+ languages)
- [x] Full pipeline verification (static + dynamic sites)
- [x] Next.js frontend UI rebuilt matching cinematic HUD reference
- [x] API Integration (Zustand -> FastAPI)
- [x] Production hardening (Rate limiting, CORS, Audit logs)
- [x] Functional Legal Pages (Terms & Privacy) and Login/Signup flows
- [x] Refresh token rotation + automatic 401 retry
- [x] SSRF protection on scrape targets with DNS-rebinding TOCTOU mitigation
- [x] Upload hardening & session context persistence
- [x] Ownership-based authorization (Fail-closed IDOR protection)
- [x] In-memory access token storage with secure httpOnly cookie rotation
- [x] Password strength validation + automated strong password generator
- [x] Full validation metadata surfaced in frontend dataset view
- [x] Complete security & integration audit (17 fixes: C1-C5, H1-H5, M1-M8)
- [x] Zero-warning package restructuring & module shadowing resolution
- [ ] Deployment to Vercel (Frontend) + Render (Backend)

---

## 🤝 Contributing

WEBISCRAP is being built by a small core team.

```bash
# Create your branch
git checkout -b feat/your-feature

# Commit your changes
git commit -m "feat: your feature description"

# Push and open a PR
git push origin feat/your-feature
```

---

## 📜 License

All Rights Reserved — see [LICENSE](LICENSE) file.

---

## 👨‍💻 Team

Built by:

**Manoj** · **Bhavya** · **Lohit** · **Sushanth** · **Muni Bharath**

---

**⭐ Star this repo to follow along as WEBISCRAP is built.**

*WEBISCRAP — Extract Anything. Ask Naturally. Export Instantly.*
