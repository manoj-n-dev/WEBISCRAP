 # Product Requirements Document (PRD)
## WEBISCRAP — AI-Powered Multi-Agent Intelligent Web Data Extraction Platform

**Tagline:** Extract Anything. Ask Naturally. Export Instantly.

**Document Version:** 1.0
**Status:** Draft for Build


---

## 1. Executive Summary

WEBISCRAP is a conversational, AI-powered web data extraction platform that replaces traditional scraping workflows (CSS selectors, XPath, brittle scripts) with natural language. A user pastes one or more URLs (or uploads a file), describes what they want in plain language — in English or a regional/mixed language — 

1. **Agent Orchestrator**  
   - Implements the specialized logic for Planner, Analyzer, Browser, Extractor, Cleaner, Validator, Memory, and Conversation Agents.
   - Built in Python (FastAPI).
2. **AI Provider Fallback (Groq + Groq)**  
   - **Groq (llama-3.3-70b-versatile)**: Fast reasoning, conversation, workflow decisions.
   - **Groq LLaMA (groq-3.5-flash)**: Heavy extraction, visual analysis, structure generation.
   - Key Manager automatically load-balances and cycles keys when limits are hit.

The core differentiator is **session-aware intelligence**: once a website has been scraped, the resulting dataset is cached in the session. Follow-up questions ("show only Dell laptops," "sort by rating," "export only 5-star items") are answered from cached data instead of triggering a new scrape, making the product feel instant and conversational rather than transactional.

---

## 2. Problem Statement

| Problem | Current State | WEBISCRAP Solution |
|---|---|---|
| Writing scrapers requires code | Users need CSS selectors, XPath, or Python/JS scripting knowledge | Natural language replaces all selector logic |
| Websites change structure often | Selector-based scrapers break silently | AI re-analyzes DOM per request; no hardcoded selectors to break |
| JS-heavy sites are hard to scrape | Static scrapers fail on React/Vue/SPA sites | Playwright-driven browser automation renders JS before extraction |
| Repeated scraping wastes time/cost | Every question re-hits the website | Session memory caches datasets; follow-ups use cached data |
| Non-English speakers are underserved | Scraping tools are English-only | Multi-language (Telugu, Hindi, Tamil, Hinglish, etc.) prompt understanding |
| Output is unstructured | Manual copy-paste from pages | One-click export to CSV, Excel, JSON, Markdown, PDF |

---

## 3. Product Vision & Philosophy

**Traditional scraper flow:**
Write Selectors → Scrape HTML → Hope Website Doesn't Change

**WEBISCRAP flow:**
Paste URL → Ask AI → Multi-Agent Reasoning → Dynamic Browser Automation → Structured Results → Conversation Continues

The guiding philosophy: **scraping is a side effect of conversation, not the main interaction.**

---

## 4. Goals & Objectives

### 4.1 Primary Goal
Build an intelligent web scraping platform capable of understanding natural language, handling both static and dynamic (JS-heavy) websites, remembering extracted data per session, supporting follow-up questions without re-scraping, and exporting structured datasets — all through a single conversational interface.

### 4.2 Key Objectives
1. Eliminate the need to write CSS selectors or scraping code.
2. Make web scraping accessible to non-programmers.
3. Support fully conversational, multi-turn data extraction.
4. Handle modern JavaScript-heavy websites (SPA, AJAX, infinite scroll).
5. Provide reusable, structured datasets in standard export formats.
6. Enable AI-powered post-processing (filtering, sorting, comparing, summarizing) on already-extracted data.
7. Minimize redundant scraping through session-level caching and memory.

### 4.3 Non-Goals (Out of Scope for v1)
- Scraping content behind paywalls or requiring bypass of anti-bot/CAPTCHA systems.
- Violating a target site's robots.txt or terms of service.
- Building a visual no-code selector/point-and-click builder (explicitly avoided — natural language only).
- Multi-tenant enterprise admin dashboards, analytics, or team billing (future scope).
- Shadow DOM support (explicitly deferred to a future release).

---

## 5. Target Users & Personas

| Persona | Description | Primary Need |
|---|---|---|
| **Non-technical researcher** | Market analyst, student, journalist with no coding background | Extract structured data without learning to code |
| **Indie developer / builder** | Wants quick structured data for a side project or MVP | Fast extraction without building a custom scraper per site |
| **Small business owner** | Needs competitor price monitoring, lead lists, etc. | Simple, repeatable extraction with exports for spreadsheets |
| **Regional-language user** | Comfortable in Telugu/Hindi/Tamil/Hinglish rather than English | Ability to issue requests in their native or mixed language |
| **Power user / analyst** | Needs to filter, compare, and summarize large extracted datasets | Fast follow-up querying without re-scraping |

---

## 6. Core User Stories

1. *As a user*, I want to paste a URL and describe what I need in plain language, so that I don't have to learn scraping syntax.
2. *As a user*, I want to ask follow-up questions about already-extracted data (filter, sort, compare) without waiting for a new scrape.
3. *As a user*, I want to extract data from JavaScript-heavy websites (React/Vue/Angular/SPA) the same way I would from a static page.
4. *As a user*, I want to type my request in Telugu, Hindi, Tamil, or Hinglish and have it understood correctly.
5. *As a user*, I want to upload a file (PDF, DOCX, CSV, HTML, image) instead of a URL and get the same conversational extraction experience.
6. *As a user*, I want to export my results to CSV, Excel, JSON, Markdown, or PDF with one click.
7. *As a user*, I want my session to persist so I can return later and continue querying the same dataset.
8. *As a returning user*, I want to sign in via Email/Password, Google OAuth, or Phone OTP, or use Guest Mode for a quick trial.
9. *As a user*, I want to know when the AI is planning, browsing, extracting, or cleaning, via live progress indicators, so the process doesn't feel like a black box.
10. *As a user*, I want confidence scores or flags on extracted data so I know when something might be incomplete or unreliable.

---

## 7. Core Product Experience

### 7.1 ChatGPT-Style Interface
There is no traditional dashboard. The chat interface **is** the application. Flow:

```
Paste URL / Upload File
        ↓
Type Natural-Language Request
        ↓
Watch Live Agent Progress (Planning → Analyzing → Extracting → Cleaning → Validating)
        ↓
Receive Structured Data (table + download options)
        ↓
Continue Asking Follow-Up Questions
        ↓
Export Results
```

There is no analytics dashboard, no chart-heavy admin panel — the Chat page is the product.

### 7.2 Session-Aware Intelligence (Core Innovation)

After the first scrape, the extracted dataset is cached in the user's session. Subsequent requests are served from cache unless the user explicitly asks to re-scrape.

**Example conversation:**

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

This session memory is what separates WEBISCRAP from single-shot scraping tools — the value compounds with every follow-up question instead of resetting.

---

## 8. Functional Requirements

### 8.1 Authentication
- Email & Password
- Google OAuth
- Phone Number OTP (via Firebase Authentication)
- Guest Mode (optional, limited-session trial access)

### 8.2 Session Management
Each authenticated (or guest) session isolates and stores:
- Current conversation history
- Website URL(s) associated with the session
- Uploaded files
- Scraped/cached datasets
- AI responses
- User preferences
- Export history
- Temporary extraction cache

Sessions allow continued querying of already-extracted data without triggering another scrape unless explicitly requested by the user.

### 8.3 Cookie Support
- Session cookies
- Persistent cookies
- Authentication cookies (for sites requiring logged-in state)
- Cookie import/export (future release)
- Cookie-aware browsing during automated scraping, always respecting user-provided authentication and target-site policies.

### 8.4 Supported Inputs
Website URL(s), plus uploaded: HTML, PDF, DOCX, TXT, CSV, Excel, JSON, XML, Markdown, ZIP archives, and images (via OCR). The system auto-detects input type and routes to the correct parser.

### 8.5 Dynamic Website Support
Must correctly render and extract from:
- React, Next.js, Vue, Angular, Svelte
- Single Page Applications (SPA)
- AJAX-driven content
- Lazy loading
- Infinite scroll
- Dynamic pagination
- Login-gated pages (using user-supplied credentials/cookies)
- Modal popups
- Shadow DOM — explicitly **deferred to a future release**

### 8.6 Multi-Language Prompt Understanding
The AI must correctly interpret requests in English, Telugu, Hindi, Tamil, Kannada, Malayalam, Bengali, Marathi, Gujarati, Urdu, Hinglish, and mixed-language input.

Examples:
- "ఈ website లో laptop prices తీసుకో." → Extract laptop prices from this website.
- "Is website se sare emails nikal do." → Extract all emails from this website.

### 8.7 Export Formats
CSV, Excel, JSON, Markdown, PDF, and clipboard-ready tables.

---

## 9. Multi-Agent Architecture

WEBISCRAP is powered by nine specialized agents that collaborate on every request. This is the technical heart of the product.

| # | Agent | Responsibilities |
|---|---|---|
| 1 | **Planner Agent** | Interprets user intent; decides required data, tools, and extraction strategy; builds the execution workflow. |
| 2 | **Website Analyzer Agent** | Analyzes DOM, HTML/CSS/JS; detects page structure, repeating content blocks, and layout patterns. |
| 3 | **Browser Automation Agent** | Drives Playwright: launches browser, navigates, clicks, scrolls, waits for JS to settle, captures rendered DOM. |
| 4 | **Extraction Agent** | Extracts titles, prices, tables, reviews, images, links, emails, phone numbers, metadata, FAQs, product details, articles, contact info. |
| 5 | **Cleaning Agent** | Removes duplicates and empty values; normalizes formatting; fixes broken URLs; cleans extracted text. |
| 6 | **Validation Agent** | Checks completeness; validates extracted fields; assigns confidence scores; flags missing/uncertain information. |
| 7 | **Memory Agent** | Stores extracted datasets and chat history; manages session context; enables follow-ups; prevents unnecessary re-scraping. |
| 8 | **Conversation Agent** | Answers questions about already-extracted data (filtering, comparisons, summaries, counts) without re-scraping. |
| 9 | **Export Agent** | Generates CSV, Excel, JSON, Markdown, PDF, and clipboard-ready outputs. |

### 9.1 Agent Orchestration Flow

```
User Request
   ↓
Planner Agent (intent + strategy)
   ↓
Website Analyzer Agent (DOM structure)
   ↓
Browser Automation Agent (render + capture)
   ↓
Extraction Agent (pull requested fields)
   ↓
Cleaning Agent (normalize)
   ↓
Validation Agent (confidence scoring)
   ↓
Memory Agent (cache dataset + context)
   ↓
Conversation Agent (answer / respond to user)
   ↓
Export Agent (on demand)
```

For follow-up queries where data already exists in session memory, the flow short-circuits directly to the **Conversation Agent**, skipping the Analyzer, Browser, Extraction, Cleaning, and Validation steps entirely.

---

## 10. Sample Session-Aware Interactions

- Only show laptops under ₹60,000.
- Sort by rating.
- Which products have free shipping?
- Create a summary.
- Export only Dell products.
- Count the number of HP laptops.
- Compare Dell vs Lenovo prices.
- Find duplicate products.
- Show only 5-star ratings.
- Convert prices from USD to INR.

All of the above operate on cached session data rather than re-scraping the source website.

---

## 11. AI Providers & Reliability

WEBISCRAP uses a **dual AI-provider architecture** to maximize performance, reliability, and availability. Instead of relying on a single LLM provider, the platform intelligently distributes tasks between **Groq** and **Groq Cloud (Groq)** based on their strengths.

### 11.1 AI Provider Responsibilities

#### Groq
Groq is optimized for ultra-fast inference and is primarily responsible for:

- Planner Agent
- Conversation Agent
- Validation Agent
- Intent Understanding
- Workflow Planning
- Follow-up Conversation Handling
- Session Memory Queries
- Fast Reasoning Tasks
- General Chat Responses

#### Groq Cloud (Groq)

Groq is optimized for large-context understanding and complex data processing. It is primarily responsible for:

- Website Analysis
- Extraction Agent
- Cleaning Agent
- Long-context Processing
- Data Summarization
- Multi-language Understanding
- Structured Data Generation
- Large Document Analysis
- Complex Information Extraction

By assigning tasks according to each provider's strengths, WEBISCRAP achieves faster responses, better extraction quality, improved multilingual performance, and higher overall reliability.

---

### 11.2 API Key Management

WEBISCRAP maintains a centralized **API Key Manager** with a pool of:

- 10 Groq API Keys
- 10 Groq Cloud (Groq) API Keys

The API Key Manager automatically:

- Detects quota exhaustion
- Detects rate limits
- Monitors provider health
- Rotates API keys automatically
- Switches providers when necessary
- Retries failed requests
- Applies exponential backoff
- Tracks usage statistics
- Handles cooldown periods
- Restores expired keys automatically

The entire process is seamless and invisible to the user.

---

### 11.3 Key Rotation Workflow

#### Groq Rotation

```
Groq Key 1
      ↓
Quota Exceeded
      ↓
Groq Key 2
      ↓
Groq Key 3
      ↓
Groq Key 4
      ↓
Groq Key 5
      ↓
Groq Key 6
      ↓
Groq Key 7
      ↓
Groq Key 8
      ↓
Groq Key 9
      ↓
Groq Key 10
```

If all Groq keys become unavailable due to quota limits or temporary failures, the system automatically switches to the Groq provider.

```
Groq Pool Exhausted
        ↓
Switch to Groq Pool
```

---

#### Groq Rotation

```
Groq Key 1
      ↓
Quota Exceeded
      ↓
Groq Key 2
      ↓
Groq Key 3
      ↓
Groq Key 4
      ↓
Groq Key 5
      ↓
Groq Key 6
      ↓
Groq Key 7
      ↓
Groq Key 8
      ↓
Groq Key 9
      ↓
Groq Key 10
```

If all Groq keys are also exhausted, the API Key Manager waits until the earliest key's quota resets and automatically resumes processing.

---

### 11.4 Intelligent Provider Selection

Rather than sending every request to a single model, WEBISCRAP intelligently routes tasks to the most suitable AI provider.

| Task | Preferred Provider |
|------|--------------------|
| Planner Agent | Groq |
| Conversation Agent | Groq |
| Validation Agent | Groq |
| Intent Understanding | Groq |
| Follow-up Queries | Groq |
| Session Memory | Groq |
| Website Analyzer | Groq |
| Extraction Agent | Groq |
| Cleaning Agent | Groq |
| Large Context Processing | Groq |
| Data Summarization | Groq |
| Multi-language Understanding | Groq |
| Complex Structured Extraction | Groq |

This intelligent routing balances workload across providers while leveraging the unique strengths of each model.

---

### 11.5 Reliability Strategy

The API Key Manager continuously monitors both providers and automatically:

- Detects failed API requests
- Detects quota exhaustion
- Detects temporary outages
- Detects high response latency
- Switches to the next available API key
- Switches to the alternate provider if necessary
- Retries failed requests with exponential backoff
- Maintains detailed logs for monitoring and debugging

This architecture ensures high availability, minimizes downtime, and provides a consistent user experience even during provider-specific outages or quota limitations.

---

## 12. Non-Functional Requirements

| Category | Requirement |
|---|---|
| **Performance** | Streaming AI responses; live agent-progress indicators during multi-step extraction. |
| **Scalability** | Background job architecture for long-running scrapes; queue-based browser automation to avoid blocking the API. |
| **Reliability** | Automatic API key rotation and retry/backoff on failure; error recovery at each agent stage. |
| **Security** | JWT authentication, refresh tokens, secure cookies, CSRF protection, input/file validation, rate limiting, SQL injection & XSS protection, encrypted session storage. |
| **Compliance** | Respect target sites' terms of service and robots.txt where applicable; only use cookies/auth explicitly provided by the user. |
| **Usability** | Fully conversational UX; no manual configuration screens; responsive design; light/dark theme. |
| **Internationalization** | Correct understanding of 10+ languages and mixed-language/code-switched prompts. |
| **Data Retention** | Session-scoped caching with defined expiry; export history retained per user. |

---

## 13. System Architecture

### 13.1 High-Level Architecture

```
┌─────────────────────┐        ┌─────────────────────┐
│   Frontend (Next.js) │  <──>  │   Backend (FastAPI)  │
│  Chat UI, Streaming  │        │  REST API, Auth,      │
│  Uploads, Exports    │        │  Job Orchestration    │
└─────────────────────┘        └──────────┬──────────┘
                                            │
                       ┌────────────────────┼─────────────────────┐
                       ▼                    ▼                     ▼
              ┌────────────────┐   ┌────────────────┐   ┌──────────────────┐
              │ Agent Orchestr.│   │ Browser Layer   │   │ Groq API Layer │
              │ (Planner, etc.)│   │ (Playwright)    │   │ (Key Rotation)   │
              └───────┬────────┘   └────────┬────────┘   └────────┬─────────┘
                      │                     │                     │
                      ▼                     ▼                     ▼
              ┌──────────────────────────────────────────────────────┐
              │        Data Layer: PostgreSQL + Redis (cache)         │
              │  Users, Sessions, Datasets, Exports, Audit Logs       │
              └──────────────────────────────────────────────────────┘
```

### 13.2 Technology Stack

**Frontend**
- Next.js, React, TypeScript
- Tailwind CSS, shadcn/ui
- React Markdown (rendering AI responses)
- TanStack Query (data fetching/caching)

**Backend**
- FastAPI (Python)
- REST API with JWT auth + refresh tokens

**AI**
- Groq LLaMA (AI Studio) — with 10-key rotation pool
- Groq API Key — with 10-key rotation pool

**Scraping / Browser Automation**
- Playwright (dynamic JS rendering)
- BeautifulSoup + lxml (static parsing)

**Authentication**
- Better Auth or Auth.js (NextAuth)
- Google OAuth
- Firebase Authentication (Phone OTP)

**Database**
- PostgreSQL (production) / SQLite (development)
- Neon PostgreSQL (managed hosting)

**Caching**
- Redis (optional, recommended for production session/dataset caching)

**Storage**
- Local storage (dev) / Cloudflare R2 (optional free tier, for uploaded files)

**Deployment**
- Frontend: Vercel
- Backend: Render / Railway / Fly.io (evaluate free-tier limits)
- Database: Neon PostgreSQL

### 13.3 Suggested Folder Structure

```
apps/
 ├── frontend/
 └── backend/

packages/
 ├── agents/
 ├── ai/
 ├── auth/
 ├── browser/
 ├── scraper/
 ├── exporters/
 ├── parsers/
 ├── memory/
 ├── prompts/
 ├── storage/
 ├── shared/

uploads/
exports/
docs/
```

---

## 14. Data Model (Core Entities)

| Entity | Purpose |
|---|---|
| **Users** | Account records; auth method; profile info |
| **Sessions** | Per-user isolated session state and expiry |
| **Conversations** | Chat threads tied to a session |
| **Messages** | Individual chat turns (user + AI) within a conversation |
| **Uploaded Files** | Metadata + storage pointer for user-uploaded documents |
| **Websites** | URLs submitted for scraping, with metadata (domain, last scraped, structure hints) |
| **Scrape Jobs** | Job records tracking agent pipeline execution and status |
| **Cached Datasets** | Structured extraction results tied to a session, used for follow-up queries |
| **Exports** | Generated export files (format, timestamp, source dataset) |
| **API Keys** | Metadata only (key status, cooldown, usage count) — never raw secrets in plaintext logs |
| **Audit Logs** | Security- and compliance-relevant event history |

---

## 15. Frontend Requirements

- ChatGPT-style single-workspace interface (no dashboard)
- Streaming AI responses with live agent-stage indicators (Planning → Analyzing → Extracting → Cleaning → Validating → Done)
- Drag-and-drop file upload
- URL input field
- Persistent conversation history
- Markdown rendering of AI responses and tables
- Download center for exports
- Light/Dark theme switching
- Fully responsive design (desktop + mobile)

**Suggested pages:** `/` (chat home), Login, Register, Chat, History, Settings, Profile. No analytics dashboard — the Chat page is the product.

---

## 16. Backend Requirements

- REST API
- JWT authentication + refresh tokens
- Session management
- Cookie handling (target-site cookies, separate from app auth cookies)
- Rate limiting
- File upload handling with validation
- Background job processing (for scrape jobs)
- AI agent orchestration layer
- Structured logging
- Error recovery and retry logic at each pipeline stage

---

## 17. Security Requirements

- JWT Authentication
- Secure, HttpOnly cookies
- CSRF protection where applicable
- Input validation (all user-submitted text and URLs)
- File validation (type, size, content sniffing for uploads)
- API rate limiting
- SQL injection protection (parameterized queries / ORM)
- XSS protection (sanitized rendering of scraped content)
- Encrypted session storage
- Role-based access control (future)

---

## 18. Success Metrics

| Metric | Target / Signal |
|---|---|
| Time-to-first-extraction | Under 30 seconds for a typical static page |
| Re-scrape avoidance rate | >80% of follow-up queries served from session cache |
| Extraction accuracy | High validation-agent confidence scores on majority of fields |
| Multi-language accuracy | Correct intent parsing across all 10+ supported languages |
| API key rotation reliability | Zero user-facing failures due to quota exhaustion |
| Export success rate | >99% successful export generation across all formats |

---

## 19. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Target website blocks automated browsing / anti-bot measures | Respect robots.txt and ToS; avoid CAPTCHA bypass; fail gracefully with clear user messaging |
| Groq API quota exhaustion across all 10 keys | Implement wait/backoff queue; surface a clear "temporarily rate-limited" state to the user |
| Dynamic site structure changes mid-session | Website Analyzer Agent re-analyzes DOM per scrape rather than relying on hardcoded selectors |
| Ambiguous or mixed-language prompts misinterpreted | Planner Agent falls back to clarifying questions when confidence is low |
| Sensitive data inadvertently scraped (PII, login-gated content) | Validation Agent flags sensitive fields; access to login-gated content requires explicit user-provided credentials/cookies only |
| Cost overrun from repeated full re-scrapes | Session-aware caching is the default behavior; re-scrape only on explicit user request |

---

## 20. MVP Build Plan (Phased)

**Phase 1 — Foundation**
- Auth (Email/Password, Google OAuth, Guest Mode)
- Basic chat UI shell
- FastAPI backend skeleton + PostgreSQL schema
- Single Groq API key integration (rotation deferred)

**Phase 2 — Core Scraping Pipeline**
- Planner Agent + Website Analyzer Agent
- Playwright-based Browser Automation Agent (static + basic dynamic sites)
- Extraction Agent (titles, prices, tables, links, emails)

**Phase 3 — Data Quality & Memory**
- Cleaning Agent + Validation Agent
- Memory Agent + session-based dataset caching
- Conversation Agent for follow-up queries (filter/sort/summarize)

**Phase 4 — Export & Polish**
- Export Agent (CSV, Excel, JSON, Markdown, PDF)
- Multi-language prompt support
- Phone OTP auth
- Theme switching, responsive polish

**Phase 5 — Reliability & Scale**
- 10-key Groq API rotation manager
- Redis caching layer
- Background job queue for long-running scrapes
- Full security hardening pass (rate limiting, CSRF, audit logs)

---

## 21. Open Decisions

1. **Stack tier**: Zero-cost lightweight stack (FastAPI + Playwright + Supabase + Groq/Ollama + Vercel/Render) vs. full production stack (Next.js + PostgreSQL + Redis + Celery + Docker + Elasticsearch) — recommend resolving before implementation begins.
2. **Backend host**: Render vs. Railway vs. Fly.io — depends on free-tier suitability for long-running Playwright browser processes.
3. **Cookie import/export**: Confirmed as a future release, not MVP.
4. **Shadow DOM support**: Confirmed as a future release, not MVP.

---

## 22. Appendix — Example Natural-Language Requests

- "Extract all laptop names, prices, ratings, and images."
- "Find every company email address on this page."
- "Summarize this entire website."
- "ఈ website లో అన్ని laptop prices తీసుకో" (Telugu)
- "Ee website lo anni loq laptops ni tisuko" (Tenglish)
- "Is website ke sare mobile names nikal do" (Hinglish)
- "Show only Dell laptops." (follow-up, no re-scrape)
- "Compare Dell vs Lenovo prices." (follow-up, no re-scrape)
- "Export only 5-star rated products." (follow-up, no re-scrape)

---

# 23. Development Roadmap (2-Month Sprint Plan)

## Development Strategy

The project will follow a **Backend-First Development** approach.

Instead of building the frontend and backend simultaneously, the team will first complete and test the entire backend, including all AI agents, APIs, authentication, session management, database integration, and export functionality.

Once the backend reaches a stable state, the frontend will be developed on top of the completed APIs.

This approach minimizes integration issues, allows independent backend testing, and enables parallel team collaboration.

---

## Duration

Total Duration: **2 Months (8 Weeks)**

Working Days:
- Monday
- Friday

Total Development Sessions:
**16 Sessions**

---

# Week 1

### Monday
- Project setup
- Repository structure
- Backend architecture
- FastAPI setup
- PostgreSQL setup
- Authentication design

### Friday
- User Authentication
- JWT
- Google Login
- Phone OTP
- Session Management

---

# Week 2

### Monday
Agent 1 — Planner Agent

Features:
- Understand user prompts
- Detect extraction intent
- Decide execution workflow
- Select required tools

### Friday
Testing & Integration
- Planner Agent
- API
- Database
- Logging

---

# Week 3

### Monday
Agent 2 — Website Analyzer Agent

Features:
- Analyze DOM
- Detect repeating structures
- Detect tables
- Detect product cards
- Detect pagination

### Friday
Testing
Integration with Planner Agent

---

# Week 4

### Monday
Agent 3 — Browser Automation Agent

Features:
- Playwright
- Dynamic websites
- Infinite scrolling
- Pagination
- JavaScript rendering

### Friday
Testing
Optimization
Error Handling

---

# Week 5

### Monday
Agent 4 — Extraction Agent

Features:
- Products
- Prices
- Images
- Tables
- Emails
- Phone Numbers
- Metadata

### Friday
Agent 5 — Cleaning Agent

Features:
- Remove duplicates
- Clean text
- Normalize data
- Fix URLs

---

# Week 6

### Monday
Agent 6 — Validation Agent

Features:
- Confidence scores
- Missing field detection
- Validation
- Error reporting

### Friday
Agent 7 — Memory Agent

Features:
- Session cache
- Conversation history
- Dataset storage
- Follow-up query support

---

# Week 7

### Monday
Agent 8 — Conversation Agent

Features:
- Filter
- Sort
- Compare
- Summarize
- Follow-up conversations

### Friday
Agent 9 — Export Agent

Features:
- CSV
- Excel
- JSON
- Markdown
- PDF

---

# Week 8

### Monday
Backend Integration

- API Key Manager
- 10 Groq Keys
- 10 Groq Keys
- Retry Logic
- Provider Routing
- Security
- Final Testing

### Friday
Frontend Development

- Chat Interface
- Authentication UI
- File Upload
- URL Input
- Streaming Responses
- Export Buttons
- Deployment
- Final Bug Fixes

---

## Team Workflow

Each AI Agent will be developed independently by assigned team members.

Every completed agent must pass:

- Unit Testing
- Integration Testing
- API Testing
- Performance Testing

before merging into the main branch.

---

## Milestones

Milestone 1
✔ Authentication Completed

Milestone 2
✔ Planner Agent

Milestone 3
✔ Website Analyzer Agent

Milestone 4
✔ Browser Automation Agent

Milestone 5
✔ Extraction Pipeline

Milestone 6
✔ Memory System

Milestone 7
✔ Conversation Engine

Milestone 8
✔ Export Engine

Milestone 9
✔ Backend Completed

Milestone 10
[ ] Frontend Completed

Milestone 11
[ ] Final Integration

Milestone 12
[ ] Production Ready

---

*End of Document.*

