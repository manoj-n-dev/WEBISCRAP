import React from "react";
import type { Metadata } from "next";
import Link from "next/link";
import { MarketingNavbar } from "@/components/marketing/MarketingNavbar";
import { MarketingFooter } from "@/components/marketing/MarketingFooter";
import { WarmUp } from "@/components/system/WarmUp";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import {
  Sparkles,
  Bot,
  Zap,
  Shield,
  Table,
  Cpu,
  Globe,
  Database,
  Lock,
  FileSpreadsheet,
  CheckCircle,
  XCircle,
  ArrowRight,
  Code2,
} from "lucide-react";

export const metadata: Metadata = {
  title: "Features & Capabilities | WEBISCRAP",
  description: "Explore the enterprise-grade web data extraction features, 9-agent pipeline, and security defenses of WEBISCRAP.",
};

const featureList = [
  {
    icon: Globe,
    title: "Multilingual Natural Language",
    badge: "Polyglot Extraction",
    desc: "Describe what you want extracted in English, Hindi, Telugu, Tamil, or Hinglish. Ask questions like 'sabse saste laptops dikhao' or 'rating 4 kante ekkuva unna items extract chey'.",
  },
  {
    icon: Bot,
    title: "Self-Healing 9-Agent Swarm",
    badge: "Autonomous",
    desc: "No CSS selectors or XPath to maintain. If a site changes its layout or classes tomorrow, our Website Analyzer and Extractor adapt in real time.",
  },
  {
    icon: Database,
    title: "Zero-Re-Scrape Memory",
    badge: "Redis Session Cache",
    desc: "Datasets are cached in Redis. Sort, filter, aggregate, and query your extracted data conversationally without hitting the target site repeatedly.",
  },
  {
    icon: FileSpreadsheet,
    title: "Multi-Format Instant Export",
    badge: "One-Click Formats",
    desc: "Export clean datasets to CSV with UTF-8 BOM, native Microsoft Excel (.xlsx), structured JSON, Markdown tables, or printable PDFs.",
  },
  {
    icon: Shield,
    title: "SSRF & DNS-Rebinding Defense",
    badge: "Enterprise Security",
    desc: "Target URLs are pre-resolved and validated against private IP ranges, cloud metadata (169.254.169.254), and localhost before Chromium navigates.",
  },
  {
    icon: Lock,
    title: "Hardened In-Memory Auth",
    badge: "Fail-Closed Architecture",
    desc: "Access tokens live strictly in memory to block XSS. Refresh tokens use httpOnly SameSite cookies with strict JTI blacklisting on rotation.",
  },
];

const comparison = [
  { feature: "Selector Maintenance", traditional: "Breaks whenever site updates", webiscrap: "Autonomous AI schema adaptation" },
  { feature: "Query Interface", traditional: "Python / Puppeteer / XPath scripts", webiscrap: "Natural conversation (English/Hindi/Telugu)" },
  { feature: "Follow-up Filtering", traditional: "Must write custom data parsing logic", webiscrap: "Instant in-memory conversational queries" },
  { feature: "JavaScript / Lazy-Loading", traditional: "Complex manual scroll wait configs", webiscrap: "Automated Playwright viewport rendering" },
  { feature: "Security & SSRF Guard", traditional: "Requires manual proxy configuration", webiscrap: "Built-in private IP & DNS rebinding filter" },
  { feature: "Formula Injection Defenses", traditional: "Raw string dumping into CSV", webiscrap: "Automated sanitization for Excel/Sheets" },
];

export default function FeaturesPage() {
  return (
    <div className="relative min-h-dvh bg-bg-0 text-text-hi font-body overflow-x-hidden">
      <WarmUp />
      <div className="bg-field" />
      <MarketingNavbar />

      <main className="relative z-10 pt-[112px] sm:pt-[140px] px-[16px] sm:px-[32px] pb-[80px]">
        {/* Header */}
        <section className="max-w-[1000px] mx-auto text-center mb-[72px] sm:mb-[96px]">
          <div className="inline-flex items-center gap-[8px] px-[12px] py-[6px] rounded-pill border border-glass-border bg-white/5 font-mono text-[11px] text-cyan tracking-[0.04em] mb-[20px]">
            <Sparkles className="w-[14px] h-[14px]" />
            BUILT FOR MODERN WEB RESEARCH
          </div>
          <h1 className="text-[34px] sm:text-[52px] font-display font-semibold leading-[1.12] mb-[20px]">
            Engineered for Precision, <br className="hidden sm:inline" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-signal-400 to-cyan">
              Speed, and Peace of Mind
            </span>
          </h1>
          <p className="text-[16px] sm:text-[18px] text-text-mid max-w-[660px] mx-auto leading-[1.6]">
            Everything you need to extract structured data from any corner of the web—without brittle code, selector fatigue, or complex proxy setups.
          </p>
        </section>

        {/* Feature Grid */}
        <section className="max-w-[1200px] mx-auto mb-[96px]">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-[24px]">
            {featureList.map((f, i) => (
              <Card key={i} className="p-[28px] group hover:border-[rgba(20,119,245,0.4)] transition-all bg-panel">
                <div className="flex items-center justify-between mb-[16px]">
                  <div className="w-[44px] h-[44px] rounded-lg bg-[rgba(20,119,245,0.08)] border border-[rgba(20,119,245,0.2)] flex items-center justify-center text-signal-400 group-hover:bg-signal-500 group-hover:text-white transition-colors">
                    <f.icon className="w-[22px] h-[22px]" />
                  </div>
                  <span className="px-[10px] py-[3px] rounded-full border border-hair bg-white/5 font-mono text-[10.5px] text-cyan">
                    {f.badge}
                  </span>
                </div>
                <h3 className="text-[18px] font-display font-semibold mb-[10px] text-text-hi">{f.title}</h3>
                <p className="text-[13.5px] text-text-mid leading-[1.65]">{f.desc}</p>
              </Card>
            ))}
          </div>
        </section>

        {/* Comparison Table */}
        <section className="max-w-[1000px] mx-auto mb-[96px]">
          <div className="text-center mb-[40px]">
            <h2 className="text-[26px] sm:text-[34px] font-display font-semibold mb-[12px]">Why WEBISCRAP vs Traditional Scraping</h2>
            <p className="text-text-mid">See how our conversational approach solves the classic headaches of data harvesting.</p>
          </div>

          <Card variant="strong" className="p-0 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full border-collapse text-[13.5px]">
                <thead>
                  <tr className="border-b border-hair bg-white/5">
                    <th className="p-[14px_18px] text-left font-display font-semibold text-text-hi">Capability</th>
                    <th className="p-[14px_18px] text-left font-display font-semibold text-text-dim">Traditional Scrapers</th>
                    <th className="p-[14px_18px] text-left font-display font-semibold text-cyan">WEBISCRAP Platform</th>
                  </tr>
                </thead>
                <tbody>
                  {comparison.map((row, idx) => (
                    <tr key={idx} className="border-b border-hair/60 hover:bg-white/2 transition-colors">
                      <td className="p-[14px_18px] font-medium text-text-hi">{row.feature}</td>
                      <td className="p-[14px_18px] text-text-dim flex items-center gap-2">
                        <XCircle className="w-[15px] h-[15px] text-red-400 shrink-0" />
                        <span>{row.traditional}</span>
                      </td>
                      <td className="p-[14px_18px] text-text-hi font-medium">
                        <span className="flex items-center gap-2 text-cyan">
                          <CheckCircle className="w-[15px] h-[15px] text-cyan shrink-0" />
                          <span>{row.webiscrap}</span>
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </section>

        {/* CTA Banner */}
        <section className="max-w-[1000px] mx-auto text-center">
          <Card variant="strong" className="p-[36px] sm:p-[56px] relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-b from-transparent to-[rgba(20,119,245,0.08)]" />
            <div className="relative z-10">
              <h2 className="text-[26px] sm:text-[36px] font-display font-semibold mb-[14px]">
                Stop Debugging Selectors Today
              </h2>
              <p className="text-[15px] text-text-mid mb-[28px] max-w-[480px] mx-auto">
                Join users who extract clean tables from the web with simple conversational prompts.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-[14px]">
                <Link href="/login">
                  <Button variant="primary" className="h-[48px] px-[28px] text-[15px]">
                    Get Started Free <ArrowRight className="w-[18px] h-[18px] ml-1" />
                  </Button>
                </Link>
                <Link href="/how-it-works">
                  <Button className="h-[48px] px-[24px] text-[15px]">
                    See The 9 Agents
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
