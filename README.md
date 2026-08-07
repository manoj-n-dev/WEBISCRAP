# WEBISCRAP 🕸️

<div align="center">
  <table>
    <tr>
      <td align="center" style="padding: 10px;">
        <img src="apps/frontend/public/assets/branding-logo.png" alt="WEBISCRAP Branding Logo" width="300" />
        <br />
        <strong>Branding Logo</strong>
      </td>
      <td align="center" style="padding: 10px;">
        <img src="apps/frontend/public/assets/inner-logo.png" alt="WEBISCRAP Inner Logo" width="150" />
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
![Status](https://img.shields.io/badge/Status-In%20Development-00ff78?style=flat-square)

> *"Paste a link. Ask in your own words. Get your data."*

---

## 📑 Table of Contents

- [Current Status](#-current-status--next-steps)
- [Overview](#-overview)
- [How It Works](#-how-it-works)
- [Agent Team](#-agent-team)
- [Session-Aware Intelligence](#-session-aware-intelligence)
- [Tech Stack](#-tech-stack)
- [Folder Structure](#-folder-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#️-configuration)
- [Roadmap](#️-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Team](#-team)

---

## 🚀 Current Status & Next Steps

**Where we are:**
- ✅ The **FastAPI Backend** is 100% complete and verified.
- ✅ The **9-Agent AI Pipeline** runs exclusively on **Groq** (LLaMA 3.3 70B).
- ✅ **Authentication logic** (Email/Password, Google OAuth, Phone OTP, Guest Mode) is implemented on the backend.
- ✅ **10-key rotation** with automatic failover, cooldown, and load balancing.
- ✅ Successfully tested on both **static** (HackerNews) and **dynamic/JS** (Quotes to Scrape) websites.
- ✅ **Phase 4 (Frontend UI):** Fully rebuilt Next.js chat-first UI matching the cinematic HUD glassmorphism design.

**What we are doing next:**
- ✅ **Phase 5 (Frontend API Integration):** Wire up Zustand state and Next.js pages to the live FastAPI backend.
- 🔲 **Deployment:** Deploy frontend to Vercel, backend to Render/Railway.

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

## 🧠 How It Works

```
You (Chat Interface)
        │
        ▼
   Planner Agent
 (intent · strategy · workflow)
        │
        ▼
Website Analyzer Agent
   (DOM structure)
        │
        ▼
Browser Automation Agent
  (Playwright · render · capture)
        │
        ▼
  Extraction Agent
 (titles · prices · tables · emails · images)
        │
        ▼
  Cleaning Agent
 (dedupe · normalize · fix URLs)
        │
        ▼
 Validation Agent
(confidence scores · flags)
        │
        ▼
   Memory Agent
(session cache · context)
        │
        ▼
Conversation Agent  ──▶  Export Agent
(answers, filters,        (CSV · Excel · JSON
 follow-ups)                Markdown · PDF)
```

For follow-up questions, the flow **short-circuits straight to the Conversation Agent** — no re-scrape needed.

---

## 🤖 Agent Team

| # | Agent | Role | What It Does |
|---|-------|------|---------------|
| 1 | 🧭 **Planner Agent** | Orchestrator | Interprets intent, decides extraction strategy, builds the workflow |
| 2 | 🔬 **Website Analyzer Agent** | Structure | Analyzes DOM/HTML/CSS/JS, detects repeating blocks and layouts |
| 3 | 🌐 **Browser Automation Agent** | Automation | Drives Playwright — navigates, scrolls, waits for JS, captures rendered DOM |
| 4 | 📦 **Extraction Agent** | Extraction | Pulls titles, prices, tables, reviews, images, emails, contact info |
| 5 | 🧹 **Cleaning Agent** | Data Quality | Removes duplicates, normalizes formatting, fixes broken URLs |
| 6 | ✅ **Validation Agent** | Trust | Checks completeness, assigns confidence scores, flags uncertainty |
| 7 | 🧠 **Memory Agent** | Session Memory | Caches datasets and chat history, enables follow-ups without re-scraping |
| 8 | 💬 **Conversation Agent** | Follow-ups | Filters, sorts, compares, summarizes cached data — no new scrape |
| 9 | 📤 **Export Agent** | Output | Generates CSV, Excel, JSON, Markdown, and PDF exports |

All nine agents run as a coordinated pipeline for the first request, then hand off to the Memory + Conversation agents for everything after.

---

## 💾 Session-Aware Intelligence

The core differentiator. Once a site is scraped, the dataset is cached for the session. Follow-ups are answered from cache instead of re-hitting the website.

```
User: Extract all laptop prices.
AI:   [Scrapes website] → Returns structured dataset.

User: Show only Dell laptops.
AI:   [No new scrape] → Filters cached dataset.

User: Sort by highest rating.
AI:   [No new scrape] → Sorts cached dataset.

User: Export only Dell laptops.
AI:   [No new scrape] → Exports filtered cached dataset.
```

This is what separates WEBISCRAP from single-shot scraping tools — value compounds with every question instead of resetting.

---

## 💻 Tech Stack

```
Frontend      →  Next.js + React + TypeScript (upcoming)
Backend       →  FastAPI (Python) · REST API · JWT auth + refresh tokens
AI Provider   →  Groq (100% routing to llama-3.3-70b-versatile, 10-key rotation)
Browser       →  Playwright (dynamic JS rendering) + BeautifulSoup/lxml (static)
Auth          →  JWT · Google OAuth · Firebase (Phone OTP) · Guest Mode
Database      →  PostgreSQL (Neon, managed)
Caching       →  Redis (Upstash, session + dataset caching)
Deployment    →  Vercel (frontend) · Render/Railway (backend) · Neon (database)
```

### Why This Stack?

- **100% Groq Architecture** — All 9 agents route exclusively to Groq (LLaMA 3 70B). An aggressive HTML minifier protects the context window, and a 10-key rotation pool ensures near-zero downtime from rate limits.
- **Playwright** — Full JS rendering for React/Vue/Angular/SPA sites, infinite scroll, and dynamic pagination — no brittle static-only scraping.
- **Session-first design** — Redis + Postgres combination keeps extracted datasets alive for the session so follow-up questions never trigger a redundant scrape.
- **FastAPI + Next.js** — A clean separation between a fast async Python backend for agent orchestration and a streaming, chat-first frontend.

---

## 📁 Folder Structure

```
webiscrap/
│
├── apps/
│   ├── frontend/              # (Upcoming) Next.js chat UI
│   │
│   └── backend/               # FastAPI backend
│       ├── agents/             # 9-Agent Pipeline (orchestrator, planner, analyzer, browser, etc.)
│       │   ├── base.py         # BaseAgent class with progress events
│       │   ├── orchestrator.py # PipelineOrchestrator — coordinates all agents
│       │   ├── planner.py      # Intent parsing and workflow planning
│       │   ├── analyzer.py     # DOM structure analysis
│       │   ├── browser.py      # Playwright automation + HTML minifier
│       │   ├── extractor.py    # AI-driven data extraction
│       │   ├── cleaner.py      # Deduplication and normalization
│       │   ├── validator.py    # Confidence scoring
│       │   ├── memory.py       # Session cache save/load
│       │   ├── conversation.py # Follow-up query handling
│       │   └── exporter.py     # CSV/Excel/JSON/Markdown export
│       ├── ai/                 # Groq Client, Key Manager, AI Router
│       ├── api/                # FastAPI route handlers (auth, chat, scrape, export, upload)
│       ├── auth/               # JWT security, Google OAuth, Firebase Phone OTP
│       ├── core/               # App settings and config (Pydantic Settings)
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
- **Node.js** v20+ (for frontend, upcoming)
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
```

The API will be available at `http://localhost:8000` and docs at `http://localhost:8000/docs`.

---

## ⚙️ Configuration

Create a `.env` file in the **project root** (not in `apps/backend/`):

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

# Google OAuth (optional for dev)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Firebase Phone OTP (optional for dev)
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_CLIENT_EMAIL=your_firebase_client_email
# ... see .env.example for full list
```

> **Note:** All API keys, database URLs, and Redis URLs should be changed before deployment. The current `.env` contains development credentials only.

---

## 🗺️ Roadmap

Based on the backend-first build plan:

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
- [x] Real authentication testing with live credentials
- [ ] Production hardening (rate limiting, CSRF, audit logs)
- [ ] Deployment to Vercel + Render

---

## 🤝 Contributing

WEBISCRAP is being built by a small core team, following a backend-first approach — all agents, APIs, and auth are completed and tested before frontend work begins.

```bash
# Create your branch
git checkout -b feat/your-feature

# Commit your changes
git commit -m "feat: your feature description"

# Push and open a PR
git push origin feat/your-feature
```

Every completed agent goes through Unit, Integration, API, and Performance testing before merging into `main`.

---

## 📜 License

All Rights Reserved — see [LICENSE](LICENSE) file.

---

## 👨‍💻 Team

Built by:

**Manoj** · **Bhavya** · **Lohit** · **Sushanth** · **Muni Bharath**

---

**⭐ Star this repo to follow along as WEBISCRAP gets built.**

*WEBISCRAP — Extract Anything. Ask Naturally. Export Instantly.*
