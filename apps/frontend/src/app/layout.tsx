import React from "react";
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "WEBISCRAP | AI Web Data Extraction",
  description: "Extract Anything. Ask Naturally. Export Instantly.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="font-sans antialiased text-text-hi bg-bg-0" suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
