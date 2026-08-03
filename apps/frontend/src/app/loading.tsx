import React from "react";

export default function Loading() {
  return (
    <div className="relative min-h-screen flex flex-col items-center justify-center gap-7 bg-bg-0 text-text-hi font-body overflow-hidden">
      <div className="bg-field"></div>
      
      <div className="relative z-10 flex flex-col items-center justify-center gap-[28px]">
        {/* Animated Mark */}
        <div className="relative w-[120px] h-[120px] flex items-center justify-center">
          <div className="absolute inset-[-18px] rounded-full border border-[rgba(130,170,255,0.08)]"></div>
          <div className="absolute inset-0 rounded-full border border-transparent border-t-signal-400 animate-[spin_1.6s_linear_infinite]"></div>
          
          <svg
            className="animate-[pulseGlow_2.4s_ease-in-out_infinite]"
            width="56"
            height="56"
            viewBox="0 0 56 56"
            fill="none"
          >
            <path
              d="M6 16 L20 44 L28 26 L36 44 L50 16"
              stroke="url(#gsplash)"
              strokeWidth="5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M28 8 v14 M22 14 v6 M34 14 v6"
              stroke="url(#gsplash)"
              strokeWidth="3"
              strokeLinecap="round"
            />
            <defs>
              <linearGradient id="gsplash" x1="6" y1="8" x2="50" y2="44" gradientUnits="userSpaceOnUse">
                <stop stopColor="var(--color-signal-300)" />
                <stop offset="1" stopColor="var(--color-signal-500)" />
              </linearGradient>
            </defs>
          </svg>
        </div>

        {/* Brand Block */}
        <div className="text-center">
          <div className="font-display text-[30px] font-semibold tracking-[0.01em]">
            WEB<span className="text-signal-400">I</span>SCRAP
          </div>
          <div className="mt-2 font-mono text-[11px] tracking-[0.3em] text-text-dim uppercase">
            Scrape · Structure · Succeed
          </div>
        </div>

        {/* Loader Bar */}
        <div className="w-[220px] h-[2px] bg-white/5 rounded-sm overflow-hidden relative">
          <div className="absolute top-0 bottom-0 left-0 w-[38%] bg-gradient-to-r from-transparent via-signal-400 to-cyan animate-[sweep_1.4s_ease-in-out_infinite]"></div>
        </div>
        
        {/* Status Line */}
        <div className="font-mono text-[11px] text-text-dim tracking-[0.04em]">
          Waking the agent pipeline…
        </div>
      </div>
    </div>
  );
}
