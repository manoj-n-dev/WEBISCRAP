"use client";

import React, { useState, useEffect } from "react";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { PipelineStrip } from "@/components/chat/PipelineStrip";
import { DataCard } from "@/components/chat/DataCard";
import { Composer } from "@/components/chat/Composer";
import { Button } from "@/components/ui/Button";
import { FileDown, RefreshCw } from "lucide-react";
import { useChatStore } from "@/lib/store/chat";
import { useRouter } from "next/navigation";

export default function ChatPage({ params }: { params: Promise<{ sessionId: string }> }) {
  const resolvedParams = React.use(params);
  const sessionId = resolvedParams.sessionId;

  const [input, setInput] = useState("");
  const router = useRouter();
  
  const { 
    messages, 
    submitExtraction, 
    isPipelineActive, 
    setActiveSession,
    activeSessionId 
  } = useChatStore();

  useEffect(() => {
    if (sessionId && sessionId !== "new") {
      setActiveSession(sessionId);
    }
  }, [sessionId, setActiveSession]);

  // If activeSessionId changed from "new" to a real ID after submission, redirect silently
  useEffect(() => {
    if (sessionId === "new" && activeSessionId && activeSessionId !== "new") {
      router.replace(`/chat/${activeSessionId}`);
    }
  }, [activeSessionId, sessionId, router]);

  const [activeStep, setActiveStep] = useState<string>("plan");
  const [completedSteps, setCompletedSteps] = useState<string[]>([]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isPipelineActive && activeSessionId && activeSessionId !== "new") {
      interval = setInterval(async () => {
        try {
          const { ApiClient } = await import("@/lib/api/client");
          const res = await ApiClient.getProgress(activeSessionId);
          if (res.step) {
             const STEPS = ["plan", "analyze", "browse", "extract", "clean", "validate"];
             const currentIndex = STEPS.indexOf(res.step);
             setActiveStep(res.step);
             if (currentIndex > 0) {
                setCompletedSteps(STEPS.slice(0, currentIndex));
             } else {
                setCompletedSteps([]);
             }
          }
        } catch(e) {}
      }, 1000);
    } else {
      setActiveStep("plan");
      setCompletedSteps([]);
    }
    return () => clearInterval(interval);
  }, [isPipelineActive, activeSessionId]);

  const handleSubmit = async () => {
    if (!input.trim() || isPipelineActive) return;
    
    const query = input;
    setInput("");
    
    // Extract URL if one is provided in the prompt (simple heuristic)
    const urlMatch = query.match(/https?:\/\/[^\s]+/);
    const url = urlMatch ? urlMatch[0] : "";
    
    await submitExtraction(query, url);
  };

  const handleRerun = async (index: number) => {
    if (isPipelineActive) return;
    let lastUserMsg = "Re-run the extraction";
    for (let i = index - 1; i >= 0; i--) {
      if (messages[i].role === "user") {
        lastUserMsg = String(messages[i].content);
        break;
      }
    }
    const urlMatch = lastUserMsg.match(/https?:\/\/[^\s]+/);
    const url = urlMatch ? urlMatch[0] : "";
    await submitExtraction(lastUserMsg, url);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-[24px_24px_40px]">
        <div className="max-w-[760px] mx-auto flex flex-col gap-[32px]">
          
          {messages.length === 0 && (
            <div className="text-center mt-20 text-text-dim">
              <h2 className="text-xl text-text-hi mb-2">What would you like to extract?</h2>
              <p>Paste a URL and describe the data you need.</p>
            </div>
          )}

          {messages.map((msg, index) => (
            <MessageBubble key={msg.id} role={msg.role} content={
              msg.role === "user" ? msg.content : (
                <div className="flex flex-col gap-[12px]">
                  <div>{msg.content}</div>
                  
                  {msg.status === "running" && (
                    <PipelineStrip 
                      activeStep={activeStep as any}
                      completedSteps={completedSteps as any} 
                      title="Processing Pipeline..."
                    />
                  )}
                  
                  {msg.status === "completed" && msg.data && msg.data.length > 0 && (
                    <DataCard 
                      rows={Math.min(5, msg.data.length)} 
                      cols={Object.keys(msg.data[0] || {}).length} 
                      totalRows={msg.totalRows || msg.data.length} 
                      data={msg.data} 
                      className="mt-4"
                    />
                  )}

                  {msg.status === "completed" && msg.confidenceScore !== undefined && (
                    <div className="mt-4 p-4 rounded-lg bg-bg-base border border-border-dim">
                      <div className="flex items-center gap-2 mb-2">
                        <div className="text-sm font-medium text-text-hi">Validation Confidence</div>
                        <div className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                          msg.confidenceScore >= 80 ? 'bg-green-500/10 text-green-500' :
                          msg.confidenceScore >= 50 ? 'bg-yellow-500/10 text-yellow-500' :
                          'bg-red-500/10 text-red-500'
                        }`}>
                          {msg.confidenceScore}%
                        </div>
                      </div>
                      {msg.validationNotes && (
                        <div className="text-sm text-text-dim mt-2">
                          {msg.validationNotes}
                        </div>
                      )}
                    </div>
                  )}

                  {msg.status === "completed" && (
                    <div className="flex gap-[12px] mt-4 flex-wrap">
                      <Button onClick={() => router.push(`/dataset/${activeSessionId}`)}>
                        <FileDown className="w-[16px] h-[16px]" />
                        Open in Dataset View
                      </Button>
                      
                      {msg.exportUrl && (
                        <Button 
                          variant="default" 
                          onClick={() => {
                            const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
                            const token = localStorage.getItem("token");
                            
                            // Download using fetch to send auth header
                            fetch(`${baseUrl}${msg.exportUrl}`, {
                              headers: { "Authorization": `Bearer ${token}` }
                            })
                            .then(res => res.blob())
                            .then(blob => {
                              const url = window.URL.createObjectURL(blob);
                              const a = document.createElement('a');
                              a.href = url;
                              a.download = msg.exportUrl!.split('/').pop() || "export";
                              document.body.appendChild(a);
                              a.click();
                              a.remove();
                            });
                          }}
                        >
                          <FileDown className="w-[16px] h-[16px]" />
                          Download Export
                        </Button>
                      )}
                      
                      <Button variant="ghost" onClick={() => handleRerun(index)}>
                        <RefreshCw className="w-[16px] h-[16px]" />
                        Re-run Extraction
                      </Button>
                    </div>
                  )}
                </div>
              )
            } />
          ))}
          
        </div>
      </div>
      
      <Composer 
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onSubmit={handleSubmit}
      />
    </div>
  );
}
