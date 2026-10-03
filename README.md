<div align="center">
  <img src="https://raw.githubusercontent.com/manoj-n-dev/WEBISCRAP/main/apps/frontend/public/assets/branding-logo.png" alt="WEBISCRAP Logo" width="320" />

  <h1>WEBISCRAP</h1>
  <p><strong>Extract Anything. Ask Naturally. Export Instantly.</strong></p>
  <p><em>An autonomous 9-agent AI platform that transforms web scraping into natural, intelligent conversation.</em></p>

  <p>
    <a href="https://webiscrap.vercel.app"><img src="https://img.shields.io/badge/Live%20App-webiscrap.vercel.app-00e5ff?style=for-the-badge&logo=vercel" alt="Live App" /></a>
    <a href="https://webiscrap-api.onrender.com/health"><img src="https://img.shields.io/badge/API-Operational-00ff78?style=for-the-badge&logo=render" alt="API Status" /></a>
    <a href="https://github.com/manoj-n-dev/WEBISCRAP/releases"><img src="https://img.shields.io/badge/Release-v1.0.0%20Gold-8a2be2?style=for-the-badge&logo=github" alt="Release v1.0.0" /></a>
    <a href="#-security--hardening"><img src="https://img.shields.io/badge/Security-Audited%20%26%20Hardened-green?style=for-the-badge&logo=shield" alt="Security Hardened" /></a>
    <a href="#-license"><img src="https://img.shields.io/badge/License-All%20Rights%20Reserved-red?style=for-the-badge" alt="License" /></a>
  </p>
</div>

---

## 🌐 Live Services

| Component | Platform | Status | URL |
|---|---|---|---|
| **Web Application HUD** | Vercel Edge | 🟢 Active | [https://webiscrap.vercel.app](https://webiscrap.vercel.app) |
| **Backend REST API** | Render Cloud | 🟢 Active | [https://webiscrap-api.onrender.com](https://webiscrap-api.onrender.com) |
| **Health Probe** | Render Cloud | 🟢 Operational | [https://webiscrap-api.onrender.com/health](https://webiscrap-api.onrender.com/health) |
| **Primary Repository** | GitHub | 📦 Production | [github.com/manoj-n-dev/WEBISCRAP](https://github.com/manoj-n-dev/WEBISCRAP) |
| **Team Mirror** | GitHub | 📦 Mirrored | [github.com/team3c23/WEBISCRAP](https://github.com/team3c23/WEBISCRAP) |

---

## 📑 Table of Contents

- [Overview](#-overview)
- [How It Works](#-how-it-works)
- [The 9-Agent Pipeline](#-the-9-agent-pipeline)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Security & Hardening](#-security--hardening)
- [Repository Structure](#-repository-structure)
- [Prerequisites](#-prerequisites)
- [Installation & Local Setup](#-installation--local-setup)
- [Environment Configuration](#️-environment-configuration)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [Production Deployment](#-production-deployment)
- [Milestones & Roadmap](#-milestones--roadmap)
- [Team](#-team)
- [License](#-license)

---

## ⚡ Overview

Traditional web scraping workflows require reverse-engineering HTML DOM hierarchies, maintaining brittle CSS selectors or XPath expressions, and rewriting parsers whenever site layouts change.

**WEBISCRAP** fundamentally reimagines data extraction:

> **Scraping is a side effect of natural conversation, not a manual coding task.**

Paste any public website URL or upload a file (PDF, DOCX, CSV, Excel, or screenshot), describe what you need in plain natural language (English, Telugu, Hindi, Tamil, or Hinglish), and an autonomous swarm of **nine specialized AI agents** collaborates to navigate, analyze, extract, clean, validate, and deliver clean structured records in real time.

### Why WEBISCRAP?

- **No CSS Selectors or XPath:** The LLM analyzer identifies data structures semantically from rendered DOM containers.
- **Multilingual Query Understanding:** Understands colloquial prompts across English, Hindi, Telugu, Tamil, and Hinglish.
- **Instant Follow-Up Queries (Zero Re-Scraping):** Validated datasets are cached in Upstash Redis (`z1:` zlib compressed). Subsequent prompts like *"sort by lowest price"* or *"filter ratings > 4.5"* execute in memory with zero re-scraping latency.
- **Intelligent Access Classifier:** Distinguishes public web pages from login-walls (ChatGPT, social networks, OAuth portals), informing users gracefully without errors or corrupted records.
- **Multi-Format Export Suite:** Download clean data with one click in CSV (UTF-8 BOM), native Excel (`.xlsx`), JSON, Markdown, or client-rendered PDF.

---

## 🧠 How It Works

```
User Prompt: "Extract all laptop names, discounted prices, ratings, and image links"
             + Target URL (or uploaded PDF/DOCX/CSV/Excel/Image)
                                     │
                                     ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                         9-AGENT AUTONOMOUS SWARM                            │
 │                                                                             │
 │  1. 🧭 Planner Agent      → Deconstructs prompt; decides scrape vs. cache   │
 │  2. 🔬 Analyzer Agent     → Inspects DOM; discovers repeating card patterns │
 │  3. 🌐 Browser Agent      → Headless Chromium (auto-scroll, network-idle)   │
 │  4. 📦 Extractor Agent    → Extracts strict typed JSON records              │
 │  5. 🧹 Cleaner Agent      → Dedupes, trims, normalizes currency & dates     │
 │  6. ✅ Validator Agent    → Calculates statistical confidence score (0-1)   │
 │  7. 🧠 Memory Agent       → Caches dataset into Redis (z1 compressed)       │
 │  8. 💬 Conversation Agent → Handles conversational filters & transformations│
 │  9. 📤 Export Agent       → Sanitizes formulas & prepares download files    │
 └─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
      Interactive Chat HUD + TanStack Data Table + One-Click Export Suite
```

---

## 🤖 The 9-Agent Pipeline

The core orchestration engine lives in [`apps/backend/agents/orchestrator.py`](apps/backend/agents/orchestrator.py), dispatching state deterministically through nine dedicated agents powered by Groq LLaMA 3 70B with an automated multi-key rotation pool:

| # | Agent | Category | Role & Core Responsibility |
|---|---|---|---|
| 1 | 🧭 **Planner** | Orchestration | Interprets user intent, determines whether to trigger live browsing or query cached memory, and synthesizes a schema plan. |
| 2 | 🔬 **Analyzer** | Structure | Analyzes minified DOM structures, discovers repeating container elements (cards, table rows, list items), and detects access barriers. |
| 3 | 🌐 **Browser** | Automation | Drives headless Chromium via Playwright with smart scrolling, dynamic network-idle waits, and SSRF/DNS-rebinding defenses. |
| 4 | 📦 **Extractor** | Extraction | Maps unstructured HTML/text chunks into strict, typed JSON schema objects matching user fields. |
| 5 | 🧹 **Cleaner** | Quality | Dedupes rows, normalizes messy currencies and dates, and resolves relative links to absolute URLs. |
| 6 | ✅ **Validator** | Integrity | Computes data completeness and statistical confidence scores (0.0–1.0), flagging sparse or null attributes. |
| 7 | 🧠 **Memory** | Session Cache | Stores compressed (`z1:`) datasets into Upstash Redis for instant follow-up conversations without re-scraping. |
| 8 | 💬 **Conversation** | Analytics | Applies in-memory filtering, sorting, column reshaping, and aggregations in response to conversational prompts. |
| 9 | 📤 **Export** | Output | Sanitizes spreadsheet formula injections and generates production-ready CSV, Excel (.xlsx), JSON, Markdown, and PDF. |

---

## ✨ Key Features

### ⚡ Conversational Data Extraction
- **Zero-Code Extraction:** Paste any link and ask in plain words.
- **Multilingual NLP:** Understands prompts in English, Telugu, Hindi, Tamil, and Hinglish.
- **Zero-Latency Follow-ups:** Filter, sort, rank, or aggregate cached datasets conversationally.

### 🛡️ URL Accessibility Classifier
- **Login-Wall Detection:** Automatically detects private sessions, login walls (ChatGPT, Instagram, Gmail), and bot blocks (Cloudflare).
- **Graceful Feedback:** Provides clear, user-friendly guidance instead of raw exceptions or corrupted data.

### 📁 Multi-Modal Document Parsing
- **Document Ingestion:** Upload PDF, DOCX, CSV, Excel (`.xlsx`, `.xls`), and image screenshots up to 20MB.
- **Image OCR:** Embedded Tesseract OCR engine extracts text and tabular structures from images and diagrams.
- **Direct Tabular Mode:** Tabular files bypass LLM round-trips for lossless, instantaneous dataset ingestion.

### 🎧 Cyberpunk HUD Audio Interface
- **Real-Time Sound Synthesis:** Synthesized dynamically via the browser's Web Audio API with zero external audio assets.
- **Acoustic Cues:** Interactive audio feedback for keystroke clicks, file uploads, scrape complete fanfares, and downloads.

### 📊 Multi-Format Export Engine
- **CSV:** UTF-8 BOM encoded for seamless Microsoft Excel compatibility.
- **Excel (.xlsx):** Native multi-column spreadsheet workbooks.
- **JSON:** Formatted, pretty-printed structured arrays for developers.
- **Markdown:** Clean tables ready for GitHub, Notion, or documentation.
- **PDF:** Print-ready tables generated client-side via jsPDF.

### 📱 Responsive Glassmorphism HUD
- **Cinematic Dark Theme:** Built with Tailwind CSS v4 custom tokens, subtle ambient glows, and glassmorphism cards.
- **Adaptive Mobile Layout:** Slide-over navigation drawers, touch-friendly composer, and horizontally scrollable tables.
- **Inline Session Management:** Rename chat session titles directly from the sidebar (`Enter` to save, `Esc` to cancel).

---

## 💻 Tech Stack

```
Frontend:
  Framework        → Next.js 16 (App Router · Turbopack) + React 19
  Language         → TypeScript
  State Management → Zustand (Reactive in-memory store)
  Styling          → Tailwind CSS v4 (Custom HUD glassmorphism design tokens)
  Data Tables      → TanStack Table v8
  Audio Engine     → Web Audio API (real-time synthesizer)
  Icons            → Lucide React

Backend:
  Framework        → FastAPI (Python 3.11+, async/await, Uvicorn)
  ORM & Database   → SQLModel + SQLAlchemy (asyncpg) on Neon PostgreSQL
  Session Memory   → Upstash Redis (z1 zlib compression, atomic claims)
  AI Infrastructure→ Groq (LLaMA 3 70B) with automatic multi-key rotation pool
  Browser Engine   → Playwright (Headless Chromium with DNS pin guards)
  Document Parsers → PyPDF, python-docx, openpyxl, pandas, pytesseract (OCR)
  Email Service    → Brevo HTTPS API with SMTP fallback

Infrastructure & Deployment:
  Frontend Edge    → Vercel (Edge network, global CDN, automated CI/CD)
  Backend Engine   → Render (Dockerized web service with /health probe)
  Background Worker→ Render (Durable Redis scrape queue worker)
```

---

## 🔒 Security & Hardening

WEBISCRAP has undergone extensive security audits and vulnerability remediation:

### Authentication & Session Security
- **In-Memory Access Tokens:** JWT access tokens reside exclusively in JavaScript memory (never in `localStorage` or `sessionStorage`), eliminating XSS token exfiltration risks.
- **HttpOnly Refresh Cookies:** Refresh tokens are restricted to `httpOnly`, `SameSite=Lax`, secure cookies with automatic rotation and JTI blacklisting on logout/refresh.
- **Fail-Closed Session Authorization:** Every session-scoped request validates ownership via Redis atomic claims, rejecting unauthorized access to other users' data.
- **Google OAuth Nonce Protection:** Client-side cryptographic nonce generation and server-side verification prevent token replay and CSRF attacks.

### Network & SSRF Defenses
- **Comprehensive SSRF & DNS-Rebinding Guards:** All target URLs and redirect hops are resolved via `getaddrinfo` and validated against loopback, private ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), carrier-grade NAT / cloud metadata (`100.64.0.0/10`), link-local (`169.254.169.254`), and IPv6-mapped equivalents.
- **Headless Browser Subresource Interception:** Headless Chromium routes resolve and validate all dynamic subresource requests against the same IP whitelist.
- **Reverse-Proxy Client IP Integrity (Anti-Spoofing):** Resolves client IP via proxy-appended `X-Forwarded-For` tail selection behind trusted proxies, preventing rate-limit and audit log spoofing.

### Data Sanitization & Resource Bounding
- **Spreadsheet Formula Injection Defense:** All cell contents and column headers starting with formula triggers (`=`, `+`, `-`, `@`, `\t`, `\r`) are sanitized before CSV/Excel export.
- **Upload Hardening:** Magic-byte header inspection, strict file-extension allowlists, 60s OCR timeout guards, and a 20MB file limit with early `Content-Length` checks.
- **Structured Audit Logging:** Production logs are formatted as strict JSON with newline-injection sanitization on correlation `X-Request-ID` headers.
- **Readiness Probe Rate-Limiting:** Protects `/health/ready` against probe enumeration (30 req/min per IP) while redacting raw internal exceptions in production.

---

## 📁 Repository Structure

```
WEBISCRAP/
├── apps/
│   ├── frontend/                       # Next.js 16 UI Application
│   │   ├── src/
│   │   │   ├── app/                    # Marketing, Auth, and App Route Handlers
│   │   │   ├── components/             # Reusable HUD Primitives, Chat, Dataset, Sidebar
│   │   │   ├── lib/                    # API client, Zustand store, Audio engine, Exporter
│   │   │   └── styles/                 # Global styles & Tailwind v4 design tokens
│   │   ├── tests/                      # Frontend store behavior verification tests
│   │   └── package.json
│   │
│   └── backend/                        # FastAPI REST API & Worker Engine
│       ├── agents/                     # 9-Agent Pipeline Swarm
│       ├── ai/                         # Groq client, Key rotation pool manager
│       ├── api/                        # Route handlers (auth, chat, scrape, export, upload)
│       ├── auth/                       # JWT tokens, Google OAuth, Brevo HTTPS service
│       ├── core/                       # App configuration, rate limiter, audit logger, health
│       ├── database/                   # PostgreSQL async connection (SQLModel)
│       ├── memory/                     # Redis session store (z1 compression, atomic claims)
│       ├── models/                     # SQLModel database schemas (User, Session)
│       ├── parsers/                    # PDF, DOCX, CSV, Excel, and OCR document parsers
│       ├── prompts/                    # Specialized agent system prompts
│       ├── tests/                      # Backend test suites (84 unit & integration tests)
│       ├── workers/                    # Durable Redis scrape queue worker
│       └── main.py                     # FastAPI application entrypoint
│
├── dev.py                              # Local multi-service orchestrator (Frontend + Backend)
├── render.yaml                         # Render Blueprint specification
├── vercel.json                         # Vercel edge deployment configuration
├── .env.example                        # Template for environment variables
└── README.md
```

---

## 🔧 Prerequisites

- **Python:** 3.11+
- **Node.js:** 20+
- **Git**
- **Groq API Key(s):** [console.groq.com](https://console.groq.com) (Free tier supported)
- **PostgreSQL Database:** [Neon Serverless](https://neon.tech) (Free tier managed Postgres)
- **Redis Cache:** [Upstash](https://upstash.com) (Free tier managed Redis)
- **Brevo API Key:** [brevo.com](https://www.brevo.com) (Optional, for transactional emails)

---

## 🚀 Installation & Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/manoj-n-dev/WEBISCRAP.git
cd WEBISCRAP
```

### 2. Backend Setup

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

### 3. Frontend Setup

```bash
cd ../frontend
npm install
```

### 4. Configure Environment Variables

From the project root:

```bash
cd ../..
cp .env.example .env
```

Populate `.env` with your Neon database URL, Upstash Redis URL, and Groq API keys.

### 5. Launch Development Servers

Run both services concurrently using the root orchestrator:

```bash
python dev.py
```

- **Frontend HUD:** `http://localhost:3000`
- **Backend API:** `http://localhost:8000`
- **Interactive API Docs:** `http://localhost:8000/docs`

---

## ⚙️ Environment Configuration

Example `.env` configuration template:

```env
# AI Provider (Groq) — comma-separated keys for auto-rotation
GROQ_API_KEYS=gsk_key1,gsk_key2,gsk_key3

# Database (Neon PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@ep-host.aws.neon.tech/neondb?ssl=require

# Cache & Session Store (Upstash Redis)
REDIS_URL=rediss://default:password@host.upstash.io:6379

# JWT Security
JWT_SECRET=your_super_secret_random_key_of_at_least_32_chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email Provider (Brevo HTTPS API)
EMAIL_PROVIDER=auto
BREVO_API_KEY=xkeysib-your_brevo_key_here
EMAILS_FROM_EMAIL=noreply@webiscrap.com
EMAILS_FROM_NAME=WEBISCRAP

# Security & CORS
FRONTEND_URL=http://localhost:3000
BACKEND_CORS_ORIGINS=http://localhost:3000,https://webiscrap.vercel.app
RATE_LIMIT_PER_MINUTE=60
TRUST_PROXY_HEADERS=False
```

---

## 🧪 Testing & Quality Assurance

WEBISCRAP maintains strict quality gates across both frontend and backend services:

```bash
# 1. Run all backend tests (SSRF, auth, agents, pipelines, parsers)
cd apps/backend
python tests/run_all_tests.py

# 2. Run specific security test suites
python -m unittest tests.test_ssrf_and_proxy -v
python -m unittest tests.test_private_url_handling -v

# 3. Run frontend reactive store behavior suite
cd ../frontend
npm run test:store

# 4. Run TypeScript compilation check
npx tsc --noEmit
```

---

## 🌐 Production Deployment

WEBISCRAP is architected for zero-downtime, continuous deployment:

### Backend on Render (`render.yaml`)
1. Connect your repository to [Render](https://render.com).
2. Create a new **Blueprint** from `render.yaml`. Render automatically provisions:
   - `webiscrap-api` — FastAPI Docker container with automated `/health` probes.
   - `webiscrap-worker` — Background worker running `python -m workers.scrape_worker`.
3. Configure the environment variables in the Render dashboard.

### Frontend on Vercel (`vercel.json`)
1. Import the repository on [Vercel](https://vercel.com) and designate the root directory as `apps/frontend`.
2. Configure `NEXT_PUBLIC_API_URL` pointing to your Render deployment.
3. Deploy — security headers, CSP, and route rewrites apply automatically.

---

## 🎯 Milestones & Roadmap

| Milestone | Release | Key Highlights | Status |
|---|---|---|---|
| **Phase 1: Foundation** | `v0.1.0` | Monorepo scaffolding, FastAPI REST API, Next.js 16 app router, PostgreSQL schemas. | ✅ Completed |
| **Phase 2: Agent Swarm** | `v0.4.0` | 9-agent autonomous pipeline, Groq LLaMA 3 70B integration, multi-key rotation pool. | ✅ Completed |
| **Phase 3: State & Hardening** | `v0.7.0` | Upstash Redis `z1` compressed cache, SSRF/DNS-rebinding guards, HttpOnly refresh cookies. | ✅ Completed |
| **Phase 4: HUD & Experience** | `v0.8.5` | Cyberpunk HUD glassmorphism theme, TanStack data tables, multi-format export suite. | ✅ Completed |
| **Phase 5: Audio & Mobile** | `v0.9.0` | Real-time Web Audio synthesis engine, full responsive mobile drawer navigation, SEO tags. | ✅ Completed |
| **Phase 6: Forensic Audit** | `v0.9.8` | Forensic vulnerability fixes (N1–N11), private URL classifier, proxy anti-spoofing. | ✅ Completed |
| **Phase 7: Gold Release** | `v1.0.0` | 🌟 **Official Production Gold Release** — 84/84 tests passing, zero-defect release. | ✅ Completed |
| **Phase 8: Future Roadmap** | `v1.1+` | Scheduled recurring extractions, webhook integrations, browser extension companion. | 🗺️ Planned |

---

## 👨‍💻 Team

WEBISCRAP was conceptualized, engineered, and deployed as a Final Year Capstone Project by:

| Name | Role | Core Specialization |
|---|---|---|
| **N Manoj** | Project Lead & Full-Stack Architect | System Architecture, FastAPI Orchestrator, Next.js 16 HUD, Cloud Deployment |
| **S Bhavyasree** | AI Pipeline Engineer | 9-Agent Prompt Workflows, Groq Key Pool Rotation, LLM Schema Alignment |
| **Y Lohith Kumar** | Backend & Distributed Cache Engineer | Redis Session Memory, `z1` Compression, Async Queue Workers |
| **A Sushanth Royal** | Frontend UI/UX Engineer | TanStack Table, Multi-Format Export Suite, Dark HUD Glassmorphism |
| **S Muni Bharath** | Security & QA Engineer | SSRF/DNS Rebinding Guards, Anti-Spoofing, E2E Security Test Suites |

- **Primary Repository:** [github.com/manoj-n-dev/WEBISCRAP](https://github.com/manoj-n-dev/WEBISCRAP)
- **Team Mirror:** [github.com/team3c23/WEBISCRAP](https://github.com/team3c23/WEBISCRAP)

---

## 📜 License

All Rights Reserved © 2026 WEBISCRAP. See [LICENSE](LICENSE) for details.

---

<div align="center">
  <sub>Built with ❤️ by Manoj &amp; Team</sub>
</div>