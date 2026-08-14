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
- ✅ The **FastAPI Backend** is 100% complete, hardened, and verified.
- ✅ The **9-Agent AI Pipeline** runs exclusively on **Groq** (LLaMA 3.3 70B).
- ✅ **Authentication logic** (Email/Password, Google OAuth, Phone OTP, Guest Mode) is implemented on the backend via JWT.
- ✅ **10-key rotation** with automatic failover, cooldown, and load balancing for Groq.
- ✅ Successfully tested on both **static** (HackerNews) and **dynamic/JS** (Quotes to Scrape) websites using Playwright.
- ✅ **Frontend UI** fully built in Next.js 16 (Turbopack) with a highly customized cinematic HUD glassmorphism design.
- ✅ **API Integration (Phase 5)** completed: Zustand globally manages live API interactions, session IDs, and polling for the PipelineStrip.
- ✅ **Production Hardening (Phase 6)** completed: Implemented Redis-based sliding window Rate Limiting, Audit Logging Middleware, and strict CORS.
- ✅ **Frontend Features Completed**: Legal pages (Terms/Privacy), fully working Auth (Login/Signup), and error handling for chat extractions.

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
- **Data Fetching**: A custom `ApiClient` (`src/lib/api/client.ts`) handles REST communications. The extraction endpoint (`POST /api/chat/`) accepts `multipart/form-data` to easily upload the prompt and target URL, passing along the `Authorization: Bearer <token>` in headers.

### 2. Backend (FastAPI)
- **Framework**: FastAPI (Python 3.11+). Runs asynchronously using Uvicorn.
- **Authentication**: JWT-based auth (`api/auth.py`). Passwords are hashed with `passlib` (bcrypt). Guest mode issues anonymous JWTs so users can test the platform without an account.
- **Middleware**: 
  - `AuditLoggingMiddleware`: Logs the IP, endpoint, response time, and HTTP status of every incoming request.
  - `CORSMiddleware`: Locked down to the `FRONTEND_URL` environment variable to prevent cross-origin abuse.
- **Rate Limiting**: Custom Redis-backed Sliding Window rate limiter (`core/rate_limit.py`). Automatically prevents LLM abuse by throttling IPs to a customizable limit (default 10 requests/minute).

### 3. Database & Caching
- **Database (PostgreSQL)**: Managed via Neon. Mapped via `SQLModel` and `SQLAlchemy`. Stores `User` records, hashed passwords, and OAuth IDs.
- **Caching (Redis)**: Managed via Upstash. Redis powers two core systems:
  1. **Rate Limiting**: Sliding window token bucket.
  2. **Session Memory**: Once an extraction is completed, the resulting JSON schema is cached in Redis using the `session_id`. When a user asks a follow-up question (e.g. "sort by price"), the memory agent retrieves the data directly from Redis, bypassing the entire scraping pipeline.

---

## 🧠 The 9-Agent AI Pipeline

The beating heart of WEBISCRAP is the Orchestrator (`apps/backend/agents/orchestrator.py`), which passes state across 9 specialized AI Agents. Every agent calls the Groq API (LLaMA 3 70B) utilizing a 10-key rotation pool (`ai.key_manager`) to prevent rate limits.

| # | Agent | Role | What It Does (Technical Depth) |
|---|-------|------|---------------|
| 1 | 🧭 **Planner Agent** | Orchestrator | Interprets intent using prompt engineering. Decides if a new scrape is needed or if this is a follow-up query against the cache. Outputs a JSON workflow plan. |
| 2 | 🔬 **Website Analyzer Agent** | Structure | Analyzes raw DOM/HTML (minified). It detects repeating `<li>`, `<tr>`, or `<div>` card layouts to determine where the data lies. |
| 3 | 🌐 **Browser Automation Agent** | Automation | Uses `Playwright` to spawn a headless Chromium instance. It navigates to the URL, waits for network idle, scrolls to the bottom to trigger lazy-loaded JS elements, and captures the final rendered HTML. The HTML is then passed through a rigorous minifier to strip `<script>`, `<style>`, and SVG tags to fit within the LLaMA context window. |
| 4 | 📦 **Extraction Agent** | Extraction | Receives the minified HTML and the Planner's field list. Forces a `json_object` response format via the LLM to guarantee structured output matching the requested schema. |
| 5 | 🧹 **Cleaning Agent** | Data Quality | A post-processing LLM pass. Dedupes identical rows, normalizes currencies/dates, and resolves relative URLs (`/images/pic.png`) to absolute URLs (`https://site.com/images/pic.png`). |
| 6 | ✅ **Validation Agent** | Trust | Compares the output against the schema. Calculates a `confidence_score` (0.0 to 1.0) and flags missing/null fields. |
| 7 | 🧠 **Memory Agent** | Session Memory | Saves the validated JSON to Redis (`SET session:{id}:data`). For follow-ups, retrieves it. |
| 8 | 💬 **Conversation Agent** | Follow-ups | Takes a follow-up natural language query, takes the cached JSON, and writes a Python snippet or directly prompts the LLM to filter, sort, or modify the JSON. |
| 9 | 📤 **Export Agent** | Output | Translates JSON array into raw string formats (CSV, Excel, JSON, Markdown). |

---

## 🔒 Security & Production Hardening

- **Key Rotation**: `apps/backend/ai/key_manager.py` manages a `cycle()` iterator across all keys provided in `GROQ_API_KEYS`. If a key hits a 429 Rate Limit, it is put into a "cooldown dictionary" for 60 seconds and the next key is tried automatically.
- **Audit Logs**: Every API request is tracked by `AuditLoggingMiddleware` to stdout, making it easily ingested by Datadog or AWS CloudWatch.
- **Strict CORS**: `allow_origins=[settings.FRONTEND_URL]` instead of `*`.
- **IP Rate Limiting**: Redis ZSET (Sorted Set) tracks requests per IP. Drops connections via `429 Too Many Requests` if the 1-minute window is exceeded.

---

## 📁 Folder Structure

```
webiscrap/
│
├── apps/
│   ├── frontend/              # Next.js 16 UI
│   │   ├── src/app            # App Router (login, chat, dataset layouts)
│   │   ├── src/components     # Custom HUD UI Components
│   │   ├── src/lib/store      # Zustand global state
│   │   └── src/lib/api        # ApiClient class
│   │
│   └── backend/               # FastAPI
│       ├── agents/             # 9-Agent Pipeline (orchestrator, planner, analyzer, browser, etc.)
│       ├── ai/                 # Groq Client, Key Manager, AI Router
│       ├── api/                # FastAPI route handlers (auth, chat, scrape, export, upload)
│       ├── auth/               # JWT security, Google OAuth, Firebase Phone OTP
│       ├── core/               # App config & Redis Rate Limiter
│       ├── database/           # Async PostgreSQL connection (SQLModel)
│       ├── memory/             # Redis session store
│       ├── models/             # Database ORM models (User, etc.)
│       ├── parsers/            # Document parsers (PDF, DOCX, CSV, Image/OCR)
│       ├── prompts/            # System prompts for each AI agent
│       └── main.py             # FastAPI entry point
│
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

# 4. Run the backend
cd apps/backend
uvicorn main:app --reload

# 5. Run the frontend
cd ../frontend
npm install
npm run dev
```

The API will be available at `http://localhost:8000` and the UI at `http://localhost:3000`.

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

# Security
FRONTEND_URL=http://localhost:3000
RATE_LIMIT_PER_MINUTE=10
```

> **Note:** All API keys, database URLs, and Redis URLs should be changed before deployment. The current `.env.example` contains development placeholders only.

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
- [x] Memory Agent (Redis session caching)
- [x] Conversation Agent (follow-up queries without re-scraping)
- [x] Export Agent (CSV, Excel, JSON, Markdown)
- [x] Multi-language prompt support (10+ languages)
- [x] Full pipeline verification (static + dynamic sites)
- [x] Next.js frontend UI rebuilt matching cinematic HUD reference
- [x] API Integration (Zustand -> FastAPI)
- [x] Production hardening (Rate limiting, CORS, Audit logs)
- [x] Functional Legal Pages (Terms & Privacy) and Login/Signup flows
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
