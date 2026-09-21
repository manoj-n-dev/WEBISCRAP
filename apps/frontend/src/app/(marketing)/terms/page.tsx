import React from "react";
import type { Metadata } from "next";
import Link from "next/link";
import { LegalLayout, LegalSection, ContactLine } from "@/components/legal/LegalLayout";

export const metadata: Metadata = { title: "Terms of Service", description: "The rules for using WEBISCRAP, the AI web and document data extraction platform." };

export default function TermsPage() {
  return (
    <LegalLayout
      title="Terms of Service"
      intro="These terms explain what you can expect from WEBISCRAP and what we expect from you. By creating an account, continuing as a guest, or otherwise using WEBISCRAP, you agree to them."
    >
      <LegalSection heading="1. What WEBISCRAP does">
        <p>WEBISCRAP is an AI-assisted tool that turns public web pages and files you upload (CSV, Excel, PDF, Word documents and images) into structured tables. A team of software agents plans the task, opens the page or reads your file, extracts and cleans the data, scores its quality, and lets you ask follow-up questions and export the result as CSV, Excel, JSON, Markdown or PDF.</p>
        <p>WEBISCRAP is a student-built project offered on an &quot;as available&quot; basis. Features may change, be limited, or be withdrawn.</p>
      </LegalSection>

      <LegalSection heading="2. Accounts and guest access">
        <p>You can sign up with an email address and password, sign in with Google, or use a temporary guest session. Email accounts must be verified before you can sign in. Keep your credentials private; you are responsible for activity under your account. Phone-number sign-in is not currently available.</p>
        <p>Guest sessions are temporary. Guest chats and data are removed when you log out or when they expire, so export anything you want to keep.</p>
        <p>You must be at least 18 years old, or the age of majority where you live, to use WEBISCRAP.</p>
      </LegalSection>

      <LegalSection heading="3. Acceptable use">
        <p>You may use WEBISCRAP only for lawful purposes. You agree not to:</p>
        <ul className="list-disc pl-[22px] flex flex-col gap-[6px]">
          <li>extract data in violation of a website&apos;s terms of service, robots.txt directives, technical restrictions, or applicable law, including copyright, database-rights and privacy laws;</li>
          <li>collect sensitive personal data about individuals, or use extracted personal data for spam, harassment, profiling, or any unlawful purpose;</li>
          <li>attempt to reach private, internal or local network addresses, bypass paywalls or logins, or circumvent access controls or rate limits;</li>
          <li>overload third-party websites or our service, or use WEBISCRAP for denial-of-service, credential stuffing or other attacks;</li>
          <li>upload malware, or files you do not have the right to process;</li>
          <li>probe, reverse engineer or disrupt the service, or misuse the AI features to generate harmful content.</li>
        </ul>
        <p>You are responsible for making sure you are allowed to scrape and use the content you ask WEBISCRAP to process. We may block requests, limit usage, or suspend accounts that put the service or others at risk.</p>
      </LegalSection>

      <LegalSection heading="4. Your content and extracted data">
        <p>You keep ownership of the files you upload and of the data you are entitled to extract. You give WEBISCRAP permission to process that content, including sending the relevant text to our AI provider, solely to deliver the results you requested. Content from third-party websites remains the property of its owners; your rights to use it depend on the source and the law.</p>
      </LegalSection>

      <LegalSection heading="5. AI output and accuracy">
        <p>WEBISCRAP uses large language models. They can misread dynamic pages, omit rows, or produce incorrect values. The data-quality score is an automated estimate of completeness, not a guarantee of accuracy. Always review extracted data before relying on it for financial, legal, medical or other important decisions.</p>
      </LegalSection>

      <LegalSection heading="6. Fair use and availability">
        <p>We apply rate limits, file-size limits (currently 20 MB per file) and dataset-size limits to keep the service available for everyone. The AI provider we use enforces its own usage quotas; when they are reached you will see an &quot;AI usage limit reached&quot; notice and can try again later.</p>
        <p>WEBISCRAP runs on shared free-tier infrastructure. It can be slow to start after a period of inactivity, and we do not guarantee uptime, continuity of stored data, or any particular response time.</p>
      </LegalSection>

      <LegalSection heading="7. Data retention">
        <p>Chats, uploaded-file text, and extracted datasets are kept only for a limited time (up to 14 days) and are deleted automatically afterwards. You can delete a chat at any time from the sidebar. See the <Link href="/privacy" className="text-signal-400 hover:text-signal-300 underline underline-offset-4">Privacy Policy</Link> for details.</p>
      </LegalSection>

      <LegalSection heading="8. Disclaimer of warranties">
        <p>To the fullest extent permitted by law, WEBISCRAP is provided &quot;as is&quot; and &quot;as available&quot;, without warranties of any kind, express or implied, including merchantability, fitness for a particular purpose, accuracy, and non-infringement.</p>
      </LegalSection>

      <LegalSection heading="9. Limitation of liability">
        <p>To the fullest extent permitted by law, the WEBISCRAP team is not liable for indirect, incidental, special or consequential damages, or for loss of data, profits or business, arising from your use of (or inability to use) the service, including claims arising from how you use data you extract. Nothing in these terms limits liability that cannot be limited by law.</p>
      </LegalSection>

      <LegalSection heading="10. Suspension and termination">
        <p>You may stop using WEBISCRAP at any time and may ask us to delete your account. We may suspend or terminate access if these terms are breached or if needed to protect the service, other users, or third-party websites.</p>
      </LegalSection>

      <LegalSection heading="11. Changes to these terms">
        <p>We may update these terms as WEBISCRAP evolves. The version published on this page is the one that applies; continuing to use the service after a change means you accept it.</p>
      </LegalSection>

      <LegalSection heading="12. Governing law and contact">
        <p>These terms are governed by the laws of India. Questions about these terms can be sent via <ContactLine />.</p>
      </LegalSection>
    </LegalLayout>
  );
}
