import React from "react";
import Link from "next/link";
import { WarmUp } from "@/components/system/WarmUp";
import { MarketingNavbar } from "@/components/marketing/MarketingNavbar";
import { MarketingFooter } from "@/components/marketing/MarketingFooter";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { PipelineStrip } from "@/components/chat/PipelineStrip";
import {
  ArrowRight,
  Bot,
  Target,
  Shield,
  Table2,
  Zap,
  BrainCircuit,
  ScanSearch,
  CheckCircle2,
  History,
  MessageSquare,
  Sparkles,
  Layers,
  Database,
  Globe,
  FileSpreadsheet,
  Lock,
  Code2,
  Cpu,
  Palette,
  ShieldCheck,
  ExternalLink,
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="relative min-h-dvh bg-bg-0 text-text-hi font-body overflow-x-hidden selection:bg-[rgba(20,119,245,0.3)]">
      <WarmUp />
      <div className="bg-field" />
      <MarketingNavbar />

      <main className="relative z-10 pt-[104px] sm:pt-[140px] px-[16px] sm:px-[24px]">
        {/* Hero Section */}
        <section className="max-w-[1200px] mx-auto text-center mb-[72px] sm:mb-[120px]">
          <div className="inline-flex items-center gap-[8px] px-[12px] py-[6px] rounded-pill border border-glass-border bg-white/5 font-mono text-[11px] text-cyan tracking-[0.04em] mb-[24px]">
            <span className="w-[6px] h-[6px] rounded-full bg-cyan animate-[pulseDot_1.2s_ease-in-out_infinite]"></span>
            AGENT PIPELINE v2.0 LIVE
          </div>
          <h1 className="text-[34px] sm:text-[48px] lg:text-[64px] font-display font-semibold leading-[1.12] tracking-tight mb-[20px] sm:mb-[24px]">
            Scrape the web with <br className="hidden sm:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-signal-400 to-cyan">plain natural language.</span>
          </h1>
          <p className="text-[16px] sm:text-[18px] text-text-mid max-w-[620px] mx-auto mb-[32px] sm:mb-[40px] leading-[1.6]">
            No CSS selectors. No XPath. No brittle scripts. Paste a URL or attach a CSV, Excel, PDF or image, describe what you want in English, Hindi, or Telugu, and our 9-agent pipeline handles the rest.
          </p>
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-center gap-[12px] sm:gap-[16px] max-w-[420px] sm:max-w-none mx-auto">
            <Link href="/login" className="block">
              <Button variant="primary" className="w-full sm:w-auto h-[48px] px-[28px] text-[15px]">
                Start Free Extraction <ArrowRight className="w-[18px] h-[18px]" />
              </Button>
            </Link>
            <a href="#how-it-works" className="block">
              <Button className="w-full sm:w-auto h-[48px] px-[28px] text-[15px]">How It Works</Button>
            </a>
          </div>

          {/* Hero Mock Chat */}
          <div className="mt-[48px] sm:mt-[80px] max-w-[800px] mx-auto">
            <Card variant="strong" className="p-[14px] sm:p-[24px] text-left relative overflow-hidden">
              <div className="absolute top-0 left-0 right-0 h-[4px] bg-gradient-to-r from-signal-400 via-cyan to-signal-500"></div>

              <MessageBubble role="user" content="Extract the top 20 trending repositories from GitHub today, including their name, description, star count, and primary language." />

              <div className="my-[20px] sm:my-[24px] ml-[14px] sm:ml-[42px] border-l-2 border-[rgba(130,170,255,0.1)] pl-[12px] sm:pl-[24px]">
                <PipelineStrip activeStep="extract" completedSteps={["plan", "analyze", "browse"]} title="Pipeline Progress" />
              </div>

              <MessageBubble role="ai" content={
                <div>
                  Extraction complete. I found 20 trending repositories matching your request. The data is ready for export.
                </div>
              } />
            </Card>
          </div>
        </section>

        {/* How It Works Section */}
        <section id="how-it-works" className="max-w-[1200px] mx-auto mb-[72px] sm:mb-[120px] scroll-mt-[88px]">
          <div className="text-center mb-[36px] sm:mb-[48px]">
            <div className="inline-flex items-center gap-[6px] font-mono text-[11px] uppercase tracking-wider text-cyan mb-[8px]">
              <Sparkles className="w-[14px] h-[14px]" />
              Conversational Extraction Engine
            </div>
            <h2 className="text-[26px] sm:text-[34px] font-display font-semibold mb-[12px]">How WEBISCRAP Works</h2>
            <p className="text-text-mid max-w-[600px] mx-auto">
              Four streamlined stages from raw request to structured spreadsheet, without ever writing a script.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-[20px]">
            {[
              { num: "01", title: "Natural Prompt", desc: "Paste any link or attach a document. Ask for fields in English, Hindi, Telugu, or Hinglish." },
              { num: "02", title: "9-Agent Swarm", desc: "Chromium browses, the analyzer identifies repeating structures, and LLM extracts clean rows." },
              { num: "03", title: "Redis Memory", desc: "Data is cached instantly. Ask follow-up questions to filter, sort, or reshape without re-scraping." },
              { num: "04", title: "Safe Export", desc: "Download in CSV, Excel (.xlsx), JSON, Markdown, or PDF with formula injection defense." },
            ].map((step, i) => (
              <Card key={i} className="p-[24px] bg-panel border-glass-border hover:border-signal-400/40 transition-all flex flex-col justify-between">
                <div>
                  <div className="font-mono text-[24px] font-bold text-signal-400 opacity-60 mb-[12px]">{step.num}</div>
                  <h3 className="font-display font-semibold text-[17px] mb-[8px] text-text-hi">{step.title}</h3>
                  <p className="text-[13px] text-text-mid leading-[1.6]">{step.desc}</p>
                </div>
                <div className="pt-[16px] mt-[16px] border-t border-hair">
                  <Link href="/how-it-works" className="text-[12px] text-cyan hover:underline font-mono inline-flex items-center gap-1">
                    Learn more <ArrowRight className="w-[12px] h-[12px]" />
                  </Link>
                </div>
              </Card>
            ))}
          </div>
        </section>

        {/* 9 Agents Grid */}
        <section id="agents" className="max-w-[1200px] mx-auto mb-[72px] sm:mb-[120px] scroll-mt-[88px]">
          <div className="text-center mb-[32px] sm:mb-[48px]">
            <div className="inline-flex items-center gap-[6px] font-mono text-[11px] uppercase tracking-wider text-cyan mb-[8px]">
              <Layers className="w-[14px] h-[14px]" />
              Micro-Specialized Architecture
            </div>
            <h2 className="text-[26px] sm:text-[32px] font-display font-semibold mb-[12px]">The 9-Agent Backend Swarm</h2>
            <p className="text-text-mid max-w-[620px] mx-auto">A specialized swarm of AI agents working in concert to guarantee flawless, validated extraction.</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-[16px] sm:gap-[20px]">
            {[
              { icon: Target, title: "Planner", desc: "Analyzes your natural language request and formulates the extraction strategy." },
              { icon: ScanSearch, title: "Analyzer", desc: "Inspects the target URL's DOM structure and identifies data clusters." },
              { icon: Bot, title: "Browser", desc: "Navigates headless browsers, handles pagination, scrolling, and popups." },
              { icon: BrainCircuit, title: "Extractor", desc: "Uses an LLM to map unstructured pages and documents to your requested fields." },
              { icon: Zap, title: "Cleaner", desc: "Normalizes whitespace, prices and links, and removes empty and duplicate rows." },
              { icon: Shield, title: "Validator", desc: "Scores completeness against your requested fields and flags sparse rows." },
              { icon: History, title: "Memory", desc: "Maintains session context for follow-up refinements and corrections." },
              { icon: MessageSquare, title: "Conversation", desc: "Manages the chat interface and reports pipeline status back to you." },
              { icon: Table2, title: "Export", desc: "Compiles the validated dataset into CSV, JSON, Excel, or PDF." }
            ].map((agent, i) => (
              <Card key={i} className="p-[20px] sm:p-[24px] group hover:border-[rgba(130,170,255,0.3)] transition-colors">
                <div className="w-[40px] h-[40px] rounded-lg bg-[rgba(20,119,245,0.06)] border border-[rgba(20,119,245,0.12)] flex items-center justify-center text-signal-400 mb-[16px] group-hover:bg-signal-500 group-hover:text-white transition-colors">
                  <agent.icon className="w-[20px] h-[20px]" />
                </div>
                <h3 className="font-display font-semibold text-[16px] mb-[8px]">{agent.title}</h3>
                <p className="text-[13px] text-text-dim leading-[1.6]">{agent.desc}</p>
              </Card>
            ))}
          </div>
        </section>

        {/* Features Highlights Section */}
        <section id="features" className="max-w-[1200px] mx-auto mb-[72px] sm:mb-[120px] scroll-mt-[88px]">
          <div className="text-center mb-[36px] sm:mb-[48px]">
            <div className="inline-flex items-center gap-[6px] font-mono text-[11px] uppercase tracking-wider text-cyan mb-[8px]">
              <Shield className="w-[14px] h-[14px]" />
              Production SaaS Standards
            </div>
            <h2 className="text-[26px] sm:text-[34px] font-display font-semibold mb-[12px]">Key Platform Features</h2>
            <p className="text-text-mid max-w-[580px] mx-auto">Built from the ground up with data integrity, speed, and privacy in mind.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-[20px]">
            {[
              { icon: Globe, title: "Multilingual Prompting", desc: "Seamlessly extract in English, Hindi, Telugu, Tamil, or Hinglish with colloquial term understanding." },
              { icon: Database, title: "Redis Session Caching", desc: "Ask instant follow-ups ('cheapest 5', 'rating > 4') from memory without re-fetching the target website." },
              { icon: FileSpreadsheet, title: "Multi-Format Export", desc: "One-click export to CSV (UTF-8 BOM), native Microsoft Excel (.xlsx), formatted JSON, and Markdown." },
              { icon: Lock, title: "Hardened Security", desc: "In-memory tokens immune to XSS, httpOnly refresh rotation with JTI revocation, and fail-closed data endpoints." },
              { icon: Shield, title: "SSRF & DNS Shield", desc: "Protects backend infrastructure by pre-resolving and blocking private IP and cloud-metadata addresses." },
              { icon: Zap, title: "Durable Job Queue", desc: "Background Redis queue workers decouple heavy Playwright browsing from API response times." },
            ].map((item, i) => (
              <Card key={i} className="p-[24px] bg-panel hover:border-signal-400/40 transition-all">
                <div className="w-[38px] h-[38px] rounded-lg bg-[rgba(20,119,245,0.08)] border border-[rgba(20,119,245,0.2)] flex items-center justify-center text-cyan mb-[14px]">
                  <item.icon className="w-[18px] h-[18px]" />
                </div>
                <h3 className="font-display font-semibold text-[16px] text-text-hi mb-[8px]">{item.title}</h3>
                <p className="text-[13px] text-text-dim leading-[1.6]">{item.desc}</p>
              </Card>
            ))}
          </div>
          <div className="text-center mt-[32px]">
            <Link href="/features">
              <Button className="px-[24px] py-[10px] text-[13.5px]">
                View All Capabilities &amp; Comparison <ArrowRight className="w-[14px] h-[14px] ml-1" />
              </Button>
            </Link>
          </div>
        </section>

        {/* Creators & Maintainers Section */}
        <section id="creators" className="max-w-[1200px] mx-auto mb-[72px] sm:mb-[120px] scroll-mt-[88px]">
          <div className="text-center mb-[36px] sm:mb-[48px]">
            <div className="inline-flex items-center gap-[6px] font-mono text-[11px] uppercase tracking-wider text-cyan mb-[8px]">
              <Bot className="w-[14px] h-[14px]" />
              Engineering Team
            </div>
            <h2 className="text-[26px] sm:text-[34px] font-display font-semibold mb-[12px]">Meet the Creators</h2>
            <p className="text-text-mid max-w-[580px] mx-auto">The final-year engineering team that designed, developed, and deployed WEBISCRAP.</p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-[16px]">
            {[
              { name: "Manoj N", role: "Lead Architect", icon: Code2, focus: "Architecture & Core" },
              { name: "Bhavya", role: "AI Pipeline", icon: Cpu, focus: "Prompt & LLM Swarm" },
              { name: "Lohit", role: "Backend & Cache", icon: Database, focus: "Redis & Queue" },
              { name: "Sushanth", role: "Frontend UI/UX", icon: Palette, focus: "Next.js & Tables" },
              { name: "Muni Bharath", role: "Security & QA", icon: ShieldCheck, focus: "SSRF & Auth Hardening" },
            ].map((m, i) => (
              <Card key={i} className="p-[20px] bg-panel text-center hover:border-signal-400/40 transition-all flex flex-col items-center justify-between">
                <div className="w-[48px] h-[48px] rounded-full bg-[rgba(20,119,245,0.1)] border border-[rgba(20,119,245,0.25)] flex items-center justify-center text-cyan mb-[12px]">
                  <m.icon className="w-[20px] h-[20px]" />
                </div>
                <div>
                  <h4 className="font-display font-semibold text-[15px] text-text-hi mb-[2px]">{m.name}</h4>
                  <div className="text-[11.5px] font-mono text-signal-400 mb-[4px]">{m.role}</div>
                  <div className="text-[11px] text-text-dim">{m.focus}</div>
                </div>
              </Card>
            ))}
          </div>
          <div className="text-center mt-[24px]">
            <Link href="/creators" className="text-[13px] text-cyan hover:underline font-mono inline-flex items-center gap-1">
              Read full team bios and roles <ArrowRight className="w-[12px] h-[12px]" />
            </Link>
          </div>
        </section>

        {/* CTA Section */}
        <section className="max-w-[1200px] mx-auto mb-[72px] sm:mb-[120px]">
          <Card variant="strong" className="p-[28px] sm:p-[64px] text-center relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-b from-transparent to-[rgba(20,119,245,0.05)]"></div>
            <div className="relative z-10">
              <h2 className="text-[26px] sm:text-[40px] font-display font-semibold mb-[16px]">Ready to ditch the selectors?</h2>
              <p className="text-[16px] text-text-mid mb-[32px] max-w-[500px] mx-auto">
                Join developers and researchers using WEBISCRAP to turn the internet into a database.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-[12px]">
                <Link href="/login">
                  <Button variant="primary" className="h-[48px] px-[32px] text-[15px]">
                    Start Extracting Now <ArrowRight className="w-[18px] h-[18px] ml-1" />
                  </Button>
                </Link>
                <Link href="/docs">
                  <Button className="h-[48px] px-[24px] text-[15px]">
                    View Documentation
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
