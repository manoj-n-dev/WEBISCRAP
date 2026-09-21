"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { FileDown, RefreshCw, AlertTriangle, Download } from "lucide-react";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { PipelineStrip, type AgentStep } from "@/components/chat/PipelineStrip";
import { DataCard } from "@/components/chat/DataCard";
import { Composer } from "@/components/chat/Composer";
import { AttachmentChip } from "@/components/chat/AttachmentChip";
import { LimitReached } from "@/components/chat/LimitReached";
import { ThinkingDots } from "@/components/chat/ThinkingDots";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useChatStore, type Message } from "@/lib/store/chat";
import { ApiClient } from "@/lib/api/client";
import { exportSession, type ExportFormat } from "@/lib/export";

const STEPS: AgentStep[] = ["plan", "analyze", "browse", "extract", "clean", "validate"];

function extractUrl(text: string): string {
  const m = text.match(/https?:\/\/[^\s]+/);
  return m ? m[0].replace(/[.,;:!?)\]}]+$/, "") : "";
}

/* ── Message list: memoised so typing in the composer does NOT re-render every table/card on each keystroke ─────────── */
interface ListProps {
  messages: Message[];
  sessionId?: string;
  activeStep: AgentStep;
  doneSteps: AgentStep[];
  onRetry: (index: number) => void;
}

const MessageList = React.memo(function MessageList({ messages, sessionId, activeStep, doneSteps, onRetry }: ListProps) {
  const router = useRouter();

  const renderAi = (msg: Message, index: number) => {
    if (msg.status === "running") {
      return msg.mode === "followup" ? (
        <ThinkingDots label="Analyzing your data" />
      ) : (
        <div className="flex flex-col gap-[8px]">
          <div className="text-[14.5px] leading-[1.65] text-text-hi">{msg.content}</div>
          <PipelineStrip activeStep={activeStep} completedSteps={doneSteps} title="Processing pipeline" />
        </div>
      );
    }

    if (msg.status === "error" && msg.error) {
      if (msg.error.code === "LLM_RATE_LIMIT") {
        return <LimitReached retryAfter={msg.error.retryAfter} scope={msg.error.scope} onRetry={() => onRetry(index)} />;
      }
      return (
        <Card variant="strong" className="p-[16px]" role="alert">
          <div className="flex items-start gap-[12px]">
            <AlertTriangle className="w-[18px] h-[18px] text-red-400 shrink-0 mt-[2px]" />
            <div className="min-w-0">
              <div className="text-[14px] text-text-hi">{msg.error.message}</div>
              <Button variant="ghost" className="mt-[10px] text-[13px] py-[8px]" onClick={() => onRetry(index)}>
                <RefreshCw className="w-[14px] h-[14px]" />
                Try again
              </Button>
            </div>
          </div>
        </Card>
      );
    }

    const exportFmt = msg.exportUrl?.match(/\/api\/export\/(\w+)/)?.[1];
    const isExtraction = msg.mode === "extraction";
    return (
      <div className="flex flex-col gap-[12px]">
        <div className="text-[14.5px] leading-[1.65] text-text-hi whitespace-pre-wrap break-words">{msg.content}</div>

        {msg.warnings?.map((w, i) => (
          <div key={i} className="text-[12.5px] text-warn flex gap-[8px]"><AlertTriangle className="w-[14px] h-[14px] shrink-0 mt-[2px]" />{w}</div>
        ))}

        {isExtraction && msg.data && msg.data.length > 0 && (
          <DataCard data={msg.data} totalRows={msg.totalRows} sessionId={sessionId} className="mt-[4px]" />
        )}

        {!isExtraction && msg.resultRows && msg.resultRows.length > 0 && (
          <DataCard data={msg.resultRows} totalRows={msg.resultCount ?? msg.resultRows.length} label="Matching rows" previewRows={10} showExports={false} sessionId={sessionId} className="mt-[4px]" />
        )}

        {isExtraction && msg.confidenceScore !== undefined && (
          <div className="p-[14px] rounded-lg bg-white/2 border border-hair">
            <div className="flex items-center gap-2 mb-1">
              <div className="text-sm font-medium text-text-hi">Data quality</div>
              <div className={`px-2 py-0.5 rounded-full text-xs font-semibold ${msg.confidenceScore >= 80 ? "bg-green-500/10 text-green-500" : msg.confidenceScore >= 50 ? "bg-yellow-500/10 text-yellow-500" : "bg-red-500/10 text-red-500"}`}>
                {Math.round(msg.confidenceScore)}%
              </div>
            </div>
            {msg.validationNotes && <div className="text-[13px] text-text-dim">{msg.validationNotes}</div>}
          </div>
        )}

        {msg.status === "completed" && (isExtraction || exportFmt) && sessionId && (
          <div className="flex gap-[10px] flex-wrap">
            {isExtraction && msg.data && msg.data.length > 0 && (
              <Button onClick={() => router.push(`/dataset/${sessionId}`)} className="text-[13px] py-[9px]">
                <FileDown className="w-[15px] h-[15px]" />
                Open dataset
              </Button>
            )}
            {exportFmt && (
              <Button variant="primary" className="text-[13px] py-[9px]" onClick={() => void exportSession((exportFmt === "markdown" ? "md" : exportFmt) as ExportFormat, sessionId)}>
                <Download className="w-[15px] h-[15px]" />
                Download {exportFmt === "excel" ? "Excel" : exportFmt.toUpperCase()}
              </Button>
            )}
            {isExtraction && msg.data && msg.data.length > 0 && (
              <Button variant="ghost" className="text-[13px] py-[9px]" onClick={() => onRetry(index)}>
                <RefreshCw className="w-[15px] h-[15px]" />
                Re-run
              </Button>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <>
      {messages.map((msg, index) => (
        <MessageBubble
          key={msg.id}
          role={msg.role}
          content={
            msg.role === "user" ? (
              <div className="flex flex-col gap-[10px]">
                {msg.content && <div className="text-[14.5px] leading-[1.65] text-text-hi whitespace-pre-wrap break-words">{msg.content}</div>}
                {msg.attachments && msg.attachments.length > 0 && (
                  <div className="flex flex-wrap gap-[8px]">
                    {msg.attachments.map((a) => <AttachmentChip key={a.id} attachment={a} />)}
                  </div>
                )}
              </div>
            ) : renderAi(msg, index)
          }
        />
      ))}
    </>
  );
});

export default function ChatView({ routeId }: { routeId: string }) {
  const router = useRouter();
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  // Narrow selectors: this component only re-renders for the slices it actually shows.
  const messages = useChatStore((s) => s.messages);
  const isPipelineActive = useChatStore((s) => s.isPipelineActive);
  const activeSessionId = useChatStore((s) => s.activeSessionId);
  const pendingAttachments = useChatStore((s) => s.pendingAttachments);
  const submitExtraction = useChatStore((s) => s.submitExtraction);
  const setActiveSession = useChatStore((s) => s.setActiveSession);
  const startNewChat = useChatStore((s) => s.startNewChat);
  const addAttachments = useChatStore((s) => s.addAttachments);
  const removeAttachment = useChatStore((s) => s.removeAttachment);

  // Route -> store. "/chat/new" starts a blank chat (unless a run is in flight); a real id loads that chat.
  useEffect(() => {
    if (routeId === "new") {
      if (!useChatStore.getState().isPipelineActive) startNewChat();
    } else {
      setActiveSession(routeId);
    }
  }, [routeId, setActiveSession, startNewChat]);

  // After the FIRST answer of a brand-new chat, move the URL to the real session id (store guard prevents a reload).
  useEffect(() => {
    if (routeId === "new" && activeSessionId && !isPipelineActive && messages.length > 0) {
      router.replace(`/chat/${activeSessionId}`);
    }
  }, [routeId, activeSessionId, isPipelineActive, messages.length, router]);

  // ── Live pipeline progress (extraction runs only). Works from the very first message: the session id is client-generated.
  const running = messages.find((m) => m.status === "running");
  const pollProgress = running?.mode === "extraction" && isPipelineActive && !!activeSessionId;
  const [activeStep, setActiveStep] = useState<AgentStep>("plan");
  const [doneSteps, setDoneSteps] = useState<AgentStep[]>([]);

  useEffect(() => {
    if (!pollProgress || !activeSessionId) {
      setActiveStep("plan");
      setDoneSteps([]);
      return;
    }
    let stop = false;
    let delay = 1500;
    const tick = async () => {
      if (stop) return;
      try {
        const res = await ApiClient.getProgress(activeSessionId);
        delay = 1500;
        if (res?.step && !stop) {
          const idx = STEPS.indexOf(res.step as AgentStep);
          if (idx >= 0) {
            setActiveStep(STEPS[idx]);
            setDoneSteps(STEPS.slice(0, idx));
          }
        }
      } catch (e) {
        // 403 = the very first POST has not claimed the new session yet: just poll again shortly.
        delay = (e as { status?: number })?.status === 403 ? 700 : Math.min(delay * 2, 8000);   // back off on 429 / network errors
      }
      if (!stop) setTimeout(tick, delay);
    };
    const t = setTimeout(tick, 400);
    return () => {
      stop = true;
      clearTimeout(t);
    };
  }, [pollProgress, activeSessionId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages.length, isPipelineActive]);

  const handleSubmit = useCallback(async () => {
    const hasReady = pendingAttachments.some((a) => a.status === "ready");
    if ((!input.trim() && !hasReady) || isPipelineActive) return;
    const query = input;
    setInput("");
    await submitExtraction(query, extractUrl(query));
  }, [input, isPipelineActive, pendingAttachments, submitExtraction]);

  // Stable identity (reads the store directly) so MessageList's memo is not defeated by every render.
  const handleRetry = useCallback(async (index: number) => {
    const state = useChatStore.getState();
    if (state.isPipelineActive) return;
    let text = "";
    for (let i = index - 1; i >= 0; i--) {
      if (state.messages[i].role === "user") { text = String(state.messages[i].content); break; }
    }
    text = text || "Re-run the extraction";
    await state.submitExtraction(text, extractUrl(text));
  }, []);

  return (
    <div className="flex flex-col h-full min-h-0">
      <div className="flex-1 overflow-y-auto p-[16px_12px_24px] sm:p-[24px_24px_40px]">
        <div className="max-w-[760px] mx-auto flex flex-col gap-[24px] sm:gap-[32px]">
          {messages.length === 0 && (
            <div className="text-center mt-12 sm:mt-20 text-text-dim px-2">
              <h2 className="text-lg sm:text-xl text-text-hi mb-2">What would you like to extract?</h2>
              <p className="text-[14px]">Paste a URL, or attach a CSV, Excel, PDF, Word file or image — then describe the data you need.</p>
            </div>
          )}

          <MessageList messages={messages} sessionId={activeSessionId ?? undefined} activeStep={activeStep} doneSteps={doneSteps} onRetry={handleRetry} />
          <div ref={bottomRef} />
        </div>
      </div>

      <Composer
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onSubmit={handleSubmit}
        isLoading={isPipelineActive}
        attachments={pendingAttachments}
        onAttach={addAttachments}
        onRemoveAttachment={removeAttachment}
      />
    </div>
  );
}
