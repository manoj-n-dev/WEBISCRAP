import React from "react";
import type { Metadata } from "next";
import Link from "next/link";
import { MarketingNavbar } from "@/components/marketing/MarketingNavbar";
import { MarketingFooter } from "@/components/marketing/MarketingFooter";
import { WarmUp } from "@/components/system/WarmUp";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { BackButton } from "@/components/ui/BackButton";
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
  Cpu,
  Layers,
  Database,
  Lock,
  FileSpreadsheet,
  CheckCircle2,
} from "lucide-react";

export const metadata: Metadata = {
  title: "AI Agents | WEBISCRAP",
  description: "Meet the 9 autonomous AI agents powering WEBISCRAP's zero-code web data extraction pipeline.",
};

const agents = [
  {
    num: "01",
    icon: Target,
    name: "Planner Agent",
    role: "Strategy & Intent Classification",
    badge: "FastAPI / Intent Engine",
    color: "from-signal-400 to-emerald-400",
    desc: "Interprets natural language prompts in English, Telugu, Hindi, Tamil, or Hinglish. Analyzes user intent to determine whether a fresh web scrape is required or if the query can be resolved instantly from Redis session memory.",
    capabilities: [
      "Multilingual intent parsing",
      "Session cache hit/miss classification",
      "Dynamic multi-step execution planning",
      "Prompt safety & injection defense",
    ],
  },
  {
    num: "02",
    icon: ScanSearch,
    name: "Website Analyzer",
    role: "DOM Structural Analysis",
    badge: "AST / BeautifulSoup4",
    color: "from-cyan to-blue-400",
    desc: "Performs headless structural decomposition of target web pages. Strips ads, navigation headers, footers, and scripts while isolating repeating semantic card clusters, table rows, and grid layouts.",
    capabilities: [
      "Semantic container identification",
      "Boilerplate & noise reduction",
      "XPath & CSS selector generation",
      "Dynamic pagination discovery",
    ],
  },
  {
    num: "03",
    icon: Bot,
    name: "Browser Automation",
    role: "Sandboxed Playwright Engine",
    badge: "Playwright / Chromium",
    color: "from-purple-400 to-indigo-400",
    desc: "Drives headless Chromium instances in an isolated sandbox. Handles client-rendered JavaScript (React, Vue, Next.js), scrolls to trigger lazy-loaded images, and enforces strict SSRF and private-network access guards.",
    capabilities: [
      "Dynamic infinite-scroll trigger",
      "Single-page application hydration",
      "SSRF & DNS-rebinding shield",
      "Automated cookie & modal dismissal",
    ],
  },
  {
    num: "04",
    icon: BrainCircuit,
    name: "Extractor Agent",
    role: "LLM Schema Alignment",
    badge: "Google Gemini / Pydantic",
    color: "from-amber-400 to-signal-400",
    desc: "Transforms raw extracted HTML trees into strictly typed JSON structures. Maps colloquial requested fields (e.g. 'discount price', 'specs', 'star rating') into normalized database columns with zero selector dependencies.",
    capabilities: [
      "Zero-shot schema generation",
      "Colloquial column name mapping",
      "Nested object & array extraction",
      "Self-correcting JSON parsing",
    ],
  },
  {
    num: "05",
    icon: Zap,
    name: "Cleaning Agent",
    role: "Normalization & Deduplication",
    badge: "Data Cleansing Engine",
    color: "from-emerald-400 to-teal-400",
    desc: "Cleans extracted datasets by removing duplicate entries, resolving relative URLs to absolute HTTP links, unescaping HTML entities, and standardizing disparate currency formats and timestamps.",
    capabilities: [
      "Cross-row deduplication",
      "Relative-to-absolute URL conversion",
      "Currency symbol & rate normalization",
      "ISO-8601 timestamp standardizing",
    ],
  },
  {
    num: "06",
    icon: Shield,
    name: "Validation Agent",
    role: "Quality Assurance & Scoring",
    badge: "Statistical Scorer",
    color: "from-red-400 to-pink-400",
    desc: "Evaluates extracted records against data integrity rules. Computes row-level confidence scores (0.0 to 1.0), detects missing critical columns, flags anomalies, and guarantees minimum quality thresholds.",
    capabilities: [
      "Statistical confidence scoring",
      "Null and empty cell detection",
      "Outlier & anomaly flagging",
      "Data type consistency verification",
    ],
  },
  {
    num: "07",
    icon: History,
    name: "Memory Agent",
    role: "Redis Session Store",
    badge: "Redis / z1 Compression",
    color: "from-violet-400 to-purple-400",
    desc: "Stores validated datasets in low-latency Redis cache using z1 compression. Keeps your extraction context alive throughout the session so you can ask conversational follow-up questions without re-scraping the target site.",
    capabilities: [
      "Compressed session caching (z1)",
      "Zero re-scrape conversational memory",
      "Instant state recall across turns",
      "Multi-session TTL management",
    ],
  },
  {
    num: "08",
    icon: MessageSquare,
    name: "Conversation Agent",
    role: "In-Memory Follow-up Querying",
    badge: "Pandas / Polars Engine",
    color: "from-cyan to-teal-400",
    desc: "Answers natural language questions about your active dataset. Filters rows, calculates mathematical aggregations, sorts by arbitrary columns, and generates summary insights directly in the chat HUD.",
    capabilities: [
      "In-memory filtering & sorting",
      "Statistical aggregation & averages",
      "Sub-dataset extraction",
      "Natural language data summaries",
    ],
  },
  {
    num: "09",
    icon: Table2,
    name: "Export Agent",
    role: "Secure Multi-Format Delivery",
    badge: "Format Neutralization Engine",
    color: "from-signal-400 to-cyan",
    desc: "Compiles validated datasets into production-ready file formats. Defends against spreadsheet formula injection attacks (=, +, -, @ prepending) and produces clean CSV, native Excel (.xlsx), JSON, Markdown, and PDF files.",
    capabilities: [
      "CSV with UTF-8 BOM for Microsoft Excel",
      "Real Microsoft Excel (.xlsx) workbooks",
      "Spreadsheet formula injection defense",
      "Structured JSON, Markdown, & PDF export",
    ],
  },
];

const pipelineSteps = [
  { step: "01", name: "Planner", label: "Intent" },
  { step: "02", name: "Analyzer", label: "DOM Tree" },
  { step: "03", name: "Browser", label: "Headless" },
  { step: "04", name: "Extractor", label: "LLM Schema" },
  { step: "05", name: "Cleaner", label: "Normalize" },
  { step: "06", name: "Validator", label: "Score" },
  { step: "07", name: "Memory", label: "Redis Cache" },
  { step: "08", name: "Conversation", label: "Chat HUD" },
  { step: "09", name: "Exporter", label: "Delivery" },
];

export default function AgentsPage() {
  return (
    <div className="relative min-h-dvh bg-bg-0 text-text-hi font-body overflow-x-hidden">
      <WarmUp />
      <div className="bg-field" />
      <MarketingNavbar />

      <main className="relative z-10 pt-[96px] sm:pt-[120px] px-[16px] sm:px-[32px] pb-[80px]">
        <div className="max-w-[1200px] mx-auto mb-[20px]">
          <BackButton fallbackHref="/" />
        </div>

        {/* Hero */}
        <section className="max-w-[1000px] mx-auto text-center mb-[64px] sm:mb-[80px]">
          <div className="inline-flex items-center gap-[8px] px-[12px] py-[6px] rounded-pill border border-glass-border bg-white/5 font-mono text-[11px] text-cyan tracking-[0.04em] mb-[20px]">
            <Sparkles className="w-[14px] h-[14px]" />
            AUTONOMOUS MULTI-AGENT SWARM
          </div>
          <h1 className="text-[34px] sm:text-[54px] font-display font-semibold leading-[1.12] mb-[20px]">
            Nine Specialized AI Agents. <br className="hidden sm:inline" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-signal-400 via-cyan to-signal-300">
              One Flawless Dataset.
            </span>
          </h1>
          <p className="text-[16px] sm:text-[18px] text-text-mid max-w-[700px] mx-auto leading-[1.6]">
            WEBISCRAP replaces brittle manual scraping code with a synchronized swarm of autonomous agents. Each agent handles a single specialized responsibility with built-in validation, memory, and security guards.
          </p>
        </section>

        {/* Swarm Pipeline Strip */}
        <section className="max-w-[1100px] mx-auto mb-[72px]">
          <div className="bg-panel border border-glass-border rounded-card p-[20px] sm:p-[28px]">
            <div className="flex items-center justify-between gap-[8px] mb-[20px] flex-wrap">
              <div className="flex items-center gap-[8px]">
                <Layers className="w-[18px] h-[18px] text-signal-400" />
                <span className="text-[14px] font-mono font-medium tracking-wide uppercase text-text-hi">Swarm Execution Pipeline</span>
              </div>
              <span className="text-[12px] font-mono text-cyan bg-cyan/10 border border-cyan/20 px-[10px] py-[4px] rounded-pill">
                Self-Healing &amp; Fully Autonomous
              </span>
            </div>
            
            <div className="grid grid-cols-3 sm:grid-cols-5 md:grid-cols-9 gap-[8px]">
              {pipelineSteps.map((s, idx) => (
                <div key={s.step} className="flex flex-col items-center text-center p-[10px] rounded-[8px] bg-white/[0.02] border border-white/[0.04] hover:border-signal-400/40 transition-colors">
                  <span className="font-mono text-[10px] text-text-dim mb-[4px]">{s.step}</span>
                  <span className="text-[12px] font-display font-semibold text-text-hi leading-tight">{s.name}</span>
                  <span className="text-[10px] text-cyan font-mono mt-[2px]">{s.label}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Detailed 9-Agent Grid */}
        <section className="max-w-[1200px] mx-auto mb-[96px]">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-[20px] sm:gap-[24px]">
            {agents.map((agent) => {
              const Icon = agent.icon;
              return (
                <div
                  key={agent.num}
                  className="bg-panel border border-glass-border rounded-card p-[24px] sm:p-[28px] hover:border-glass-border-strong hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between group"
                >
                  <div>
                    <div className="flex items-center justify-between mb-[16px]">
                      <div className="w-[44px] h-[44px] rounded-[10px] bg-white/5 border border-glass-border flex items-center justify-center text-signal-400 group-hover:text-cyan group-hover:border-cyan/40 transition-colors">
                        <Icon className="w-[22px] h-[22px]" />
                      </div>
                      <span className="font-mono text-[12px] text-text-dim tracking-wider">
                        AGENT {agent.num}
                      </span>
                    </div>

                    <div className="mb-[12px]">
                      <h3 className="text-[19px] font-display font-semibold text-text-hi mb-[4px]">
                        {agent.name}
                      </h3>
                      <p className="text-[12.5px] font-mono text-cyan">
                        {agent.role}
                      </p>
                    </div>

                    <p className="text-[13.5px] text-text-mid leading-[1.6] mb-[20px]">
                      {agent.desc}
                    </p>
                  </div>

                  <div>
                    <div className="border-t border-glass-border pt-[16px]">
                      <div className="text-[11px] font-mono text-text-dim uppercase tracking-wider mb-[10px]">
                        Key Capabilities
                      </div>
                      <div className="flex flex-col gap-[6px]">
                        {agent.capabilities.map((cap, i) => (
                          <div key={i} className="flex items-center gap-[8px] text-[12px] text-text-mid">
                            <CheckCircle2 className="w-[12px] h-[12px] text-signal-400 shrink-0" />
                            <span>{cap}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="mt-[16px] pt-[12px] border-t border-white/[0.04] flex items-center justify-between">
                      <span className="font-mono text-[10px] text-text-dim uppercase">Engine</span>
                      <span className="font-mono text-[11px] text-text-mid">{agent.badge}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* Architecture Highlights & Stats */}
        <section className="max-w-[1100px] mx-auto mb-[96px]">
          <div className="bg-panel border border-glass-border rounded-card p-[32px] sm:p-[48px] text-center">
            <h2 className="text-[26px] sm:text-[36px] font-display font-semibold mb-[16px]">
              Engineered for Speed, Reliability, &amp; Defense
            </h2>
            <p className="text-[15px] sm:text-[16px] text-text-mid max-w-[640px] mx-auto mb-[40px] leading-[1.6]">
              Every component of the agent swarm is architected to operate asynchronously. While the Browser Automation agent handles network rendering, the Extractor aligns models, and the Memory agent caches snapshots into Redis.
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-[16px] sm:gap-[24px]">
              <div className="p-[20px] rounded-card bg-white/[0.02] border border-glass-border">
                <div className="text-[32px] sm:text-[40px] font-display font-semibold text-signal-400 mb-[4px]">9</div>
                <div className="text-[12px] font-mono text-text-mid uppercase tracking-wide">Autonomous Agents</div>
              </div>
              <div className="p-[20px] rounded-card bg-white/[0.02] border border-glass-border">
                <div className="text-[32px] sm:text-[40px] font-display font-semibold text-cyan mb-[4px]">0</div>
                <div className="text-[12px] font-mono text-text-mid uppercase tracking-wide">CSS Selectors Needed</div>
              </div>
              <div className="p-[20px] rounded-card bg-white/[0.02] border border-glass-border">
                <div className="text-[32px] sm:text-[40px] font-display font-semibold text-signal-400 mb-[4px]">5+</div>
                <div className="text-[12px] font-mono text-text-mid uppercase tracking-wide">Languages Understood</div>
              </div>
              <div className="p-[20px] rounded-card bg-white/[0.02] border border-glass-border">
                <div className="text-[32px] sm:text-[40px] font-display font-semibold text-cyan mb-[4px]">5</div>
                <div className="text-[12px] font-mono text-text-mid uppercase tracking-wide">Export Formats</div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="max-w-[800px] mx-auto text-center">
          <div className="bg-panel border border-glass-border rounded-card p-[32px] sm:p-[48px] relative overflow-hidden">
            <div className="absolute top-0 right-0 w-[300px] h-[300px] bg-signal-400/5 rounded-full blur-[80px] pointer-events-none" />
            <h2 className="text-[26px] sm:text-[34px] font-display font-semibold mb-[14px]">
              Put the 9-Agent Swarm to Work
            </h2>
            <p className="text-[15px] sm:text-[16px] text-text-mid max-w-[500px] mx-auto mb-[28px] leading-[1.6]">
              Start extracting clean, validated datasets from any website in seconds. No credit card required.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-[12px]">
              <Link href="/login" className="w-full sm:w-auto">
                <Button variant="primary" className="w-full px-[28px] py-[14px] text-[15px]">
                  Start Extracting Free
                  <ArrowRight className="w-[16px] h-[16px] ml-[8px]" />
                </Button>
              </Link>
              <Link href="/how-it-works" className="w-full sm:w-auto">
                <Button variant="ghost" className="w-full px-[24px] py-[14px] text-[15px]">
                  See Pipeline Details
                </Button>
              </Link>
            </div>
          </div>
        </section>
      </main>

      <MarketingFooter />
    </div>
  );
}
