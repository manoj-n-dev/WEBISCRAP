import React from "react";
import type { Metadata } from "next";
import Link from "next/link";
import { LegalLayout, LegalSection, ContactLine } from "@/components/legal/LegalLayout";

export const metadata: Metadata = { title: "Privacy Policy", description: "How WEBISCRAP collects, uses, stores and protects your data." };

const Li = ({ children }: { children: React.ReactNode }) => <li>{children}</li>;

export default function PrivacyPage() {
  return (
    <LegalLayout
      title="Privacy Policy"
      intro="WEBISCRAP processes web pages and files on your behalf. This policy explains what we collect, why, who helps us process it, how long we keep it, and the choices you have."
    >
      <LegalSection heading="1. Information we collect">
        <ul className="list-disc pl-[22px] flex flex-col gap-[6px]">
          <Li><strong className="text-text-hi">Account data:</strong> your email address, optional name, and a salted hash of your password (we never store your password itself). If you sign in with Google we receive your Google account ID, email and name. Guest sessions create a temporary account without an email.</Li>
          <Li><strong className="text-text-hi">Content you provide:</strong> your messages, the URLs you ask us to open, and files you upload (PDF, Word, CSV, Excel, images). Uploaded files are converted to text or table rows and the original file is deleted immediately after processing.</Li>
          <Li><strong className="text-text-hi">Results:</strong> the structured dataset we extract, its quality score, and your chat history with the assistant.</Li>
          <Li><strong className="text-text-hi">Technical data:</strong> IP address, browser/device information, request identifiers and security events (such as sign-ins) in operational logs, used to run, secure and debug the service and to apply rate limits.</Li>
        </ul>
      </LegalSection>

      <LegalSection heading="2. How we use it">
        <p>We use your data to authenticate you, run extractions, answer your follow-up questions, produce exports, send account emails (verification and password reset), prevent abuse, and fix problems. We do not sell your data and we do not show advertising.</p>
      </LegalSection>

      <LegalSection heading="3. AI processing">
        <p>To extract data and answer questions, the relevant page text, file text, and portions of your dataset are sent to our AI provider, Groq, which processes them to generate a response. Do not upload or extract content you are not permitted to share with a processor. Do not include secrets or highly sensitive personal data.</p>
      </LegalSection>

      <LegalSection heading="4. Service providers">
        <p>We rely on these providers, each of which processes data only to provide its part of the service:</p>
        <ul className="list-disc pl-[22px] flex flex-col gap-[6px]">
          <Li>Vercel — hosts the website.</Li>
          <Li>Render — hosts the backend API and the headless browser that opens pages.</Li>
          <Li>Neon — stores account records (PostgreSQL).</Li>
          <Li>Upstash — stores temporary chat sessions, datasets and rate-limit counters (Redis).</Li>
          <Li>Groq — AI language-model processing.</Li>
          <Li>Google — optional sign-in with Google.</Li>
          <Li>An email delivery provider — sends verification and password-reset emails.</Li>
        </ul>
        <p>These providers may process data in countries other than your own.</p>
      </LegalSection>

      <LegalSection heading="5. How long we keep data">
        <ul className="list-disc pl-[22px] flex flex-col gap-[6px]">
          <Li>Chats, uploaded-file text and extracted datasets: automatically deleted after up to 14 days, or immediately when you delete the chat. Guest data is also deleted when the guest logs out.</Li>
          <Li>Verification and password-reset links: expire after a short period and can be used once.</Li>
          <Li>Account records: kept until you ask us to delete your account.</Li>
          <Li>Operational logs: kept for a limited period for security and debugging.</Li>
        </ul>
      </LegalSection>

      <LegalSection heading="6. Cookies and local storage">
        <p>We use one essential, HttpOnly cookie that keeps you signed in (a refresh token). Short-lived access tokens are held in memory only. We do not use advertising or cross-site tracking cookies. If you sign in with Google, Google may set its own cookies on its pages.</p>
      </LegalSection>

      <LegalSection heading="7. Security">
        <p>We use encrypted connections (HTTPS), hashed passwords, access checks so each session is only readable by its owner, network protections that block requests to private addresses, rate limiting, and automatic data expiry. No system is perfectly secure, so please use a strong, unique password.</p>
      </LegalSection>

      <LegalSection heading="8. Your choices and rights">
        <p>You can delete any chat from the sidebar, export your data at any time, and log out to end your session. You can ask us to access, correct or delete your account data, or to stop processing it, by contacting us. Depending on where you live you may have additional rights under laws such as India&apos;s Digital Personal Data Protection Act; we will respond as required.</p>
      </LegalSection>

      <LegalSection heading="9. Data from websites you extract">
        <p>Web pages can contain personal information about other people. You are responsible for having a lawful basis to collect and use it, and for complying with the source website&apos;s terms. See our <Link href="/terms" className="text-signal-400 hover:text-signal-300 underline underline-offset-4">Terms of Service</Link>.</p>
      </LegalSection>

      <LegalSection heading="10. Children">
        <p>WEBISCRAP is intended for people aged 18 or older (or the age of majority where they live). We do not knowingly collect data from children.</p>
      </LegalSection>

      <LegalSection heading="11. Changes and contact">
        <p>We may update this policy as the product changes; the version on this page is the current one. For privacy questions or requests, contact us via <ContactLine />.</p>
      </LegalSection>
    </LegalLayout>
  );
}
