import React from "react";
import type { Metadata } from "next";
import Link from "next/link";
import { MarketingNavbar } from "@/components/marketing/MarketingNavbar";
import { MarketingFooter } from "@/components/marketing/MarketingFooter";
import { WarmUp } from "@/components/system/WarmUp";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import {
  Target,
  ScanSearch,
  Bot,
  BrainCircuit,
  Zap,
  Shield,
  History,
  MessageSquare,
  Table2,
  ArrowRight,
  Sparkles,
  Layers,
  Database,
  FileCheck2,
} from "lucide-react";

export const metadata: Metadata = {
  title: "How It Works | WEBISCRAP",
  description: "Learn how WEBISCRAP's 9-agent autonomous pipeline extracts, cleans, and exports web data without code or selectors.",
};

const steps = [
  {
    step: "01",
    title: "State Your Goal in Plain Language",
    badge: "Natural Language Input",
    desc: "Paste any website URL or upload a file (PDF, Excel, CSV, Word doc, or screenshot). Describe what fields you want to extract in English, Telugu, Hindi, Tamil, or Hinglish. No CSS selectors, XPath queries, or scraping scripts required.",
    details: ["Supports dynamic JS sites, catalogs, articles, tables", "Accepts raw file attachments up to 20MB", "Understands multilingual queries and colloquial prompts"],
  },
  {
    step: "02",
    title: "Autonomous 9-Agent Execution",
    badge: "Multi-Agent Swarm",
    desc: "The Orchestrator dispatches your request across nine specialized agents that inspect the DOM, drive headless browsers, parse schemas, deduplicate rows, and assign statistical confidence scores.",
    details: ["Playwright headless Chromium rendering with lazy scroll", "SSRF and DNS-rebinding verified network protections", "Automated currency, date, and link resolution"],
  },
  {
    step: "03",
    title: "Conversational Follow-ups in Memory",
    badge: "Redis Session Caching",
    desc: "Unlike traditional scrapers that re-download the page for every tweak, WEBISCRAP stores the extracted dataset in fast Redis session memory. Ask follow-up queries like 'sort by price', 'filter rating > 4.5', or 'remove items without images' instantaneously.",
    details: ["Zero latency re-querying without hitting the target website", "Stateful conversational memory across your session", "Interactive preview table directly inside the chat HUD"],
  },
  {
    step: "04",
    title: "Sanitized Multi-Format Export",
    badge: "One-Click Delivery",
    desc: "Download clean, validated datasets in CSV (with UTF-8 BOM for Microsoft Excel), real .xlsx workbooks, structured JSON, Markdown tables, or printable PDFs with formula-injection defenses built in.",
    details: ["CSV injection protection (=, +, -, @ prepending)", "Consistent column alignment across dynamic schemas", "One-click export from chat or dedicated Dataset view"],
  },
];

const agents = [
  { num: "01", icon: Target, name: "Planner Agent", role: "Strategy & Intent", desc: "Interprets natural language queries, classifies whether new web browsing is required or if session memory can fulfill it, and produces structured pipeline plans." },
  { num: "02", icon: ScanSearch, name: "Website Analyzer", role: "DOM Structural Analysis", desc: "Inspects minified DOM trees, isolates repeating container tags (tables, grid cards, list items), and generates optimized extraction anchors." },
  { num: "03", icon: Bot, name: "Browser Automation", role: "Headless Playwright", desc: "Spins up sandboxed Chromium, scrolls to trigger lazy images, manages AJAX hydration, and defends against SSRF and DNS rebinding attacks." },
  { num: "04", icon: BrainCircuit, name: "Extractor Agent", role: "LLM Schema Alignment", desc: "Pulls raw HTML clusters into clean JSON schemas, mapping colloquial user requested fields into uniform key-value pairs." },
  { num: "05", icon: Zap, name: "Cleaning Agent", role: "Normalization & Deduping", desc: "Prunes duplicates, resolves relative paths into absolute URLs, normalizes messy currencies and formats timestamps cleanly." },
  { num: "06", icon: Shield, name: "Validation Agent", role: "Quality Assurance", desc: "Computes row-level confidence metrics (0.0 to 1.0), flags incomplete or null cells, and marks high-quality datasets for consumption." },
  { num: "07", icon: History, name: "Memory Agent", role: "Redis Session Store", desc: "Compresses and caches datasets into Redis (`z1:` compressed payloads) allowing instant conversational filtering without re-scraping." },
  { num: "08", icon: MessageSquare, name: "Conversation Agent", role: "Follow-up Querying", desc: "Executes in-memory transformations like sorting, slicing, filtering, and statistical summaries directly in chat." },
  { num: "09", icon: Table2, name: "Export Agent", role: "Safe File Generation", desc: "Compiles validated datasets into CSV, Excel (.xlsx), JSON, Markdown, and PDF formats with spreadsheet formula neutralization." },
];

export default function HowItWorksPage() {
  return (
    <div className="relative min-h-dvh bg-bg-0 text-text-hi font-body overflow-x-hidden">
      <WarmUp />
      <div className="bg-field" />
      <MarketingNavbar />

      <main className="relative z-10 pt-[112px] sm:pt-[140px] px-[16px] sm:px-[32px] pb-[80px]">
        {/* Hero */}
        <section className="max-w-[1000px] mx-auto text-center mb-[72px] sm:mb-[96px]">
          <div className="inline-flex items-center gap-[8px] px-[12px] py-[6px] rounded-pill border border-glass-border bg-white/5 font-mono text-[11px] text-cyan tracking-[0.04em] mb-[20px]">
            <Sparkles className="w-[14px] h-[14px]" />
            THE ARCHITECTURE BEHIND ZERO-CODE EXTRACTION
          </div>
          <h1 className="text-[34px] sm:text-[52px] font-display font-semibold leading-[1.12] mb-[20px]">
            How WEBISCRAP Turns <br className="hidden sm:inline" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-signal-400 to-cyan">
              Websites into Clean Databases
            </span>
          </h1>
          <p className="text-[16px] sm:text-[18px] text-text-mid max-w-[680px] mx-auto leading-[1.6]">
            Traditional scrapers fail when websites update their CSS or layout. WEBISCRAP operates like an intelligent research team that visually navigates, reads, normalizes, and validates information for you.
          </p>
        </section>

        {/* 4-Step Process Section */}
        <section className="max-w-[1100px] mx-auto mb-[96px]">
          <div className="text-center mb-[48px]">
            <h2 className="text-[26px] sm:text-[32px] font-display font-semibold mb-[12px]">The 4-Step Flow</h2>
            <p className="text-text-mid">From your raw request to an export-ready spreadsheet in seconds.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-[24px]">
            {steps.map((s) => (
              <Card key={s.step} variant="strong" className="p-[28px] sm:p-[32px] relative overflow-hidden group hover:border-[rgba(130,170,255,0.3)] transition-all">
                <div className="flex items-center justify-between mb-[16px]">
                  <span className="font-mono text-[24px] font-bold text-signal-400 opacity-60 group-hover:opacity-100 transition-opacity">
                    {s.step}
                  </span>
                  <span className="px-[10px] py-[4px] rounded-full border border-hair bg-white/5 font-mono text-[11px] text-cyan">
                    {s.badge}
                  </span>
                </div>
                <h3 className="text-[19px] font-display font-semibold mb-[12px] text-text-hi">{s.title}</h3>
                <p className="text-[14px] text-text-mid leading-[1.65] mb-[20px]">{s.desc}</p>
                <div className="space-y-[8px] pt-[16px] border-t border-hair">
                  {s.details.map((d, i) => (
                    <div key={i} className="flex items-center gap-[8px] text-[12.5px] text-text-dim">
                      <FileCheck2 className="w-[14px] h-[14px] text-cyan shrink-0" />
                      <span>{d}</span>
                    </div>
                  ))}
                </div>
              </Card>
            ))}
          </div>
        </section>

        {/* 9-Agent Pipeline Deep-Dive */}
        <section className="max-w-[1200px] mx-auto mb-[96px]">
          <div className="text-center mb-[48px]">
            <div className="inline-flex items-center gap-[6px] font-mono text-[11px] uppercase tracking-wider text-cyan mb-[8px]">
              <Layers className="w-[14px] h-[14px]" />
              Backend Swarm Engine
            </div>
            <h2 className="text-[26px] sm:text-[36px] font-display font-semibold mb-[12px]">The 9-Agent Pipeline</h2>
            <p className="text-text-mid max-w-[620px] mx-auto">
              Every extraction passes through nine specialized AI agents that collaborate to ensure precision, completeness, and security.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-[20px]">
            {agents.map((ag) => (
              <Card key={ag.num} className="p-[24px] group hover:border-[rgba(20,119,245,0.4)] transition-all bg-panel">
                <div className="flex items-center justify-between mb-[16px]">
                  <div className="w-[42px] h-[42px] rounded-lg bg-[rgba(20,119,245,0.08)] border border-[rgba(20,119,245,0.2)] flex items-center justify-center text-signal-400 group-hover:bg-signal-500 group-hover:text-white transition-colors">
                    <ag.icon className="w-[20px] h-[20px]" />
                  </div>
                  <span className="font-mono text-[11px] text-text-dim font-semibold">{ag.num}</span>
                </div>
                <div className="font-mono text-[11px] text-cyan uppercase tracking-wider mb-[4px]">{ag.role}</div>
                <h3 className="font-display font-semibold text-[17px] text-text-hi mb-[8px]">{ag.name}</h3>
                <p className="text-[13px] text-text-dim leading-[1.6]">{ag.desc}</p>
              </Card>
            ))}
          </div>
        </section>

        {/* CTA */}
        <section className="max-w-[1000px] mx-auto text-center">
          <Card variant="strong" className="p-[36px] sm:p-[56px] relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-b from-transparent to-[rgba(20,119,245,0.08)]" />
            <div className="relative z-10">
              <h2 className="text-[26px] sm:text-[36px] font-display font-semibold mb-[14px]">
                Ready to Experience AI Web Scraping?
              </h2>
              <p className="text-[15px] text-text-mid mb-[28px] max-w-[480px] mx-auto">
                No credit card required. Try guest mode or create a free account to run your first extraction right now.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-[14px]">
                <Link href="/login">
                  <Button variant="primary" className="h-[48px] px-[28px] text-[15px]">
                    Start Extracting Free <ArrowRight className="w-[18px] h-[18px] ml-1" />
                  </Button>
                </Link>
                <Link href="/features">
                  <Button className="h-[48px] px-[24px] text-[15px]">
                    Explore Features
                  </Button>
                </Link>
              </div>
            </div>
          </Card>
        </section>
      </main>

      <MarketingFooter />
    </div>
  );
}
