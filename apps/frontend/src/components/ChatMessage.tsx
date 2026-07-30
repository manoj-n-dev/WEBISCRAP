"use client";

import Image from "next/image";
import { User } from "lucide-react";
import type { Message } from "@/app/page";

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-4 animate-fade-in ${isUser ? "flex-row-reverse" : ""}`}>
      {/* Avatar */}
      <div className="shrink-0 mt-1">
        {isUser ? (
          <div className="w-7 h-7 rounded-full bg-surface-hover flex items-center justify-center">
            <User className="w-4 h-4 text-muted" />
          </div>
        ) : (
          <div className="w-7 h-7 rounded-full bg-primary/15 flex items-center justify-center overflow-hidden">
            <Image
              src="/assets/inner-logo.png"
              alt="AI"
              width={20}
              height={20}
              className="rounded-full"
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.style.display = "none";
                if (target.parentElement) {
                  target.parentElement.innerHTML = `<svg class="w-4 h-4 text-primary" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z" /></svg>`;
                }
              }}
            />
          </div>
        )}
      </div>

      {/* Content */}
      <div className={`flex-1 min-w-0 ${isUser ? "text-right" : ""}`}>
        <div
          className={`inline-block text-sm leading-relaxed max-w-full text-left ${
            isUser
              ? "bg-surface rounded-2xl rounded-tr-sm px-4 py-3"
              : ""
          }`}
        >
          <MarkdownRenderer content={message.content} />
        </div>

        {/* Table data */}
        {message.tableData && message.tableData.length > 0 && (
          <div className="mt-3 overflow-x-auto rounded-lg border border-border">
            <table className="msg-table">
              <thead>
                <tr>
                  {Object.keys(message.tableData[0]).map((key) => (
                    <th key={key}>{key}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {message.tableData.map((row, i) => (
                  <tr key={i}>
                    {Object.values(row).map((val, j) => (
                      <td key={j}>{val}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

/* ===========================
   Minimal Markdown Renderer
   =========================== */
function MarkdownRenderer({ content }: { content: string }) {
  const lines = content.split("\n");
  const elements: React.ReactNode[] = [];
  let tableBuffer: string[] = [];
  let inTable = false;

  lines.forEach((line, idx) => {
    const trimmed = line.trim();
    const isTableRow = trimmed.startsWith("|") && trimmed.endsWith("|");
    const isSeparator = /^\|[\s\-:|]+\|$/.test(trimmed);

    if (isTableRow || isSeparator) {
      inTable = true;
      tableBuffer.push(line);
    } else {
      if (inTable && tableBuffer.length > 0) {
        elements.push(<RenderTable key={`t-${idx}`} lines={tableBuffer} />);
        tableBuffer = [];
        inTable = false;
      }
      elements.push(
        <span key={idx}>
          <InlineText text={line} />
          {idx < lines.length - 1 && "\n"}
        </span>
      );
    }
  });

  if (tableBuffer.length > 0) {
    elements.push(<RenderTable key="t-last" lines={tableBuffer} />);
  }

  return <div className="whitespace-pre-wrap">{elements}</div>;
}

function InlineText({ text }: { text: string }) {
  if (text.trim().startsWith("> ")) {
    return (
      <span className="block border-l-2 border-muted pl-3 text-muted italic my-1">
        <InlineText text={text.trim().slice(2)} />
      </span>
    );
  }

  const parts: React.ReactNode[] = [];
  const regex = /(\*\*(.+?)\*\*)|(\*(.+?)\*)|(`(.+?)`)|(\[(.+?)\]\((.+?)\))/g;
  let lastIdx = 0;
  let match;
  let key = 0;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIdx) {
      parts.push(text.slice(lastIdx, match.index));
    }
    if (match[1]) {
      parts.push(<strong key={key++} className="font-semibold">{match[2]}</strong>);
    } else if (match[3]) {
      parts.push(<em key={key++} className="italic text-muted">{match[4]}</em>);
    } else if (match[5]) {
      parts.push(
        <code key={key++} className="px-1 py-0.5 rounded bg-surface text-sm font-mono">
          {match[6]}
        </code>
      );
    } else if (match[7]) {
      parts.push(
        <a key={key++} href={match[9]} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
          {match[8]}
        </a>
      );
    }
    lastIdx = match.index + match[0].length;
  }

  if (lastIdx < text.length) {
    parts.push(text.slice(lastIdx));
  }

  return <>{parts.length > 0 ? parts : text}</>;
}

function RenderTable({ lines }: { lines: string[] }) {
  const rows = lines
    .filter((l) => !/^\|[\s\-:|]+\|$/.test(l.trim()))
    .map((l) =>
      l.split("|").filter(Boolean).map((c) => c.trim())
    );

  if (rows.length === 0) return null;
  const header = rows[0];
  const body = rows.slice(1);

  return (
    <div className="my-3 overflow-x-auto rounded-lg border border-border">
      <table className="msg-table">
        <thead>
          <tr>
            {header.map((cell, i) => (
              <th key={i}>{cell}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {body.map((row, i) => (
            <tr key={i}>
              {row.map((cell, j) => (
                <td key={j}>{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
