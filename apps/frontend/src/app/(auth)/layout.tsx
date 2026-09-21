import React from "react";
import Link from "next/link";
import { Logo } from "@/components/logo/Logo";
import { WarmUp } from "@/components/system/WarmUp";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="relative min-h-dvh flex items-center justify-center py-[88px] bg-bg-0 text-text-hi font-body overflow-hidden">
      <WarmUp />
      <div className="bg-field"></div>
      
      {/* Decorative Orbs */}
      <div className="hidden sm:block absolute top-[20%] left-[20%] sm:w-[400px] sm:h-[400px] bg-[rgba(20,119,245,0.15)] rounded-full blur-[100px] mix-blend-screen pointer-events-none"></div>
      <div className="hidden sm:block absolute bottom-[20%] right-[20%] sm:w-[300px] sm:h-[300px] bg-[rgba(79,216,255,0.15)] rounded-full blur-[80px] mix-blend-screen pointer-events-none"></div>

      {/* Top Navbar for Logo */}
      <nav className="absolute top-0 left-0 right-0 p-[16px] sm:p-[24px] z-50">
        <Link href="/">
          <Logo variant="lockup" size={24} />
        </Link>
      </nav>

      <div className="relative z-10 w-full max-w-[420px] px-[16px] sm:px-[20px]">
        {children}
      </div>
    </div>
  );
}
