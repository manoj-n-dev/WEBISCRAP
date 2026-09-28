# WEBISCRAP Frontend

Next.js 16 (App Router) glassmorphism HUD interface for WEBISCRAP — an AI-powered multi-agent intelligent web data extraction platform.

---

## 💻 Tech Stack

- **Framework:** Next.js 16 (App Router, Turbopack) + React 19
- **Language:** TypeScript
- **State Management:** Zustand (reactive in-memory store)
- **Styling:** Tailwind CSS v4 (Cinematic glassmorphism dark-mode HUD)
- **Data Tables:** TanStack Table v8
- **Audio Synthesis:** Real-time Web Audio API sound FX engine (zero external audio assets)
- **Export Formats:** CSV (UTF-8 BOM), native Excel (.xlsx), JSON, Markdown, PDF (jsPDF)

---

## 📁 Directory Structure

```
src/
├── app/
│   ├── (marketing)/    # Public pages: landing, /how-it-works, /features, /docs, /creators, /terms, /privacy
│   ├── (auth)/         # Auth flows: /login, /signup, /forgot-password, /reset-password, /verify-email
│   ├── (app)/          # Core workspace: /chat/[sessionId], /dataset/[sessionId], /limit
│   ├── layout.tsx      # Root layout with HUD ambient glow and sound engine provider
│   └── globals.css     # Tailwind v4 glassmorphism tokens
├── components/
│   ├── auth/           # SocialAuth (Google popup modal UX), AuthCard
│   ├── chat/           # Composer, MessageBubble, PipelineStrip, DataCard
│   ├── dataset/        # DataTable (TanStack), ExportPanel
│   ├── marketing/      # MarketingNavbar, MarketingFooter (IRIS status card)
│   ├── sidebar/        # Session sidebar with inline title rename and deletion
│   └── ui/             # Reusable HUD primitives (Button, Card, Input, Chip, Modal)
├── lib/
│   ├── api/client.ts   # ApiClient with in-memory tokens and silent refresh rotation
│   ├── store/chat.ts   # Zustand reactive session, message, and dataset state
│   ├── audio.ts        # Synthesized sound effects (keystrokes, extraction fanfare, download cues)
│   └── export.ts       # Client-side multi-format dataset export engine
└── tests/
    └── store.behavior.test.ts  # End-to-end frontend store verification suite
```

---

## 🚀 Getting Started

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Create `.env.local` in `apps/frontend`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

---

## 🧪 Available Scripts

| Command | Description |
|---|---|
| `npm run dev` | Starts local Next.js development server with Turbopack |
| `npm run build` | Builds the production bundle |
| `npm run start` | Runs the production build server |
| `npm run lint` | Runs ESLint code quality checks |
| `npm run test:store` | Executes the 7 frontend store behavior tests |
