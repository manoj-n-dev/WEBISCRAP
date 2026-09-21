import React from "react";
import Link from "next/link";
import { Terminal, Activity, Mail, ExternalLink, Bot, CheckCircle2 } from "lucide-react";
import { Logo } from "@/components/logo/Logo";

function GithubIcon({ className = "w-4 h-4" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4" />
      <path d="M9 18c-4.51 2-5-2-7-2" />
    </svg>
  );
}

export function MarketingFooter() {
  return (
    <footer className="border-t border-hair bg-bg-0/90 text-[13px] text-text-dim relative z-10 pt-[64px] pb-[32px] px-[16px] sm:px-[32px]">
      <div className="max-w-[1200px] mx-auto">
        {/* Top 4-Column Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-[40px] lg:gap-[32px] mb-[56px]">
          {/* Col 1: Brand & Social */}
          <div className="flex flex-col items-start">
            <div className="flex items-center gap-[12px] mb-[12px]">
              <div className="w-[36px] h-[36px] rounded-lg bg-[rgba(20,119,245,0.12)] border border-[rgba(20,119,245,0.25)] flex items-center justify-center text-cyan shadow-[0_0_15px_rgba(20,119,245,0.2)]">
                <Bot className="w-[20px] h-[20px]" />
              </div>
              <div>
                <span className="font-display font-bold text-[16px] tracking-tight text-text-hi">WEBISCRAP</span>
                <div className="font-mono text-[9.5px] uppercase tracking-[0.14em] text-cyan">Conversational AI Extraction</div>
              </div>
            </div>
            <p className="text-[12.5px] text-text-mid leading-[1.65] mb-[20px] max-w-[280px]">
              The next-generation research platform turning unstructured websites, PDFs, CSVs, and documents into clean, structured data with natural language.
            </p>
            <div className="flex items-center gap-[12px]">
              <a
                href="https://github.com/manoj-n-dev/WEBISCRAP"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="GitHub"
                className="w-[34px] h-[34px] rounded-full border border-hair bg-white/5 hover:bg-white/10 hover:text-text-hi flex items-center justify-center transition-colors text-text-mid"
              >
                <GithubIcon className="w-[16px] h-[16px]" />
              </a>
              <a
                href="https://github.com/team3c23/WEBISCRAP"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Team Mirror"
                title="Team Mirror"
                className="w-[34px] h-[34px] rounded-full border border-hair bg-white/5 hover:bg-white/10 hover:text-text-hi flex items-center justify-center transition-colors text-text-mid"
              >
                <Terminal className="w-[15px] h-[15px]" />
              </a>
              <a
                href="mailto:noreply@webiscrap.com"
                aria-label="Email Support"
                className="w-[34px] h-[34px] rounded-full border border-hair bg-white/5 hover:bg-white/10 hover:text-text-hi flex items-center justify-center transition-colors text-text-mid"
              >
                <Mail className="w-[16px] h-[16px]" />
              </a>
            </div>
          </div>

          {/* Col 2: Resources */}
          <div>
            <div className="flex items-center gap-[8px] font-mono text-[11px] uppercase tracking-[0.12em] text-text-hi mb-[18px]">
              <Terminal className="w-[14px] h-[14px] text-cyan" />
              <span>Resources</span>
            </div>
            <ul className="flex flex-col gap-[10px] text-[13px]">
              <li>
                <Link href="/how-it-works" className="hover:text-text-hi transition-colors">How It Works</Link>
              </li>
              <li>
                <Link href="/docs" className="hover:text-text-hi transition-colors">Documentation</Link>
              </li>
              <li>
                <Link href="/#agents" className="hover:text-text-hi transition-colors">The 9 Agents Swarm</Link>
              </li>
              <li>
                <Link href="/features" className="hover:text-text-hi transition-colors">Features & Tech</Link>
              </li>
              <li>
                <Link href="/privacy" className="hover:text-text-hi transition-colors">Privacy Policy</Link>
              </li>
              <li>
                <Link href="/terms" className="hover:text-text-hi transition-colors">Terms of Service</Link>
              </li>
            </ul>
          </div>

          {/* Col 3: Ecosystem */}
          <div>
            <div className="flex items-center gap-[8px] font-mono text-[11px] uppercase tracking-[0.12em] text-text-hi mb-[18px]">
              <Activity className="w-[14px] h-[14px] text-cyan" />
              <span>Ecosystem</span>
            </div>
            <ul className="flex flex-col gap-[10px] text-[13px]">
              <li>
                <Link href="/creators" className="hover:text-text-hi transition-colors">Creators & Core Team</Link>
              </li>
              <li>
                <a href="https://github.com/manoj-n-dev/WEBISCRAP" target="_blank" rel="noopener noreferrer" className="hover:text-text-hi transition-colors flex items-center gap-1.5">
                  GitHub Repository <ExternalLink className="w-[11px] h-[11px] opacity-60" />
                </a>
              </li>
              <li>
                <a href="https://github.com/team3c23/WEBISCRAP" target="_blank" rel="noopener noreferrer" className="hover:text-text-hi transition-colors flex items-center gap-1.5">
                  Team Organization <ExternalLink className="w-[11px] h-[11px] opacity-60" />
                </a>
              </li>
              <li>
                <Link href="/login" className="hover:text-text-hi transition-colors">Interactive Playground</Link>
              </li>
              <li>
                <Link href="/docs#api" className="hover:text-text-hi transition-colors">REST API Spec</Link>
              </li>
              <li>
                <Link href="/login" className="hover:text-text-hi transition-colors">Guest Extraction Mode</Link>
              </li>
            </ul>
          </div>

          {/* Col 4: System Status Widget */}
          <div>
            <div className="font-mono text-[11px] uppercase tracking-[0.12em] text-text-hi mb-[18px]">
              System Status
            </div>
            <div className="rounded-xl border border-glass-border-strong bg-[rgba(10,14,23,0.85)] p-[18px] backdrop-blur-md shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
              <div className="flex items-center justify-between gap-[8px] pb-[12px] border-b border-hair">
                <span className="font-mono text-[11px] text-text-dim uppercase tracking-wider">Network</span>
                <span className="inline-flex items-center gap-[6px] font-mono text-[11px] text-cyan font-semibold">
                  <span className="w-[7px] h-[7px] rounded-full bg-cyan animate-[pulseDot_1.2s_ease-in-out_infinite]" />
                  OPERATIONAL
                </span>
              </div>
              <div className="pt-[12px] space-y-[10px]">
                <div className="flex items-center justify-between text-[11.5px]">
                  <span className="text-text-dim">Engine Version</span>
                  <span className="font-mono text-text-hi font-medium">Pipeline v2.0 Live</span>
                </div>
                <div className="flex items-center justify-between text-[11.5px]">
                  <span className="text-text-dim">AI Agents</span>
                  <span className="font-mono text-text-hi font-medium">9 / 9 Swarm Online</span>
                </div>
                <div className="flex items-center justify-between text-[11.5px]">
                  <span className="text-text-dim">Session Store</span>
                  <span className="font-mono text-text-hi font-medium">Redis Cluster Active</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-hair pt-[24px] flex flex-col sm:flex-row items-center justify-between gap-[16px] text-[12px]">
          <div>© {new Date().getFullYear()} WEBISCRAP. All rights reserved.</div>
          <div className="flex items-center gap-[6px] text-text-dim">
            ENGINEERED WITH <span className="text-red-400">❤️</span> BY{" "}
            <Link href="/creators" className="font-medium text-cyan hover:underline underline-offset-4">
              MANOJ &amp; TEAM
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
