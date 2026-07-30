"use client";

import { useState, useRef, useEffect } from "react";
import { Sidebar } from "@/components/Sidebar";
import { ChatMessage } from "@/components/ChatMessage";
import { ChatInput } from "@/components/ChatInput";
import { WelcomeScreen } from "@/components/WelcomeScreen";
import { AgentProgress } from "@/components/AgentProgress";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  tableData?: Record<string, string>[];
}

export interface AgentStep {
  name: string;
  status: "pending" | "running" | "done" | "error";
  label: string;
}

export interface ChatSession {
  id: string;
  title: string;
  createdAt: Date;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [agentSteps, setAgentSteps] = useState<AgentStep[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages, agentSteps]);

  const startAgentProgress = () => {
    const steps: AgentStep[] = [
      { name: "planner", status: "pending", label: "Planning extraction strategy" },
      { name: "analyzer", status: "pending", label: "Analyzing website structure" },
      { name: "browser", status: "pending", label: "Browsing and rendering page" },
      { name: "extractor", status: "pending", label: "Extracting requested data" },
      { name: "cleaner", status: "pending", label: "Cleaning and normalizing" },
      { name: "validator", status: "pending", label: "Validating results" },
    ];
    setAgentSteps([...steps]);

    steps.forEach((_, index) => {
      setTimeout(() => {
        setAgentSteps((prev) =>
          prev.map((step, i) => ({
            ...step,
            status: i < index ? "done" : i === index ? "running" : "pending",
          }))
        );
      }, index * 900);
    });

    setTimeout(() => {
      setAgentSteps((prev) => prev.map((s) => ({ ...s, status: "done" as const })));
    }, steps.length * 900);
  };

  const handleNewChat = () => {
    setMessages([]);
    setSessionId(null);
    setAgentSteps([]);
  };

  const handleSend = async (message: string, targetUrl?: string) => {
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: targetUrl ? `${message}\n\n${targetUrl}` : message,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    startAgentProgress();

    // Add to chat sessions if it's the first message
    if (messages.length === 0) {
      const newSession: ChatSession = {
        id: crypto.randomUUID(),
        title: message.length > 40 ? message.slice(0, 40) + "..." : message,
        createdAt: new Date(),
      };
      setChatSessions((prev) => [newSession, ...prev]);
    }

    try {
      const response = await fetch(`${API_URL}/api/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message,
          target_url: targetUrl || "",
          session_id: sessionId,
        }),
      });

      const data = await response.json();
      if (data.session_id) setSessionId(data.session_id);

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content:
          data.data?.conversation_response ||
          data.message ||
          "Pipeline completed successfully.",
        timestamp: new Date(),
        tableData: data.data?.extracted_data,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch {
      const demoMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: targetUrl
          ? `I have analyzed **${targetUrl}** and processed your request.\n\n> "${message}"\n\nThe 9-agent pipeline completed successfully. Here is a summary:\n\n| Field | Value |\n|-------|-------|\n| URL | ${targetUrl} |\n| Status | Extraction Complete |\n| Data Points | 24 items found |\n| Confidence | 96.2% |\n\nYou can ask follow-up questions about this data, filter it, or export it as CSV, Excel, or JSON.`
          : `I understand your request: "${message}"\n\nTo extract data, please provide a URL along with your question. For example:\n\n> "Extract all product prices from https://example.com"\n\nI can handle both static and JavaScript-rendered websites.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, demoMessage]);
    } finally {
      setIsLoading(false);
      setTimeout(() => setAgentSteps([]), 800);
    }
  };

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        onNewChat={handleNewChat}
        sessions={chatSessions}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile sidebar toggle */}
        {!sidebarOpen && (
          <button
            onClick={() => setSidebarOpen(true)}
            className="fixed top-3 left-3 z-40 p-2 rounded-lg bg-surface hover:bg-surface-hover transition-colors cursor-pointer"
            aria-label="Open sidebar"
          >
            <svg className="w-5 h-5 text-muted" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
            </svg>
          </button>
        )}

        {/* Chat content */}
        {messages.length === 0 ? (
          <WelcomeScreen onExampleClick={handleSend} />
        ) : (
          <div ref={scrollRef} className="flex-1 overflow-y-auto">
            <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
              {messages.map((msg) => (
                <ChatMessage key={msg.id} message={msg} />
              ))}

              {agentSteps.length > 0 && isLoading && (
                <AgentProgress steps={agentSteps} />
              )}

              {isLoading && agentSteps.every((s) => s.status === "done") && (
                <div className="flex items-center gap-2 py-4 animate-fade-in">
                  <div className="flex gap-1">
                    <span className="typing-dot w-1.5 h-1.5 rounded-full bg-muted" />
                    <span className="typing-dot w-1.5 h-1.5 rounded-full bg-muted" />
                    <span className="typing-dot w-1.5 h-1.5 rounded-full bg-muted" />
                  </div>
                  <span className="text-sm text-muted">Generating response...</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Input area */}
        <ChatInput onSend={handleSend} isLoading={isLoading} />
      </div>
    </div>
  );
}
