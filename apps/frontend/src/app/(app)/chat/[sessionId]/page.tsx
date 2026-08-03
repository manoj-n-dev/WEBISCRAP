"use client";

import React, { useState } from "react";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { PipelineStrip, AgentStep } from "@/components/chat/PipelineStrip";
import { DataCard } from "@/components/chat/DataCard";
import { Composer } from "@/components/chat/Composer";
import { Button } from "@/components/ui/Button";
import { FileDown, RefreshCw } from "lucide-react";

export default function ChatPage() {
  const [input, setInput] = useState("");
  
  // Dummy data mirroring the reference HTML
  const mockData = [
    { title: "ASUS Vivobook 15", price: "₹52,990", rating: "4.2", processor: "Core i5" },
    { title: "HP Pavilion 14", price: "₹58,500", rating: "4.4", processor: "Ryzen 5" },
    { title: "Acer Swift 3", price: "₹54,999", rating: "4.3", processor: "Core i5" },
    { title: "Lenovo IdeaPad Slim 3", price: "₹51,490", rating: "4.1", processor: "Ryzen 5" },
    { title: "Dell Inspiron 3511", price: "₹55,200", rating: "4.0", processor: "Core i5" },
  ];

  return (
    <div className="flex flex-col h-full">
      {/* Scrollable messages container */}
      <div className="flex-1 overflow-y-auto p-[24px_24px_40px]">
        <div className="max-w-[760px] mx-auto flex flex-col gap-[32px]">
          
          <MessageBubble role="user" content="extract laptops over 50k from flipkart with their price, rating, and processor" />
          
          <MessageBubble role="ai" content={
            <div className="flex flex-col gap-[12px]">
              <div>I'll extract the laptops over ₹50k from Flipkart. Launching the pipeline...</div>
              
              <PipelineStrip 
                activeStep="extract"
                completedSteps={["plan", "analyze", "browse"]} 
                title="Extracting 42 products..."
              />
              
              <div className="mt-4">
                Extraction complete. I found 42 laptops matching your criteria.
              </div>
              
              <DataCard 
                rows={5} 
                cols={4} 
                totalRows={42} 
                data={mockData} 
                className="mt-4"
              />

              <div className="flex gap-[12px] mt-4">
                <Button>
                  <FileDown className="w-[16px] h-[16px]" />
                  Open in Dataset View
                </Button>
                <Button variant="ghost">
                  <RefreshCw className="w-[16px] h-[16px]" />
                  Re-run Extraction
                </Button>
              </div>
            </div>
          } />
          
        </div>
      </div>
      
      {/* Fixed Composer at bottom */}
      <Composer 
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onSubmit={() => {
          if (input.trim()) setInput("");
        }}
      />
    </div>
  );
}
