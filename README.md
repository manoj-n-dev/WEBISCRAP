# WEBISCRAP 🕸️

### *Extract Anything. Ask Naturally. Export Instantly.*

**WEBISCRAP** is a conversational, AI-powered web data extraction platform that replaces traditional scraping workflows — CSS selectors, XPath, brittle scripts — with plain natural language. Paste a URL, describe what you want in your own words (English, Telugu, Hindi, Tamil, Hinglish, or mixed), and a team of nine specialized AI agents plans, browses, extracts, cleans, validates, and exports the data for you.

Not a scraping tool. Not a selector builder. **A research assistant that happens to understand websites.**

![License: MIT](https://img.shields.io/badge/License-MIT-purple?style=flat-square)
![Made in India](https://img.shields.io/badge/Made%20in-India%20%F0%9F%87%AE%F0%9F%87%B3-ff6b35?style=flat-square)
![Status](https://img.shields.io/badge/Status-In%20Development-00ff78?style=flat-square)

> *"Paste a link. Ask in your own words. Get your data."*

---

## 📑 Table of Contents

- [Overview](#-overview)
- [How It Works](#-how-it-works)
- [Agent Team](#-agent-team)
- [Session-Aware Intelligence](#-session-aware-intelligence)
- [Tech Stack](#-tech-stack)
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
Frontend      →  Next.js + React + TypeScript (Tailwind, shadcn/ui, TanStack Query)
Backend       →  FastAPI (Python) · REST API · JWT auth + refresh tokens
AI Providers  →  Groq (fast reasoning) + Google Gemini (large-context, extraction) [llama-3.3-70b-versatile, gemini-3.5-flash]
Browser       →  Playwright (dynamic JS rendering) + BeautifulSoup/lxml (static)
Auth          →  Better Auth / Auth.js · Google OAuth · Firebase (Phone OTP)
Database      →  PostgreSQL (Neon, production) / SQLite (development)
Caching       →  Redis (session + dataset caching)
Storage       →  Local (dev) / Cloudflare R2 (uploads)
Deployment    →  Vercel (frontend) · Render/Railway/Fly.io (backend)
```

### Why This Stack?

- **Dual AI Providers** — Groq handles fast reasoning (planning, conversation, validation); Gemini handles large-context work (extraction, cleaning, multi-language understanding). A 10-key rotation pool per provider means near-zero downtime from quota limits.
- **Playwright** — Full JS rendering for React/Vue/Angular/SPA sites, infinite scroll, and dynamic pagination — no brittle static-only scraping.
- **Session-first design** — Redis + Postgres combination keeps extracted datasets alive for the session so follow-up questions never trigger a redundant scrape.
- **FastAPI + Next.js** — A clean separation between a fast async Python backend for agent orchestration and a streaming, chat-first frontend.

---

## 📁 Folder Structure

```
webiscrap/
│
├── apps/
│   ├── frontend/              # Next.js chat UI
│   │   ├── app/                # App Router pages (Chat, Login, History, Settings)
│   │   ├── components/         # UI components
│   │   └── lib/                # Utilities, API client
│   │
│   └── backend/               # FastAPI backend
│       ├── api/                 # REST routes
│       ├── auth/                 # JWT, OAuth, OTP
│       └── main.py
│
├── packages/
│   ├── agents/                 # Planner, Analyzer, Extraction, Cleaning, Validation,
│   │                           # Memory, Conversation, Export agents
│   ├── ai/                     # Groq + Gemini client, key rotation manager
│   ├── browser/                 # Playwright automation layer
│   ├── scraper/                 # Static parsing (BeautifulSoup/lxml)
│   ├── parsers/                 # File-type parsers (PDF, DOCX, CSV, images/OCR)
│   ├── exporters/               # CSV, Excel, JSON, Markdown, PDF generation
│   ├── memory/                  # Session + dataset caching
│   └── shared/                  # Shared types and helpers
│
├── uploads/
├── exports/
├── docs/
│   └── WEBISCRAPv1_PRD.md
│
├── .env.example
├── docker-compose.yml
├── README.md
└── LICENSE
```

---

## 🔧 Prerequisites

Before you start, make sure you have:

- **Node.js** v20+
- **Python** 3.11+
- **npm** or **yarn**
- **PostgreSQL** (or use Neon's managed free tier)
- **Redis** (optional locally, recommended for production)
- **Git**
- API keys: **Groq** and **Google AI Studio (Gemini)**

---

## 🚀 Installation

```bash
# 1. Clone the repo
git clone https://github.com/manoj-n-dev/WEBISCRAP.git
cd webiscrap

# 2. Install frontend dependencies
cd apps/frontend && npm install

# 3. Install backend dependencies
cd ../backend && pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
# Add your Groq / Gemini API keys and database URL

# 5. Run in development
# Terminal 1 — Frontend
cd apps/frontend && npm run dev

# Terminal 2 — Backend
cd apps/backend && uvicorn main:app --reload
```

---

## ⚙️ Configuration

Create a `.env` file in `/apps/backend`:

```
# AI Providers
GROQ_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/webiscrap

# Auth
JWT_SECRET=your_secret_here
GOOGLE_OAUTH_CLIENT_ID=your_client_id
FIREBASE_PROJECT_ID=your_firebase_project

# Cache
REDIS_URL=redis://localhost:6379

# App config
PORT=8000
ENV=development
```

> WEBISCRAP supports a pool of multiple Groq and Gemini keys for automatic rotation on rate limits — add additional keys as `GROQ_API_KEY_2`, `GEMINI_API_KEY_2`, etc. once the key manager is in place.

---

## 🐳 Deployment

### Frontend — Vercel

```bash
cd apps/frontend
vercel --prod
```

### Backend — Render / Railway / Fly.io

```bash
# Push to your connected repo, or deploy via Docker
docker compose up --build
```

### Database — Neon PostgreSQL

Provision a free Neon instance and point `DATABASE_URL` at it for production.

---

## 🗺️ Roadmap

Based on the 2-month, 16-session backend-first build plan:

- [x] PRD finalized
- [x] API Key Manager (10-key rotation, Groq + Gemini)
- [x] Multi-language prompt support (10+ languages)
- [x] Planner Agent
- [x] Website Analyzer Agent
- [x] Browser Automation Agent (Playwright)
- [x] Extraction Agent
- [x] Cleaning Agent
- [x] Validation Agent
- [x] Memory Agent (session caching)
- [x] Conversation Agent (follow-up queries)
- [x] Export Agent (CSV, Excel, JSON, Markdown, PDF)
- [x] Authentication (Email/Password, Google OAuth, Phone OTP, Guest Mode)
- [ ] Frontend chat interface + streaming responses
- [ ] Production hardening (rate limiting, CSRF, audit logs)

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

MIT License — see [LICENSE](LICENSE) file.

---

## 👨‍💻 Team

Built by:

**Manoj** · **Bhavya** · **Lohit** · **Sushanth** · **Muni Bharath**

---

**⭐ Star this repo to follow along as WEBISCRAP gets built.**

*WEBISCRAP — Extract Anything. Ask Naturally. Export Instantly.*
