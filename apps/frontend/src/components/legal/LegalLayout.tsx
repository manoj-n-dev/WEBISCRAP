import React from "react";
import Link from "next/link";
import { Logo } from "@/components/logo/Logo";
import { Button } from "@/components/ui/Button";

export function LegalLayout({ title, intro, children }: { title: string; intro: string; children: React.ReactNode }) {
  return (
    <div className="relative min-h-dvh bg-bg-0 text-text-hi font-body overflow-x-hidden">
      <div className="bg-field"></div>
      <nav className="fixed top-0 left-0 right-0 h-[64px] sm:h-[72px] flex items-center justify-between px-[16px] sm:px-[32px] border-b border-hair bg-[rgba(5,7,12,0.6)] backdrop-blur-md z-50">
        <Link href="/" aria-label="WEBISCRAP home"><Logo variant="lockup" size={24} /></Link>
        <div className="flex items-center gap-[8px] sm:gap-[16px]">
          <Link href="/terms" className="hidden sm:block text-[13px] text-text-mid hover:text-text-hi">Terms</Link>
          <Link href="/privacy" className="hidden sm:block text-[13px] text-text-mid hover:text-text-hi">Privacy</Link>
          <Link href="/login"><Button variant="ghost" className="px-[14px] py-[9px] text-[13px]">Sign In</Button></Link>
        </div>
      </nav>
      <main className="relative z-10 pt-[96px] sm:pt-[132px] px-[16px] sm:px-[24px] pb-[64px] sm:pb-[80px]">
        <article className="max-w-[800px] mx-auto">
          <h1 className="text-[30px] sm:text-[44px] font-display font-semibold mb-[12px] sm:mb-[16px] leading-[1.15]">{title}</h1>
          <p className="text-[15px] sm:text-[16px] text-text-mid mb-[32px] sm:mb-[40px] leading-[1.7]">{intro}</p>
          <div className="flex flex-col gap-[28px] sm:gap-[32px] text-[14.5px] sm:text-[15px] leading-[1.75] text-text-mid">{children}</div>
        </article>
      </main>
      <footer className="border-t border-hair py-[28px] text-center text-[13px] text-text-dim px-[16px]">
        <div className="flex flex-wrap justify-center gap-x-[24px] gap-y-[8px]">
          <Link href="/terms" className="hover:text-text-hi">Terms</Link>
          <Link href="/privacy" className="hover:text-text-hi">Privacy</Link>
          <Link href="/" className="hover:text-text-hi">Home</Link>
        </div>
      </footer>
    </div>
  );
}

export function LegalSection({ heading, children }: { heading: string; children: React.ReactNode }) {
  return (
    <section>
      <h2 className="text-[18px] sm:text-[20px] font-display font-semibold text-text-hi mb-[10px]">{heading}</h2>
      <div className="flex flex-col gap-[10px]">{children}</div>
    </section>
  );
}

export function ContactLine() {
  const email = process.env.NEXT_PUBLIC_CONTACT_EMAIL;
  return email ? (
    <a href={`mailto:${email}`} className="text-signal-400 hover:text-signal-300 underline underline-offset-4">{email}</a>
  ) : (
    <a href="https://github.com/manoj-n-dev/WEBISCRAP/issues" target="_blank" rel="noopener noreferrer" className="text-signal-400 hover:text-signal-300 underline underline-offset-4">our GitHub issue tracker</a>
  );
}
