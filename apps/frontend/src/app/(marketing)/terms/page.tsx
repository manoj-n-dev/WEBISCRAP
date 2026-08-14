import React from "react";
import Link from "next/link";
import { Logo } from "@/components/logo/Logo";
import { Button } from "@/components/ui/Button";

export default function TermsPage() {
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
          <h1 className="text-[48px] font-display font-semibold mb-[24px]">Terms of Service</h1>
          <p className="text-text-mid mb-[40px]">Last updated: {new Date().toLocaleDateString()}</p>
          
          <div className="prose prose-invert max-w-none text-text-mid space-y-[24px]">
            <p>Welcome to WEBISCRAP. By using our service, you agree to the following terms and conditions.</p>
            
            <h2 className="text-[24px] font-display font-medium text-text-hi mt-[40px] mb-[16px]">1. Use of Service</h2>
            <p>WEBISCRAP provides AI-powered web data extraction. You agree to use this service only for lawful purposes and in accordance with the terms of service of the websites you are extracting data from.</p>
            
            <h2 className="text-[24px] font-display font-medium text-text-hi mt-[40px] mb-[16px]">2. User Accounts</h2>
            <p>You must provide accurate and complete information when creating an account. You are responsible for maintaining the security of your password and account.</p>
            
            <h2 className="text-[24px] font-display font-medium text-text-hi mt-[40px] mb-[16px]">3. Data and Privacy</h2>
            <p>We respect your privacy. Please refer to our Privacy Policy for details on how we collect, use, and protect your information.</p>
            
            <h2 className="text-[24px] font-display font-medium text-text-hi mt-[40px] mb-[16px]">4. Limitations of Liability</h2>
            <p>WEBISCRAP is not responsible for the accuracy, legality, or reliability of the data extracted using our service. You are solely responsible for how you use the extracted data.</p>
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
