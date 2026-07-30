"use client";

import Image from "next/image";
import { Globe, ShoppingCart, FileText, BarChart3 } from "lucide-react";

interface WelcomeScreenProps {
  onExampleClick: (message: string, url?: string) => void;
}

const examples = [
  {
    icon: ShoppingCart,
    title: "Extract Product Prices",
    message: "Extract all product names and prices",
    url: "https://books.toscrape.com",
  },
  {
    icon: Globe,
    title: "Scrape News Headlines",
    message: "Get all the top headlines with links",
    url: "https://news.ycombinator.com",
  },
  {
    icon: FileText,
    title: "Collect Quotes",
    message: "Extract all quotes with their authors",
    url: "https://quotes.toscrape.com",
  },
  {
    icon: BarChart3,
    title: "Table Extraction",
    message: "Extract all data from the tables on this page",
    url: "",
  },
];

export function WelcomeScreen({ onExampleClick }: WelcomeScreenProps) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
      {/* Branding Logo */}
      <div className="mb-8 animate-fade-in">
        <Image
          src="/assets/branding-logo.png"
          alt="WEBISCRAP"
          width={80}
          height={80}
          className="rounded-2xl"
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.style.display = "none";
          }}
        />
      </div>

      <h2 className="text-2xl font-semibold text-foreground mb-2 text-center animate-fade-in">
        What would you like to extract?
      </h2>
      <p className="text-muted text-center max-w-md mb-10 text-sm">
        Paste a URL, describe what you need in plain language,
        and let the AI agents handle the rest.
      </p>

      {/* Example suggestions */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-xl animate-fade-in">
        {examples.map((example) => {
          const Icon = example.icon;
          return (
            <button
              key={example.title}
              onClick={() => onExampleClick(example.message, example.url)}
              className="group flex items-start gap-3 p-4 rounded-xl border border-border bg-surface hover:bg-surface-hover transition-colors text-left cursor-pointer"
            >
              <Icon className="w-5 h-5 text-muted group-hover:text-foreground transition-colors mt-0.5 shrink-0" />
              <div>
                <p className="text-sm font-medium text-foreground">
                  {example.title}
                </p>
                <p className="text-xs text-muted mt-0.5">
                  {example.message}
                </p>
              </div>
            </button>
          );
        })}
      </div>

      <p className="mt-10 text-xs text-muted">
        Supports English, Hindi, Telugu, Tamil, Hinglish, and more
      </p>
    </div>
  );
}
