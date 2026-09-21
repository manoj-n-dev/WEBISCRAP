import React from "react";
import type { Metadata } from "next";
import Link from "next/link";
import { MarketingNavbar } from "@/components/marketing/MarketingNavbar";
import { MarketingFooter } from "@/components/marketing/MarketingFooter";
import { WarmUp } from "@/components/system/WarmUp";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import {
  BookOpen,
  Code,
  Terminal,
  Server,
  Layers,
  HelpCircle,
  CheckCircle2,
  FileCode,
  ArrowRight,
  ExternalLink,
} from "lucide-react";

export const metadata: Metadata = {
  title: "Documentation & API | WEBISCRAP",
  description: "Comprehensive documentation, quickstart guide, API reference, and tech stack details for WEBISCRAP.",
};

const endpoints = [
  { method: "POST", path: "/api/chat/", desc: "Submit an extraction prompt or follow-up conversation. Automatically claims or initializes the session." },
  { method: "GET", path: "/api/chat/sessions", desc: "List recent extraction sessions belonging to the authenticated user." },
  { method: "PATCH", path: "/api/chat/{id}/rename", desc: "Rename an existing chat session title for quick organization." },
  { method: "GET", path: "/api/chat/{id}/data", desc: "Fetch the cached structured dataset rows with optional preview limit." },
  { method: "GET", path: "/api/chat/{id}/progress", desc: "Poll live real-time pipeline execution progress (step by step)." },
  { method: "DELETE", path: "/api/chat/{id}", desc: "Prune chat history, cached datasets, and associated attachments." },
  { method: "GET", path: "/api/export/{csv|excel|json|markdown}", desc: "Download the server-sanitized dataset in the specified file format." },
  { method: "POST", path: "/api/upload/", desc: "Attach local documents (PDF, Word, CSV, Excel, Images) up to 20MB." },
];

const faqs = [
  {
    q: "Do I need to write or know CSS selectors or XPath?",
    a: "No. You simply describe what you want in plain natural language (e.g. 'Extract all products with price, title, image, and star rating'). The 9-agent pipeline inspects the DOM and performs semantic mapping automatically.",
  },
  {
    q: "Does WEBISCRAP re-scrape the website when I ask follow-up questions?",
    a: "No. Once a page or document is extracted, the validated dataset is stored in Redis session memory. Follow-ups like 'sort by price ascending' or 'only keep items with in_stock=true' are answered directly from cache with zero delay.",
  },
  {
    q: "What languages can I prompt with?",
    a: "WEBISCRAP's Planner and Extractor agents understand English, Hindi, Telugu, Tamil, Hinglish, and mixed colloquial instructions.",
  },
  {
    q: "How are JavaScript-heavy single-page apps (SPAs) handled?",
    a: "Browser Automation runs sandboxed headless Chromium via Playwright, scrolling the viewport to trigger dynamic lazy loading and waiting for network idle before capturing HTML.",
  },
  {
    q: "Can I use WEBISCRAP without creating an account?",
    a: "Yes. Click 'Continue as guest' on the login screen to immediately test the full extraction pipeline. When you're ready to persist your session history, you can convert your guest account to a permanent email account with one click.",
  },
];

export default function DocsPage() {
  return (
    <div className="relative min-h-dvh bg-bg-0 text-text-hi font-body overflow-x-hidden">
      <WarmUp />
      <div className="bg-field" />
      <MarketingNavbar />

      <main className="relative z-10 pt-[112px] sm:pt-[140px] px-[16px] sm:px-[32px] pb-[80px]">
        {/* Header */}
        <section className="max-w-[1000px] mx-auto text-center mb-[64px] sm:mb-[80px]">
          <div className="inline-flex items-center gap-[8px] px-[12px] py-[6px] rounded-pill border border-glass-border bg-white/5 font-mono text-[11px] text-cyan tracking-[0.04em] mb-[20px]">
            <BookOpen className="w-[14px] h-[14px]" />
            DOCUMENTATION &amp; SPECIFICATION
          </div>
          <h1 className="text-[34px] sm:text-[48px] font-display font-semibold leading-[1.15] mb-[18px]">
            Everything You Need to Build <br className="hidden sm:inline" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-signal-400 to-cyan">
              with WEBISCRAP
            </span>
          </h1>
          <p className="text-[16px] sm:text-[18px] text-text-mid max-w-[640px] mx-auto leading-[1.6]">
            From getting started in the browser to integrating our REST endpoints into your research workflow.
          </p>
        </section>

        {/* Quickstart Guide */}
        <section className="max-w-[1000px] mx-auto mb-[72px]">
          <div className="flex items-center gap-[10px] mb-[24px]">
            <Terminal className="w-[20px] h-[20px] text-cyan" />
            <h2 className="text-[22px] sm:text-[26px] font-display font-semibold">Quickstart: 3 Simple Steps</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-[20px]">
            <Card className="p-[24px] bg-panel">
              <span className="font-mono text-[11px] text-cyan font-bold uppercase tracking-wider mb-[8px] block">Step 1</span>
              <h3 className="font-display font-semibold text-[17px] mb-[8px]">Launch a Chat</h3>
              <p className="text-[13px] text-text-dim leading-[1.6]">
                Sign in or click <strong>Continue as Guest</strong> to open the extraction HUD with zero setup.
              </p>
            </Card>
            <Card className="p-[24px] bg-panel">
              <span className="font-mono text-[11px] text-cyan font-bold uppercase tracking-wider mb-[8px] block">Step 2</span>
              <h3 className="font-display font-semibold text-[17px] mb-[8px]">Prompt &amp; Attach</h3>
              <p className="text-[13px] text-text-dim leading-[1.6]">
                Paste your target URL into the URL bar or drag in a document, then describe what data you want in natural language.
              </p>
            </Card>
            <Card className="p-[24px] bg-panel">
              <span className="font-mono text-[11px] text-cyan font-bold uppercase tracking-wider mb-[8px] block">Step 3</span>
              <h3 className="font-display font-semibold text-[17px] mb-[8px]">Refine &amp; Export</h3>
              <p className="text-[13px] text-text-dim leading-[1.6]">
                Inspect the preview table, ask follow-up questions to refine, and click Export to download CSV or Excel (.xlsx).
              </p>
            </Card>
          </div>
        </section>

        {/* REST API Reference */}
        <section id="api" className="max-w-[1000px] mx-auto mb-[72px] scroll-mt-[96px]">
          <div className="flex items-center gap-[10px] mb-[20px]">
            <Code className="w-[20px] h-[20px] text-cyan" />
            <h2 className="text-[22px] sm:text-[26px] font-display font-semibold">REST API Reference</h2>
          </div>
          <p className="text-text-mid text-[14.5px] mb-[24px]">
            The backend exposes clean, session-scoped endpoints with fail-closed ownership verification and JWT security.
          </p>

          <Card variant="strong" className="p-0 overflow-hidden">
            <div className="divide-y divide-hair">
              {endpoints.map((ep, i) => (
                <div key={i} className="p-[14px_18px] flex flex-col sm:flex-row sm:items-center justify-between gap-[10px] hover:bg-white/2 transition-colors">
                  <div className="flex items-center gap-[12px] min-w-0">
                    <span className={`px-[8px] py-[3px] rounded font-mono text-[11px] font-bold ${
                      ep.method === "POST" ? "bg-signal-400/15 text-signal-400 border border-signal-400/30" :
                      ep.method === "GET" ? "bg-cyan/15 text-cyan border border-cyan/30" :
                      ep.method === "PATCH" ? "bg-amber-400/15 text-amber-400 border border-amber-400/30" :
                      "bg-red-400/15 text-red-400 border border-red-400/30"
                    }`}>
                      {ep.method}
                    </span>
                    <span className="font-mono text-[13px] text-text-hi font-medium truncate">{ep.path}</span>
                  </div>
                  <span className="text-[12.5px] text-text-dim max-w-[480px] sm:text-right">{ep.desc}</span>
                </div>
              ))}
            </div>
          </Card>
        </section>

        {/* Tech Stack Specs */}
        <section id="tech-stack" className="max-w-[1000px] mx-auto mb-[72px] scroll-mt-[96px]">
          <div className="flex items-center gap-[10px] mb-[24px]">
            <Server className="w-[20px] h-[20px] text-cyan" />
            <h2 className="text-[22px] sm:text-[26px] font-display font-semibold">Architecture &amp; Tech Stack</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-[18px]">
            {[
              { label: "Frontend Framework", val: "Next.js 16 (App Router · Turbopack) + React 19" },
              { label: "State Management", val: "Zustand (In-memory reactive state)" },
              { label: "UI Design & Styles", val: "Tailwind CSS v4 with custom HUD glassmorphism tokens" },
              { label: "Backend Framework", val: "FastAPI (Python 3.11+, async, Uvicorn)" },
              { label: "Database Layer", val: "PostgreSQL on Neon Serverless with SQLModel ORM" },
              { label: "Session Cache / JTI", val: "Redis on Upstash with z1 zlib payload compression" },
              { label: "AI Model Provider", val: "Groq (LLaMA 3 70B) with automatic key pool rotation" },
              { label: "Browser Headless Engine", val: "Playwright Chromium with SSRF/DNS-rebinding guards" },
            ].map((item, i) => (
              <Card key={i} className="p-[18px] bg-panel flex flex-col justify-between">
                <span className="font-mono text-[11px] text-text-dim uppercase tracking-wider">{item.label}</span>
                <span className="text-[14px] font-medium text-text-hi mt-[4px]">{item.val}</span>
              </Card>
            ))}
          </div>
        </section>

        {/* FAQ Section */}
        <section className="max-w-[1000px] mx-auto mb-[72px]">
          <div className="flex items-center gap-[10px] mb-[24px]">
            <HelpCircle className="w-[20px] h-[20px] text-cyan" />
            <h2 className="text-[22px] sm:text-[26px] font-display font-semibold">Frequently Asked Questions</h2>
          </div>

          <div className="space-y-[16px]">
            {faqs.map((faq, i) => (
              <Card key={i} className="p-[22px] bg-panel">
                <h3 className="text-[16px] font-display font-semibold text-text-hi mb-[8px] flex items-center gap-2">
                  <CheckCircle2 className="w-[16px] h-[16px] text-cyan shrink-0" />
                  {faq.q}
                </h3>
                <p className="text-[13.5px] text-text-mid leading-[1.65] pl-[24px]">{faq.a}</p>
              </Card>
            ))}
          </div>
        </section>

        {/* GitHub / Repo Links */}
        <section className="max-w-[1000px] mx-auto text-center">
          <Card variant="strong" className="p-[32px] sm:p-[48px] relative overflow-hidden">
            <h3 className="text-[22px] sm:text-[28px] font-display font-semibold mb-[12px]">Want to Inspect the Codebase?</h3>
            <p className="text-[14px] text-text-mid mb-[24px] max-w-[520px] mx-auto">
              WEBISCRAP is maintained and engineered by our student developer team. Check out the GitHub repository, star the project, and inspect our agent implementations.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-[14px]">
              <a href="https://github.com/manoj-n-dev/WEBISCRAP" target="_blank" rel="noopener noreferrer">
                <Button variant="primary" className="h-[44px] px-[24px] text-[14px]">
                  Primary GitHub Repo <ExternalLink className="w-[15px] h-[15px] ml-1" />
                </Button>
              </a>
              <Link href="/login">
                <Button className="h-[44px] px-[24px] text-[14px]">
                  Try Live Extraction
                </Button>
              </Link>
            </div>
          </Card>
        </section>
      </main>

      <MarketingFooter />
    </div>
  );
}
