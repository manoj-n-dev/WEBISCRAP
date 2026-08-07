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

export default function ChatPage({ params }: { params: { sessionId: string } }) {
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
    if (params.sessionId && params.sessionId !== "new") {
      setActiveSession(params.sessionId);
    }
  }, [params.sessionId, setActiveSession]);

  // If activeSessionId changed from "new" to a real ID after submission, redirect silently
  useEffect(() => {
    if (params.sessionId === "new" && activeSessionId && activeSessionId !== "new") {
      router.replace(`/chat/${activeSessionId}`);
    }
  }, [activeSessionId, params.sessionId, router]);

  const handleSubmit = async () => {
    if (!input.trim() || isPipelineActive) return;
    
    const query = input;
    setInput("");
    
    // Extract URL if one is provided in the prompt (simple heuristic)
    const urlMatch = query.match(/https?:\/\/[^\s]+/);
    const url = urlMatch ? urlMatch[0] : "";
    
    await submitExtraction(query, url);
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

          {messages.map((msg) => (
            <MessageBubble key={msg.id} role={msg.role} content={
              msg.role === "user" ? msg.content : (
                <div className="flex flex-col gap-[12px]">
                  <div>{msg.content}</div>
                  
                  {msg.status === "running" && (
                    <PipelineStrip 
                      activeStep="plan"
                      completedSteps={(msg.completedSteps as any) || []} 
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

                  {msg.status === "completed" && (
                    <div className="flex gap-[12px] mt-4">
                      <Button onClick={() => router.push(`/dataset/${activeSessionId}`)}>
                        <FileDown className="w-[16px] h-[16px]" />
                        Open in Dataset View
                      </Button>
                      <Button variant="ghost">
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
