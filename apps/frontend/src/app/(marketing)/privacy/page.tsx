import React from "react";
import Link from "next/link";
import { Logo } from "@/components/logo/Logo";
import { Button } from "@/components/ui/Button";

export default function PrivacyPage() {
  return (
    <div className="relative min-h-screen bg-bg-0 text-text-hi font-body overflow-x-hidden">
      <div className="bg-field"></div>
      
      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 h-[72px] flex items-center justify-between px-[32px] border-b border-[rgba(255,255,255,0.04)] bg-[rgba(5,7,12,0.6)] backdrop-blur-md z-50">
        <Link href="/">
          <Logo variant="lockup" size={24} />
        </Link>
        <div className="flex items-center gap-[16px]">
          <Link href="/login">
            <Button variant="ghost">Sign In</Button>
          </Link>
        </div>
      </nav>

      <main className="relative z-10 pt-[140px] px-[24px] pb-[80px]">
        <div className="max-w-[800px] mx-auto">
          <h1 className="text-[48px] font-display font-semibold mb-[24px]">Privacy Policy</h1>
          <p className="text-text-mid mb-[40px]">Last updated: {new Date().toLocaleDateString()}</p>
          
          <div className="prose prose-invert max-w-none text-text-mid space-y-[24px]">
            <p>At WEBISCRAP, we take your privacy seriously. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you visit our website and use our service.</p>
            
            <h2 className="text-[24px] font-display font-medium text-text-hi mt-[40px] mb-[16px]">1. Information We Collect</h2>
            <p>We collect personal information that you voluntarily provide to us when registering at the Services, expressing an interest in obtaining information about us or our products and services, when participating in activities on the Services or otherwise contacting us.</p>
            
            <h2 className="text-[24px] font-display font-medium text-text-hi mt-[40px] mb-[16px]">2. How We Use Your Information</h2>
            <p>We use personal information collected via our Services for a variety of business purposes described below. We process your personal information for these purposes in reliance on our legitimate business interests, in order to enter into or perform a contract with you, with your consent, and/or for compliance with our legal obligations.</p>
            
            <h2 className="text-[24px] font-display font-medium text-text-hi mt-[40px] mb-[16px]">3. Data Security</h2>
            <p>We have implemented appropriate technical and organizational security measures designed to protect the security of any personal information we process. However, please also remember that we cannot guarantee that the internet itself is 100% secure.</p>
            
            <h2 className="text-[24px] font-display font-medium text-text-hi mt-[40px] mb-[16px]">4. Contact Us</h2>
            <p>If you have questions or comments about this policy, you may email us at privacy@webiscrap.com.</p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-hair py-[40px] text-center text-[13px] text-text-dim">
        <div className="max-w-[1200px] mx-auto flex items-center justify-between px-[24px]">
          <Logo variant="lockup" size={20} className="opacity-50 grayscale" />
          <div className="flex gap-[24px]">
            <Link href="/terms" className="hover:text-text-hi">Terms</Link>
            <Link href="/privacy" className="hover:text-text-hi">Privacy</Link>
          </div>
          <div>© {new Date().getFullYear()} Webiscrap. All rights reserved.</div>
        </div>
      </footer>
    </div>
  );
}
