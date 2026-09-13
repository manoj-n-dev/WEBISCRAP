<div align="center">
  <img src="https://raw.githubusercontent.com/manoj-n-dev/WEBISCRAP/main/apps/frontend/public/assets/branding-logo.png" alt="WEBISCRAP" width="320" />
</div>

# WEBISCRAP 🕸️

### *Extract Anything. Ask Naturally. Export Instantly.*

**WEBISCRAP** is a conversational, AI-powered web data extraction platform that replaces traditional scraping workflows — CSS selectors, XPath, brittle scripts — with plain natural language. Paste a URL, describe what you want in your own words (English, Telugu, Hindi, Tamil, Hinglish, or mixed), and a team of nine specialized AI agents plans, browses, extracts, cleans, validates, and exports the data for you.

Not a scraping tool. Not a selector builder. **A research assistant that happens to understand websites.**

![License: All Rights Reserved](https://img.shields.io/badge/License-All%20Rights%20Reserved-red?style=flat-square)
![Made in India](https://img.shields.io/badge/Made%20in-India%20%F0%9F%87%AE%F0%9F%87%B3-ff6b35?style=flat-square)
![Status](https://img.shields.io/badge/Status-Production%20Ready-00ff78?style=flat-square)

> *"Paste a link. Ask in your own words. Get your data."*

---

## 📑 Table of Contents

- [Overview](#-overview)
- [How It Works](#-how-it-works)
- [The 9-Agent Pipeline](#-the-9-agent-pipeline)
- [Tech Stack](#-tech-stack)
- [Security Highlights](#-security-highlights)
- [Folder Structure](#-folder-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#️-configuration)
- [Deployment](#-deployment)
- [Roadmap](#️-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Team](#-team)

---

## ⚡ Overview

WEBISCRAP is built on one idea —

> **Scraping is a side effect of conversation, not the main interaction.**

There's no dashboard, no manual selector builder, no scrape-configuration screen. The chat interface **is** the product. Ask once, and follow-up questions ("sort by price", "only show items with ratings") are answered from cached session memory — no re-scraping required.

**No selectors. No scripts. No re-scraping for follow-up questions.**

---

## 🧠 How It Works

```
"Extract all laptop names, prices, ratings, and images from this site"

  Planner Agent        →  Understands intent, builds a plan
  Website Analyzer     →  Reads the DOM, finds repeating structures
  Browser Automation   →  Renders JS-heavy pages with Playwright
  Extraction Agent     →  Pulls the requested fields
  Cleaning Agent        →  Normalizes and dedupes
  Validation Agent     →  Scores confidence, flags gaps
  Memory Agent          →  Caches the dataset in Redis for follow-ups

  Structured table + export options → Delivered in chat. Done.
```

---

## 🤖 The 9-Agent Pipeline

The beating heart of WEBISCRAP is the Orchestrator (`apps/backend/agents/orchestrator.py`), which passes state across nine specialized AI agents. Every agent calls the Groq API (LLaMA 3 70B) through a rotating key pool (`ai/key_manager.py`) to avoid rate limits.

| # | Agent | Role | What It Does |
|---|-------|------|---------------|
| 1 | 🧭 **Planner** | Orchestrator | Interprets intent, decides whether a new scrape is needed or this is a follow-up against cache, outputs a JSON workflow plan |
| 2 | 🔬 **Website Analyzer** | Structure | Analyzes minified DOM/HTML, detects repeating `<li>`, `<tr>`, or `<div>` card layouts |
| 3 | 🌐 **Browser Automation** | Automation | Drives headless Chromium via Playwright — waits for network idle, scrolls to trigger lazy-loaded content, captures the rendered HTML with SSRF/DNS-rebinding defenses in place |
| 4 | 📦 **Extraction** | Extraction | Forces a `json_object` response from the LLM to match the requested schema |
| 5 | 🧹 **Cleaning** | Data Quality | Dedupes rows, normalizes currencies/dates, resolves relative URLs to absolute |
| 6 | ✅ **Validation** | Trust | Scores a `confidence_score` (0.0–1.0) and flags missing/null fields |
| 7 | 🧠 **Memory** | Session Memory | Saves validated JSON to Redis (`session_data:{id}`) for instant follow-ups |
| 8 | 💬 **Conversation** | Follow-ups | Filters, sorts, or reshapes cached data from natural-language follow-up questions |
| 9 | 📤 **Export** | Output | Converts JSON into CSV, Excel, JSON, or Markdown, with formula-injection sanitization |

---

## 💻 Tech Stack

```
Frontend      →  Next.js 16 (App Router · Turbopack) + React 19
State         →  Zustand
Styling       →  Tailwind CSS v4 (custom glassmorphism "HUD" theme)
Data Layer    →  TanStack Query + TanStack Table

Backend       →  FastAPI (Python 3.11+, async, Uvicorn)
Database      →  PostgreSQL via Neon (SQLModel + SQLAlchemy)
Cache/Queue   →  Redis via Upstash (rate limiting, session memory, JTI blacklist, job queue)
AI Provider   →  Groq (LLaMA 3 70B) with rotating multi-key pool
Browser       →  Playwright (headless Chromium)
Auth          →  JWT (access + refresh rotation), Google OAuth, Firebase Phone OTP, Guest Mode

Deployment    →  Render (API + durable Redis worker) + Vercel (frontend)
```

---

## 🔒 Security Highlights

WEBISCRAP has been through a full internal security and architecture audit covering authentication, session handling, SSRF, and data validation. Highlights:

- **In-memory access tokens** — access tokens never touch `localStorage`; refresh tokens live only in `httpOnly`, `SameSite` cookies with silent rotation.
- **Fail-closed authorization** — every session-scoped endpoint explicitly verifies ownership before returning data.
- **SSRF & DNS-rebinding defenses** — Playwright resolves and validates the target IP against private/internal/cloud-metadata ranges before navigating, and pins the request to the validated literal IP.
- **JWT hardening** — positive token-type validation, `token_version` binding for global session invalidation on password reset, and JTI blacklisting on refresh rotation.
- **Durable job queue** — scraping jobs are queued in Redis and processed by a dedicated worker, so a server restart never loses in-flight work.
- **Upload hardening** — magic-byte validation, extension allowlists, and size limits on all uploaded files.
- **Rate limiting** — sliding-window limiter with in-memory fallback if Redis is unreachable, reverse-proxy aware.

---

## 📁 Folder Structure

```
webiscrap/
│
├── apps/
│   ├── frontend/                  # Next.js 16 UI
│   │   ├── src/app                # App Router — (marketing), (auth), (app) route groups
│   │   ├── src/components         # Sidebar, Composer, DataTable, PipelineStrip, Logo, ui/
│   │   ├── src/lib/store          # Zustand global state (chat.ts)
│   │   └── src/lib/api            # ApiClient (in-memory token, silent refresh)
│   │
│   └── backend/                   # FastAPI
│       ├── agents/                # 9-agent pipeline (orchestrator, planner, memory_agent, ...)
│       ├── ai/                    # Groq client, key rotation manager, router
│       ├── api/                   # Route handlers (auth_routes, chat, scrape, export, upload)
│       ├── auth/                  # JWT security, Google OAuth, Firebase Phone OTP
│       ├── core/                  # App config, rate limiter, audit logger, health checks
│       ├── database/              # Async PostgreSQL connection (SQLModel) + migrations
│       ├── memory/                # Redis session store & token blacklisting
│       ├── models/                # ORM models (User, BaseUUIDModel)
│       ├── parsers/                # Document parsers (PDF, DOCX, CSV, image/OCR)
│       ├── prompts/                # System prompts per agent
│       ├── workers/                # Durable Redis scrape job worker
│       └── main.py                 # FastAPI entry point
│
├── render.yaml                    # Render Blueprint — API service + queue worker
├── pyrightconfig.json             # Python language-server search paths
├── .env.example                   # Environment variable template
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

# Team mirror (alternate remote):
# git clone https://github.com/team3c23/WEBISCRAP.git

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

# 4. Quick start (runs both backend & frontend)
python dev.py
```

The API will be available at `http://localhost:8000` and the UI at `http://localhost:3000`.

Alternatively, run them manually:

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
# AI Provider (Groq) — comma-separated keys for rotation
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

> **Note:** Set `TRUST_PROXY_HEADERS=true` only when deployed behind a reverse proxy you control (e.g. Vercel/Render). `.env.example` contains development placeholders only — never commit real secrets.

---

## 🌐 Deployment

WEBISCRAP is architected for zero-downtime deployment across **Render** (backend API + queue worker) and **Vercel** (Next.js frontend).

### Backend on Render (`render.yaml`)

1. Create a free account on [Render](https://render.com) and connect your GitHub repository.
2. Click **New +** → **Blueprint** and select the repository. Render parses `render.yaml` and provisions:
   - `webiscrap-api` — Docker web service running FastAPI, health-monitored on `/health`.
   - `webiscrap-worker` — Docker background worker running `python -m workers.scrape_worker` to dequeue durable Redis scraping jobs.
3. Fill in production environment variables in the Render dashboard: `DATABASE_URL`, `REDIS_URL`, `GROQ_API_KEYS`, `FRONTEND_URL`, `BACKEND_CORS_ORIGINS`, and SMTP/OAuth/Firebase credentials as needed.

### Frontend on Vercel (`vercel.json`)

1. Import the repository on [Vercel](https://vercel.com) and set the **Root Directory** to `apps/frontend`.
2. Set `NEXT_PUBLIC_API_URL` (your Render backend URL) and `NEXT_PUBLIC_APP_URL` (your Vercel canonical URL) in Project Settings.
3. Deploy — Vercel applies the security headers configured in `vercel.json` automatically.

### Keep-Alive Monitor

Free Render services sleep after 15 minutes of inactivity. Point an external monitor (e.g. [UptimeRobot](https://uptimerobot.com) or [Cron-Job.org](https://cron-job.org)) at `https://<your-render-api>.onrender.com/health` every 5 minutes — the probe has zero external dependencies, so it's safe to ping indefinitely.

---

## 🗺️ Roadmap

- [x] Authentication — Email/Password, Google OAuth, Phone OTP, Guest Mode
- [x] 9-agent extraction pipeline (Planner → Export)
- [x] Follow-up conversation without re-scraping (Redis session memory)
- [x] Multi-format export (CSV, Excel, JSON, Markdown)
- [x] SSRF & DNS-rebinding protection on scrape targets
- [x] Durable Redis job queue with dedicated worker
- [x] In-memory access tokens + `httpOnly` refresh rotation
- [x] Cinematic HUD frontend UI (Next.js 16 + Tailwind v4)
- [x] Production deployment — Render Blueprint + Vercel
- [ ] **v2:** Migrate auth system and database to Supabase

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

- Primary repo: [github.com/manoj-n-dev/WEBISCRAP](https://github.com/manoj-n-dev/WEBISCRAP)
- Team org repo: [github.com/team3c23/WEBISCRAP](https://github.com/team3c23/WEBISCRAP)

---

**⭐ Star this repo to follow along as WEBISCRAP is built.**

*WEBISCRAP — Extract Anything. Ask Naturally. Export Instantly.*