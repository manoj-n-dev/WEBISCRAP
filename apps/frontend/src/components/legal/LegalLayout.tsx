import React from "react";
import Link from "next/link";
import { MarketingNavbar } from "@/components/marketing/MarketingNavbar";
import { MarketingFooter } from "@/components/marketing/MarketingFooter";

export function LegalLayout({ title, intro, children }: { title: string; intro: string; children: React.ReactNode }) {
  return (
    <div className="relative min-h-dvh bg-bg-0 text-text-hi font-body overflow-x-hidden">
      <div className="bg-field"></div>
      <MarketingNavbar />
      <main className="relative z-10 pt-[96px] sm:pt-[132px] px-[16px] sm:px-[24px] pb-[64px] sm:pb-[80px]">
        <article className="max-w-[800px] mx-auto">
          <h1 className="text-[30px] sm:text-[44px] font-display font-semibold mb-[12px] sm:mb-[16px] leading-[1.15]">{title}</h1>
          <p className="text-[15px] sm:text-[16px] text-text-mid mb-[32px] sm:mb-[40px] leading-[1.7]">{intro}</p>
          <div className="flex flex-col gap-[28px] sm:gap-[32px] text-[14.5px] sm:text-[15px] leading-[1.75] text-text-mid">{children}</div>
        </article>
      </main>
      <MarketingFooter />
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
