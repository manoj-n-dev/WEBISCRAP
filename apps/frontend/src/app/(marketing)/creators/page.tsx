import React from "react";
import type { Metadata } from "next";
import Link from "next/link";
import { MarketingNavbar } from "@/components/marketing/MarketingNavbar";
import { MarketingFooter } from "@/components/marketing/MarketingFooter";
import { WarmUp } from "@/components/system/WarmUp";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import {
  Users,
  Code2,
  Cpu,
  Database,
  ShieldCheck,
  Palette,
  ExternalLink,
  Sparkles,
  Heart,
} from "lucide-react";

function GithubIcon({ className = "w-4 h-4" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4" />
      <path d="M9 18c-4.51 2-5-2-7-2" />
    </svg>
  );
}

export const metadata: Metadata = {
  title: "Creators & Team | WEBISCRAP",
  description: "Meet the creators, engineers, and maintainers of the WEBISCRAP autonomous extraction platform.",
};

const teamMembers = [
  {
    name: "Manoj N",
    role: "Lead Full-Stack Architect & Project Lead",
    focus: "System Architecture, FastAPI Orchestrator, Next.js 16 UI, Deployment",
    icon: Code2,
    badge: "Lead Architect",
    bio: "Architected the end-to-end 9-agent pipeline, in-memory auth lifecycle, and fail-closed session ownership model.",
    github: "https://github.com/manoj-n-dev",
  },
  {
    name: "Bhavya",
    role: "AI Agent Pipeline & Prompt Engineer",
    focus: "LLM Schema Alignment, Groq Key Rotation Pool, Extraction Prompts",
    icon: Cpu,
    badge: "AI Systems",
    bio: "Engineered prompt pipelines across multilingual query sets and fine-tuned structured JSON object outputs.",
    github: "https://github.com/team3c23",
  },
  {
    name: "Lohit",
    role: "Backend & Distributed Cache Engineer",
    focus: "Redis Session Memory, Payload Compression, Async Queue Workers",
    icon: Database,
    badge: "Backend & Data",
    bio: "Built the Redis z1 compression pipeline, session ownership claiming, and headless browser task synchronization.",
    github: "https://github.com/team3c23",
  },
  {
    name: "Sushanth",
    role: "Frontend UI/UX & Data Visualization",
    focus: "TanStack Table Integration, Multi-Format Exports, HUD Components",
    icon: Palette,
    badge: "Frontend & UI",
    bio: "Designed the cinematic dark-mode HUD theme, real-time PipelineStrip animations, and responsive export suite.",
    github: "https://github.com/team3c23",
  },
  {
    name: "Muni Bharath",
    role: "Security & QA Engineer",
    focus: "SSRF & DNS Defense, Token Blacklisting, E2E Integration Testing",
    icon: ShieldCheck,
    badge: "Security & QA",
    bio: "Hardened the headless Chromium sandbox against private IP probing, validated formula injection sanitization, and verified test suites.",
    github: "https://github.com/team3c23",
  },
];

export default function CreatorsPage() {
  return (
    <div className="relative min-h-dvh bg-bg-0 text-text-hi font-body overflow-x-hidden">
      <WarmUp />
      <div className="bg-field" />
      <MarketingNavbar />

      <main className="relative z-10 pt-[112px] sm:pt-[140px] px-[16px] sm:px-[32px] pb-[80px]">
        {/* Header */}
        <section className="max-w-[1000px] mx-auto text-center mb-[72px] sm:mb-[96px]">
          <div className="inline-flex items-center gap-[8px] px-[12px] py-[6px] rounded-pill border border-glass-border bg-white/5 font-mono text-[11px] text-cyan tracking-[0.04em] mb-[20px]">
            <Users className="w-[14px] h-[14px]" />
            THE CORE ENGINEERING TEAM
          </div>
          <h1 className="text-[34px] sm:text-[52px] font-display font-semibold leading-[1.12] mb-[20px]">
            Meet the Builders of <br className="hidden sm:inline" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-signal-400 to-cyan">
              WEBISCRAP
            </span>
          </h1>
          <p className="text-[16px] sm:text-[18px] text-text-mid max-w-[640px] mx-auto leading-[1.6]">
            Built with dedication, modern engineering practices, and production-grade standards as our Final Year Capstone Project.
          </p>
        </section>

        {/* Team Grid */}
        <section className="max-w-[1100px] mx-auto mb-[96px]">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-[24px]">
            {teamMembers.map((member, i) => (
              <Card key={i} className="p-[28px] bg-panel group hover:border-[rgba(20,119,245,0.4)] transition-all flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-[18px]">
                    <div className="w-[46px] h-[46px] rounded-xl bg-[rgba(20,119,245,0.08)] border border-[rgba(20,119,245,0.2)] flex items-center justify-center text-signal-400 group-hover:bg-signal-500 group-hover:text-white transition-colors">
                      <member.icon className="w-[22px] h-[22px]" />
                    </div>
                    <span className="px-[10px] py-[3px] rounded-full border border-hair bg-white/5 font-mono text-[10.5px] text-cyan">
                      {member.badge}
                    </span>
                  </div>

                  <h3 className="text-[20px] font-display font-semibold text-text-hi mb-[4px]">{member.name}</h3>
                  <div className="text-[12.5px] font-mono text-signal-400 mb-[12px]">{member.role}</div>
                  <p className="text-[13.5px] text-text-mid leading-[1.6] mb-[16px]">{member.bio}</p>
                </div>

                <div className="pt-[16px] border-t border-hair flex items-center justify-between">
                  <span className="text-[11.5px] text-text-dim font-mono truncate max-w-[200px]">{member.focus}</span>
                  <a
                    href={member.github}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-[28px] h-[28px] rounded-full border border-hair flex items-center justify-center text-text-dim hover:text-text-hi hover:bg-white/5 transition-colors shrink-0"
                    aria-label={`${member.name} GitHub`}
                  >
                    <GithubIcon className="w-[14px] h-[14px]" />
                  </a>
                </div>
              </Card>
            ))}

            {/* Team Philosophy Card */}
            <Card variant="strong" className="p-[28px] flex flex-col justify-between border-dashed border-hair bg-white/[0.02]">
              <div>
                <div className="flex items-center gap-[8px] text-cyan font-mono text-[12px] uppercase tracking-wider mb-[14px]">
                  <Sparkles className="w-[14px] h-[14px]" />
                  Our Mission
                </div>
                <h3 className="text-[19px] font-display font-semibold text-text-hi mb-[10px]">Zero-Selector Web Research</h3>
                <p className="text-[13.5px] text-text-mid leading-[1.65]">
                  We believe web data extraction shouldn't require maintaining fragile scripts. By uniting autonomous AI agents with headless browsers, we've created a research assistant that speaks your language.
                </p>
              </div>
              <div className="pt-[16px] border-t border-hair flex items-center gap-[6px] text-[12px] text-text-dim">
                Made with <Heart className="w-[13px] h-[13px] text-red-400 fill-red-400" /> in India
              </div>
            </Card>
          </div>
        </section>

        {/* Project Links & Remotes */}
        <section className="max-w-[1000px] mx-auto text-center">
          <Card variant="strong" className="p-[36px] sm:p-[48px] relative overflow-hidden">
            <h2 className="text-[24px] sm:text-[30px] font-display font-semibold mb-[12px]">Explore Our Source Code</h2>
            <p className="text-[14.5px] text-text-mid mb-[24px] max-w-[540px] mx-auto">
              WEBISCRAP is open for academic review and developer exploration. View both our primary repository and team organization mirror.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-[14px]">
              <a href="https://github.com/manoj-n-dev/WEBISCRAP" target="_blank" rel="noopener noreferrer">
                <Button variant="primary" className="h-[44px] px-[22px] text-[14px]">
                  Primary GitHub Repo <ExternalLink className="w-[15px] h-[15px] ml-1" />
                </Button>
              </a>
              <a href="https://github.com/team3c23/WEBISCRAP" target="_blank" rel="noopener noreferrer">
                <Button className="h-[44px] px-[22px] text-[14px]">
                  Team Organization Mirror <ExternalLink className="w-[15px] h-[15px] ml-1" />
                </Button>
              </a>
            </div>
          </Card>
        </section>
      </main>

      <MarketingFooter />
    </div>
  );
}
