<div align="center">
  <img src="https://raw.githubusercontent.com/manoj-n-dev/WEBISCRAP/main/apps/frontend/public/assets/branding-logo.png" alt="WEBISCRAP" width="320" />
</div>

# WEBISCRAP 🕸️

### *Extract Anything. Ask Naturally. Export Instantly.*

**WEBISCRAP** is a conversational, AI-powered web data extraction platform that replaces traditional scraping workflows — CSS selectors, XPath, and brittle scripts — with plain natural language. Paste a URL or upload a document, describe what data you want in your own words (English, Telugu, Hindi, Tamil, Hinglish, or mixed), and an autonomous swarm of nine specialized AI agents plans, browses, extracts, cleans, validates, and exports the data for you.

[![Live App](https://img.shields.io/badge/Live%20App-webiscrap.vercel.app-1477f5?style=flat-square&logo=vercel)](https://webiscrap.vercel.app)
[![API Status](https://img.shields.io/badge/API-Operational-00ff78?style=flat-square&logo=render)](https://webiscrap-api.onrender.com/health)
[![Milestone](https://img.shields.io/badge/Milestone-92%20Commits%20%7C%20Road%20to%20100-8a2be2?style=flat-square&logo=github)](#-milestones--roadmap)
[![License: All Rights Reserved](https://img.shields.io/badge/License-All%20Rights%20Reserved-red?style=flat-square)](#-license)
[![Made in India](https://img.shields.io/badge/Made%20in-India%20%F0%9F%87%AE%F0%9F%87%B3-ff6b35?style=flat-square)](#-team)

> *"Paste a link. Ask in your own words. Get your data."*

---

## 🌐 Live Deployments

- **Web Application:** [https://webiscrap.vercel.app](https://webiscrap.vercel.app)
- **Backend REST API:** [https://webiscrap-api.onrender.com](https://webiscrap-api.onrender.com)
- **API Health Check:** [https://webiscrap-api.onrender.com/health](https://webiscrap-api.onrender.com/health)
- **Primary Repository:** [github.com/manoj-n-dev/WEBISCRAP](https://github.com/manoj-n-dev/WEBISCRAP)
- **Team Organization Mirror:** [github.com/team3c23/WEBISCRAP](https://github.com/team3c23/WEBISCRAP)

---

## 📑 Table of Contents

- [Overview](#-overview)
- [How It Works](#-how-it-works)
- [The 9-Agent Pipeline](#-the-9-agent-pipeline)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Security & Architecture Hardening](#-security--architecture-hardening)
- [Folder Structure](#-folder-structure)
- [Milestones & Roadmap](#-milestones--roadmap)
- [Prerequisites](#-prerequisites)
- [Installation & Local Setup](#-installation--local-setup)
- [Environment Configuration](#️-environment-configuration)
- [Production Deployment](#-production-deployment)
- [Team](#-team)
- [License](#-license)

---

## ⚡ Overview

WEBISCRAP is built on one core philosophy:

> **Scraping is a side effect of conversation, not the main interaction.**

Traditional scrapers require configuring CSS selectors, writing custom scrapers in Python or Puppeteer, and rebuilding parsers every time a website changes its HTML classes. 

With WEBISCRAP:
- **No CSS Selectors or XPath:** The LLM-driven analyzer and extractor identify data structures semantically.
- **Multilingual Understanding:** Natural queries in English, Hindi, Telugu, Tamil, and Hinglish.
- **Zero Re-Scraping for Follow-ups:** Extracted datasets are cached in Redis session memory (`z1:` compressed). Ask questions like *"sort by lowest price"* or *"filter items rating > 4.5"* with instantaneous in-memory results.
- **Interactive HUD & Direct Export:** View interactive tables directly in chat, edit session titles, and export clean files to CSV, Excel, JSON, Markdown, or PDF.

---

## 🧠 How It Works

```
User Prompt: "Extract all laptop names, prices, ratings, and image links from this site"
             + URL (or attached PDF/Excel/CSV/DOCX)

  1. Planner Agent        →  Understands intent, decides if scrape or cache query is needed
  2. Website Analyzer     →  Reads rendered DOM, finds repeating card/table layouts
  3. Browser Automation   →  Drives headless Chromium via Playwright (lazy-scroll & JS hydration)
  4. Extraction Agent     →  Extracts clean JSON schema matching user-requested fields
  5. Cleaning Agent       →  Normalizes whitespace, formats currencies/dates, dedupes rows
  6. Validation Agent     →  Scores data confidence (0.0–1.0) and flags missing cells
  7. Memory Agent         →  Caches dataset in Redis for zero-latency follow-up queries
  8. Conversation Agent   →  Performs instant in-memory filtering, sorting, or reshaping
  9. Export Agent         →  Generates sanitized CSV, Excel (.xlsx), JSON, Markdown, or PDF

Result: Delivered directly in the interactive Chat HUD. Done.
```

---

## 🤖 The 9-Agent Pipeline

The core engine is orchestrated by `apps/backend/agents/orchestrator.py`, dispatching state across nine specialized agents calling Groq (LLaMA 3 70B) with automatic multi-key pool rotation (`ai/key_manager.py`).

| # | Agent | Role | Functionality |
|---|---|---|---|
| 1 | 🧭 **Planner** | Orchestrator | Interprets user intent, determines if a new scrape or cache query is needed, and outputs a JSON workflow plan. |
| 2 | 🔬 **Website Analyzer** | Structure | Analyzes minified DOM/HTML structures and detects repeating container cards, tables, or list items. |
| 3 | 🌐 **Browser Automation** | Automation | Drives headless Chromium via Playwright with lazy scrolling, network-idle waiting, and SSRF/DNS-rebinding defenses. |
| 4 | 📦 **Extraction** | Extraction | Maps unstructured HTML chunks into strict, typed JSON schema objects. |
| 5 | 🧹 **Cleaning** | Data Quality | Dedupes rows, normalizes messy currencies and dates, and resolves relative paths to absolute URLs. |
| 6 | ✅ **Validation** | Trust & QA | Computes statistical confidence scores (0.0–1.0) and flags sparse or null fields. |
| 7 | 🧠 **Memory** | Session Store | Caches validated datasets into Upstash Redis (`z1:` compressed) for rapid follow-ups without re-scraping. |
| 8 | 💬 **Conversation** | Follow-ups | Filters, sorts, aggregates, or transforms cached rows in response to conversational follow-up prompts. |
| 9 | 📤 **Export** | Output | Produces formula-sanitized files in CSV (UTF-8 BOM), native Excel (.xlsx), JSON, Markdown, and PDF. |

---

## ✨ Key Features

- **Conversational Extraction HUD:** Complete chat interface built with Next.js 16 and a cinematic glassmorphism dark-mode theme.
- **Audio Interface Sound FX (Cyberpunk HUD Engine):** Zero external audio files — synthesized entirely in real-time using the browser's Web Audio API. Provides acoustic feedback cues for keystroke typing clicks, file uploads, scrape extraction complete fanfare, downloads, login events, and chat deletion confirmation.
- **Full Mobile Responsiveness:** Designed for all screen viewports with responsive slide-over drawer navigation, touch-friendly composer, horizontal scrolling data tables, and mobile-first modals.
- **Diamond Cursor & Micro-Interactions:** Custom ambient glowing diamond cursor with spring physics and reactive component hover states.
- **Multilingual Support:** Understands colloquial prompts in English, Hindi, Telugu, Tamil, and Hinglish.
- **Multi-Format Export Suite:** Download datasets in one click:
  - **CSV:** UTF-8 BOM encoding for seamless Microsoft Excel compatibility.
  - **Excel (.xlsx):** Real multi-column spreadsheet workbooks.
  - **JSON:** Pretty-printed structured records for developers.
  - **Markdown:** Clean tables ready to paste into GitHub or documentation.
  - **PDF:** Print-ready tables generated client-side via jsPDF.
- **Document & Multi-Modal Uploads:** Extract directly from uploaded CSV, Excel, Word (`.docx`), PDF documents, or screenshots up to 20MB.
- **Session Organization & Inline Rename:** Edit chat session titles directly from the sidebar with keyboard shortcuts (`Enter` to save, `Esc` to cancel).
- **Public Product Suite:**
  - `/how-it-works` — Interactive visual architecture breakdown of the 4-step workflow.
  - `/features` — Feature matrix and comparison against traditional scraping scripts.
  - `/docs` — REST API endpoint specification, quickstart, and tech stack details.
  - `/creators` — Dedicated team showcase for the project maintainers.
- **Live System Status Widget:** IRIS-inspired 4-column footer featuring real-time API operational status, swarm health, and social links.
- **Intelligent URL Accessibility Classifier:** Distinguishes public vs. private or authenticated-only URLs (e.g. ChatGPT conversation sessions, Instagram login walls, internal dashboards, and OAuth portals). Gracefully explains access boundaries and guides the user toward public web pages without throwing raw exceptions, freezing, or returning corrupted rows.
- **Flexible Authentication:** Email/Password with verification, Google OAuth (popup modal UX), and instant Guest Mode (no sign-up required).
- **SEO & Search Console Integration:** Complete OpenGraph metadata, Twitter cards, and Google Search Console site verification.

---

## 💻 Tech Stack

```
Frontend:
  Framework     →  Next.js 16 (App Router · Turbopack) + React 19
  Language      →  TypeScript
  State         →  Zustand (In-memory reactive state)
  Styling       →  Tailwind CSS v4 (Custom dark glassmorphism "HUD" theme)
  Data Tables   →  TanStack Table v8
  Icons         →  Lucide React

Backend:
  Framework     →  FastAPI (Python 3.11+, async, Uvicorn)
  ORM & DB      →  SQLModel + SQLAlchemy (asyncpg)
  Database      →  PostgreSQL on Neon Serverless
  Session Store →  Redis on Upstash (z1 zlib payload compression)
  Job Queue     →  Durable Redis worker for background tasks
  AI Provider   →  Groq (LLaMA 3 70B) with automatic multi-key rotation pool
  Browser       →  Playwright (Headless Chromium)
  Email Service →  Brevo HTTPS API & SMTP fallback

Deployment:
  Frontend      →  Vercel (Edge network, automated CI/CD)
  Backend API   →  Render (Docker web service with /health probe)
  Queue Worker  →  Render (Background worker running workers.scrape_worker)
```

---

## 🔒 Security & Architecture Hardening

WEBISCRAP has undergone rigorous end-to-end security audits:

- **In-Memory Access Tokens:** Access tokens live strictly in JavaScript memory (never in `localStorage` or `sessionStorage`), protecting against XSS token exfiltration.
- **HttpOnly Refresh Rotation:** Refresh tokens are stored strictly in `httpOnly`, `SameSite=Lax`, secure cookies with silent rotation and JTI blacklisting on every refresh.
- **Fail-Closed Session Authorization:** Every session-scoped endpoint validates ownership before returning data, rejecting unowned or foreign session IDs.
- **SSRF & DNS-Rebinding Protection:** Target URLs are resolved and validated against RFC 1918 private ranges, carrier-grade NAT / cloud metadata (`100.64.0.0/10`), localhost, and link-local metadata (`169.254.169.254`). Headless browser subresources enforce fail-closed DNS pin checks.
- **Formula Injection Defense:** All spreadsheet cell contents and dynamic column headers starting with formula characters (`=`, `+`, `-`, `@`, `\t`, `\r`) are sanitized before CSV/XLSX generation.
- **Upload Hardening & Resource Bounding:** Magic-byte header inspection, strict file-extension allowlists, 60s OCR timeout guards, and 20MB file size limits with streaming HTTP chunk bounding.
- **OAuth Nonce CSRF Protection:** Cryptographic client-side nonce generation and server-side validation preventing token replay and CSRF injection.
- **High-Integrity Audit Logging:** Production log streaming formatted as strict JSON with newline-injection sanitization on correlation `X-Request-ID` headers.
- **Readiness Probe Rate-Limiting & Error Redaction:** Protects `/health/ready` against probe enumeration (30 req/min sliding window per IP) while redacting raw internal exceptions in production.

---

## 🎯 Project Milestones & Roadmap

- [x] **Milestone 1 — Core Agent Engine & Architecture (Commits #1 – #30):** 9-agent pipeline, Groq LLaMA 3 70B integration, and Redis session memory.
- [x] **Milestone 2 — Full-Stack Integration & Production Deployment (Commits #31 – #60):** Next.js 16 frontend on Vercel, FastAPI on Render, Neon PostgreSQL, and Upstash Redis.
- [x] **Milestone 3 — Multi-Modal Uploads, Exports & Audio Synthesis (Commits #61 – #90):** Document extraction (PDF, DOCX, CSV, Excel, OCR), Web Audio sound FX engine, mobile pass, and export suite.
- [x] **Milestone 4 — Security Audit & Hardened Production Readiness (Commits #91 – #98):** Forensic vulnerability fixes, private/authenticated URL detection, SSRF & formula injection guards, and zero-defect test pass (84 backend tests, 7 store tests, Next.js build).
- [ ] **Milestone 5 — 100th Commit Celebration & Final Release (Commit #100):** Comprehensive end-to-end release documentation, demo walkthrough, and capstone submission readiness.

---

## 📁 Folder Structure

```
webiscrap/
│
├── apps/
│   ├── frontend/                       # Next.js 16 UI Application
│   │   ├── src/
│   │   │   ├── app/
│   │   │   │   ├── (marketing)/        # Public landing, /how-it-works, /features, /docs, /creators, /terms, /privacy
│   │   │   │   ├── (auth)/             # /login, /signup, /forgot-password, /reset-password, /verify-email
│   │   │   │   ├── (app)/              # /chat/[sessionId], /dataset/[sessionId], /limit
│   │   │   │   └── globals.css         # Tailwind v4 HUD glassmorphism design tokens
│   │   │   ├── components/
│   │   │   │   ├── auth/               # SocialAuth (Google popup UX), AuthCard
│   │   │   │   ├── chat/               # Composer, MessageBubble, PipelineStrip, DataCard
│   │   │   │   ├── dataset/            # DataTable, ExportPanel
│   │   │   │   ├── marketing/          # MarketingNavbar, MarketingFooter (IRIS status card)
│   │   │   │   ├── sidebar/            # Sidebar with inline session rename and deletion
│   │   │   │   └── ui/                 # Button, Card, Input, Chip, Divider
│   │   │   ├── lib/
│   │   │   │   ├── api/client.ts       # ApiClient with in-memory token & silent refresh
│   │   │   │   ├── store/chat.ts       # Zustand reactive chat and session store
│   │   │   │   ├── audio.ts            # Web Audio API sound synthesis engine (typing, cues)
│   │   │   │   └── export.ts           # Multi-format export engine (CSV, XLSX, JSON, PDF)
│   │   │   └── styles/
│   │   └── package.json
│   │
│   └── backend/                        # FastAPI REST API & Worker Engine
│       ├── agents/                     # 9-Agent Pipeline (orchestrator, planner, memory_agent, ...)
│       ├── ai/                         # Groq LLM client, key rotation pool manager
│       ├── api/                        # Route handlers (auth_routes, chat, scrape, export, upload)
│       ├── auth/                       # JWT tokens, Google OAuth, Email service (Brevo HTTPS)
│       ├── core/                       # App config, rate limiter, audit logger, health checks
│       ├── database/                   # PostgreSQL async connection (SQLModel)
│       ├── memory/                     # Redis session store (z1 compression, JTI blacklist)
│       ├── models/                     # User, BaseUUIDModel SQLModel schemas
│       ├── parsers/                    # PDF, DOCX, CSV, Excel, and OCR document parsers
│       ├── prompts/                    # Specialized system prompts per agent
│       ├── workers/                    # Durable Redis scrape worker
│       ├── main.py                     # FastAPI entry point
│       └── requirements.txt
│
├── dev.py                              # Local multi-service runner (Frontend + Backend)
├── render.yaml                         # Render Blueprint (API service + Queue worker)
├── vercel.json                         # Vercel security headers & rewrite config
├── .env.example                        # Template for environment variables
└── README.md
```

---

## 🎯 Milestones & Roadmap

WEBISCRAP is actively engineered with continuous development cycles. We are currently marching toward our **100th Commit Milestone**! 🚀

```
[██████████████████████████████████████████░░░░░░░░] 92% Completed
Current Status: Commit #92 (Documentation & Architecture Update)
Target Milestone: Commit #100 (v1.0 Production Gold Release)
```

| Phase | Commits | Focus Areas | Status |
|---|---|---|---|
| **Phase 1: Foundation** | `#1` – `#25` | Monorepo setup, Next.js 16 scaffolding, FastAPI REST structure, basic database schemas | ✅ Completed |
| **Phase 2: Agent Swarm** | `#26` – `#50` | 9-Agent pipeline orchestration, Groq LLaMA 3 70B integration, multi-key rotation pool | ✅ Completed |
| **Phase 3: State & Hardening** | `#51` – `#70` | Upstash Redis `z1` compressed cache, SSRF/DNS-rebinding guards, JWT HttpOnly auth | ✅ Completed |
| **Phase 4: HUD & Experience** | `#71` – `#85` | Glassmorphism HUD theme, TanStack tables, multi-format exports (CSV/XLSX/JSON/PDF) | ✅ Completed |
| **Phase 5: Audio, Mobile & SEO** | `#86` – `#92` | Web Audio sound FX synthesis, full mobile responsiveness pass, SEO verification | ✅ Completed |
| **Phase 6: Countdown to 100** | `#93` – `#99` | Performance profiling, E2E stress testing, final UI micro-polish & release prep | 🔄 Active |
| **Phase 7: Century Milestone** | `#100` | 🌟 **Official v1.0 Production Gold Release Celebration** | 🎯 Next Up |

---

## 🔧 Prerequisites

- **Python** 3.11+
- **Node.js** v20+
- **Git**
- **Groq API Key(s)** — [console.groq.com](https://console.groq.com) (free)
- **PostgreSQL Database** — [Neon](https://neon.tech) (free tier managed PostgreSQL)
- **Redis Cache** — [Upstash](https://upstash.com) (free tier managed Redis)
- **Brevo API Key** (optional, for transactional verification emails) — [brevo.com](https://www.brevo.com)

---

## 🚀 Installation & Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/manoj-n-dev/WEBISCRAP.git
cd WEBISCRAP

# Alternate team mirror:
# git clone https://github.com/team3c23/WEBISCRAP.git
```

### 2. Set Up the Backend

```bash
cd apps/backend
python -m venv venv

# Windows:
.\venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

### 3. Set Up the Frontend

```bash
cd ../frontend
npm install
```

### 4. Configure Environment Variables

In the project root, copy `.env.example` to `.env`:

```bash
cd ../..
cp .env.example .env
```

Edit `.env` with your database URL, Redis URL, and Groq API keys.

### 5. Quick Launch

Run both the frontend and backend concurrently using the root dev runner:

```bash
python dev.py
```

- **Frontend:** `http://localhost:3000`
- **Backend API:** `http://localhost:8000`
- **API Documentation:** `http://localhost:8000/docs`

---

## ⚙️ Environment Configuration

Example `.env` configuration:

```env
# AI Provider (Groq) — comma-separated keys for auto-rotation
GROQ_API_KEYS=gsk_key1,gsk_key2,gsk_key3

# Database (Neon PostgreSQL)
DATABASE_URL=postgresql+asyncpg://neondb_owner:password@ep-host.us-east-2.aws.neon.tech/neondb?ssl=require

# Cache & Session Store (Upstash Redis)
REDIS_URL=rediss://default:password@host.upstash.io:6379

# JWT Security
JWT_SECRET=your_super_secret_random_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email Provider (Brevo HTTPS API recommended for production)
EMAIL_PROVIDER=auto
BREVO_API_KEY=xkeysib-your_brevo_key_here
EMAILS_FROM_EMAIL=noreply@webiscrap.com
EMAILS_FROM_NAME=WEBISCRAP

# Security & CORS
FRONTEND_URL=http://localhost:3000
BACKEND_CORS_ORIGINS=http://localhost:3000,https://webiscrap.vercel.app
RATE_LIMIT_PER_MINUTE=20
```

---

## 🌐 Production Deployment

WEBISCRAP is architected for zero-downtime deployment:

### Backend on Render (`render.yaml`)
1. Connect your repository to [Render](https://render.com).
2. Create a new **Blueprint** from `render.yaml`. Render provisions:
   - `webiscrap-api` — FastAPI Docker container with automatic `/health` monitoring.
   - `webiscrap-worker` — Background worker running `python -m workers.scrape_worker`.
3. Add environment variables in the Render dashboard.

### Frontend on Vercel (`vercel.json`)
1. Import the repository on [Vercel](https://vercel.com) and set the root directory to `apps/frontend`.
2. Add `NEXT_PUBLIC_API_URL` pointing to your Render service.
3. Deploy — security headers and route rewrites are applied automatically.

---

## 👨‍💻 Team

WEBISCRAP was conceptualized, engineered, and deployed as a Final Year Capstone Project by:

| Name | Role | Primary Focus |
|---|---|---|
| **Manoj N** | Project Lead & Full-Stack Architect | System Architecture, FastAPI Orchestrator, Next.js 16 UI, Deployment |
| **Bhavya** | AI Pipeline Engineer | 9-Agent Prompt Workflows, Groq Key Pool, LLM Schema Alignment |
| **Lohit** | Backend & Distributed Cache Engineer | Redis Session Memory, `z1` Compression, Async Queue Workers |
| **Sushanth** | Frontend UI/UX Engineer | TanStack Table, Export Engine (CSV/XLSX/PDF), Dark HUD Theme |
| **Muni Bharath** | Security & QA Engineer | SSRF/DNS Rebinding Guards, Token Blacklisting, E2E Workflow Testing |

- **Primary Repository:** [github.com/manoj-n-dev/WEBISCRAP](https://github.com/manoj-n-dev/WEBISCRAP)
- **Team Organization:** [github.com/team3c23/WEBISCRAP](https://github.com/team3c23/WEBISCRAP)

---

## 📜 License

All Rights Reserved © 2026 WEBISCRAP. See [LICENSE](LICENSE) for details.

---

<div align="center">
  <sub>Built with ❤️ by Manoj &amp; Team</sub>
</div>