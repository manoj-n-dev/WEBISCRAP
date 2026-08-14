"use client";

import React from "react";
import Link from "next/link";
import { Logo } from "@/components/logo/Logo";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { PipelineStrip } from "@/components/chat/PipelineStrip";
import { ArrowRight, Bot, Target, Shield, Table2, Zap, BrainCircuit, ScanSearch, CheckCircle2, History, MessageSquare } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="relative min-h-screen bg-bg-0 text-text-hi font-body overflow-x-hidden selection:bg-[rgba(20,119,245,0.3)]">
      <div className="bg-field"></div>

      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 h-[72px] flex items-center justify-between px-[32px] border-b border-[rgba(255,255,255,0.04)] bg-[rgba(5,7,12,0.6)] backdrop-blur-md z-50">
        <Logo variant="lockup" size={24} />
        <div className="flex items-center gap-[32px] text-[13px] font-medium text-text-mid">
          <Link href="#how-it-works" className="hover:text-text-hi transition-colors">How it Works</Link>
          <Link href="#agents" className="hover:text-text-hi transition-colors">The 9 Agents</Link>
          <Link href="#features" className="hover:text-text-hi transition-colors">Features</Link>
        </div>
        <div className="flex items-center gap-[16px]">
          <Link href="/login">
            <Button variant="ghost">Sign In</Button>
          </Link>
          <Link href="/login">
            <Button variant="primary">Start Extracting</Button>
          </Link>
        </div>
      </nav>

      <main className="relative z-10 pt-[140px] px-[24px]">
        {/* Hero Section */}
        <section className="max-w-[1200px] mx-auto text-center mb-[120px]">
          <div className="inline-flex items-center gap-[8px] px-[12px] py-[6px] rounded-pill border border-glass-border bg-white/5 font-mono text-[11px] text-cyan tracking-[0.04em] mb-[24px]">
            <span className="w-[6px] h-[6px] rounded-full bg-cyan animate-[pulseDot_1.2s_ease-in-out_infinite]"></span>
            AGENT PIPELINE v2.0 LIVE
          </div>
          <h1 className="text-[64px] font-display font-semibold leading-[1.1] tracking-tight mb-[24px]">
            Scrape the web with <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-signal-400 to-cyan">plain natural language.</span>
          </h1>
          <p className="text-[18px] text-text-mid max-w-[600px] mx-auto mb-[40px] leading-[1.6]">
            No CSS selectors. No XPath. No brittle scripts. Just paste a URL, describe what you want in English or Hindi, and our 9-agent pipeline handles the rest.
          </p>
          <div className="flex justify-center gap-[16px]">
            <Link href="/login">
              <Button variant="primary" className="h-[48px] px-[28px] text-[15px]">
                Start Free Extraction <ArrowRight className="w-[18px] h-[18px]" />
              </Button>
            </Link>
            <Button className="h-[48px] px-[28px] text-[15px]" onClick={() => document.getElementById('agents')?.scrollIntoView({ behavior: 'smooth' })}>View Examples</Button>
          </div>

          {/* Hero Mock Chat */}
          <div className="mt-[80px] max-w-[800px] mx-auto">
            <Card variant="strong" className="p-[24px] text-left relative overflow-hidden">
              <div className="absolute top-0 left-0 right-0 h-[4px] bg-gradient-to-r from-signal-400 via-cyan to-signal-500"></div>

              <MessageBubble role="user" content="Extract the top 20 trending repositories from GitHub today, including their name, description, star count, and primary language." />

              <div className="my-[24px] ml-[42px] border-l-2 border-[rgba(130,170,255,0.1)] pl-[24px]">
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

        {/* 9 Agents Grid */}
        <section id="agents" className="max-w-[1200px] mx-auto mb-[120px]">
          <div className="text-center mb-[48px]">
            <h2 className="text-[32px] font-display font-semibold mb-[12px]">The 9-Agent Backend</h2>
            <p className="text-text-mid">A specialized swarm of AI agents working in concert to guarantee flawless extraction.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-[20px]">
            {[
              { icon: Target, title: "Planner", desc: "Analyzes your natural language request and formulates the extraction strategy." },
              { icon: ScanSearch, title: "Analyzer", desc: "Inspects the target URL's DOM structure and identifies data clusters." },
              { icon: Bot, title: "Browser", desc: "Navigates headless browsers, handles pagination, scrolling, and popups." },
              { icon: BrainCircuit, title: "Extractor", desc: "Uses LLMs to map unstructured HTML to your requested schema." },
              { icon: Zap, title: "Cleaner", desc: "Normalizes data types, fixes formatting, and removes hallucinations." },
              { icon: Shield, title: "Validator", desc: "Cross-references extracted data against constraints to ensure 100% accuracy." },
              { icon: History, title: "Memory", desc: "Maintains session context for follow-up refinements and corrections." },
              { icon: MessageSquare, title: "Conversation", desc: "Manages the chat interface and reports pipeline status back to you." },
              { icon: Table2, title: "Export", desc: "Compiles the validated dataset into CSV, JSON, Excel, or PDF." }
            ].map((agent, i) => (
              <Card key={i} className="p-[24px] group hover:border-[rgba(130,170,255,0.3)] transition-colors">
                <div className="w-[40px] h-[40px] rounded-lg bg-[rgba(20,119,245,0.06)] border border-[rgba(20,119,245,0.12)] flex items-center justify-center text-signal-400 mb-[16px] group-hover:bg-signal-500 group-hover:text-white transition-colors">
                  <agent.icon className="w-[20px] h-[20px]" />
                </div>
                <h3 className="font-display font-semibold text-[16px] mb-[8px]">{agent.title}</h3>
                <p className="text-[13px] text-text-dim leading-[1.6]">{agent.desc}</p>
              </Card>
            ))}
          </div>
        </section>

        {/* CTA Section */}
        <section className="max-w-[1200px] mx-auto mb-[120px]">
          <Card variant="strong" className="p-[64px] text-center bg-[url('/noise.png')] bg-repeat relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-b from-transparent to-[rgba(20,119,245,0.05)]"></div>
            <div className="relative z-10">
              <h2 className="text-[40px] font-display font-semibold mb-[16px]">Ready to ditch the selectors?</h2>
              <p className="text-[16px] text-text-mid mb-[32px] max-w-[500px] mx-auto">
                Join developers and researchers using WEBISCRAP to turn the internet into a database.
              </p>
              <Link href="/login">
                <Button variant="primary" className="h-[48px] px-[32px] text-[15px]">
                  Start Extracting Now
                </Button>
              </Link>
            </div>
          </Card>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-hair py-[40px] text-center text-[13px] text-text-dim">
        <div className="max-w-[1200px] mx-auto flex items-center justify-between px-[24px]">
          <Logo variant="lockup" size={20} className="opacity-50 grayscale" />
          <div className="flex gap-[24px]">
            <Link href="/terms" className="hover:text-text-hi">Terms</Link>
            <Link href="/privacy" className="hover:text-text-hi">Privacy</Link>
            <Link href="#agents" className="hover:text-text-hi">Documentation</Link>
          </div>
          <div>© {new Date().getFullYear()} Webiscrap. All rights reserved.</div>
        </div>
      </footer>
    </div>
  );
}
