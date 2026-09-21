import React from "react";
import type { Metadata, Viewport } from "next";
import { Inter, Space_Grotesk, JetBrains_Mono } from "next/font/google";
import { CustomCursor } from "@/components/ui/CustomCursor";
import "./globals.css";

// next/font self-hosts the fonts at build time (the design tokens referenced these families but never loaded them).
const inter = Inter({ subsets: ["latin"], variable: "--font-inter", display: "swap" });
const spaceGrotesk = Space_Grotesk({ subsets: ["latin"], weight: ["500", "600"], variable: "--font-space-grotesk", display: "swap" });
const jetbrains = JetBrains_Mono({ subsets: ["latin"], weight: ["400", "500"], variable: "--font-jetbrains-mono", display: "swap" });

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://webiscrap.vercel.app";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: "WEBISCRAP | AI Web Data Extraction", template: "%s | WEBISCRAP" },
  description: "Extract Anything. Ask Naturally. Export Instantly. Turn websites, PDFs, spreadsheets and images into clean, structured data.",
  applicationName: "WEBISCRAP",
  manifest: "/manifest.webmanifest",
  openGraph: { title: "WEBISCRAP | AI Web Data Extraction", description: "Scrape. Structure. Succeed.", siteName: "WEBISCRAP", type: "website" },
  twitter: { card: "summary_large_image", title: "WEBISCRAP", description: "Scrape. Structure. Succeed." },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: "#05070c",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${inter.variable} ${spaceGrotesk.variable} ${jetbrains.variable}`} suppressHydrationWarning>
      <body className="font-body antialiased text-text-hi bg-bg-0" suppressHydrationWarning>
        <CustomCursor />
        {children}
      </body>
    </html>
  );
}
