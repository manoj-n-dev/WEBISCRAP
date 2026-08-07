import { create } from "zustand";
import { ApiClient } from "../api/client";

export interface Message {
  id: string;
  role: "user" | "ai";
  content: string | React.ReactNode;
  data?: any[];
  status?: "running" | "completed" | "error";
  completedSteps?: string[];
  totalRows?: number;
}

interface ChatState {
  activeSessionId: string | null;
  sessions: any[];
  messages: Message[];
  isPipelineActive: boolean;
  error: string | null;
  
  setActiveSession: (id: string) => void;
  addMessage: (msg: Message) => void;
  updateMessage: (id: string, updates: Partial<Message>) => void;
  submitExtraction: (message: string, url: string) => Promise<void>;
}

export const useChatStore = create<ChatState>((set, get) => ({
  activeSessionId: null,
  sessions: [],
  messages: [],
  isPipelineActive: false,
  error: null,
  
  setActiveSession: (id) => set({ activeSessionId: id }),
  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  updateMessage: (id, updates) =>
    set((state) => ({
      messages: state.messages.map((m) => (m.id === id ? { ...m, ...updates } : m)),
    })),
    
  submitExtraction: async (message: string, url: string) => {
    const { addMessage, updateMessage, activeSessionId } = get();
    
    // Add user message
    const userMsgId = Date.now().toString();
    addMessage({ id: userMsgId, role: "user", content: message });
    
    // Add AI placeholder message
    const aiMsgId = (Date.now() + 1).toString();
    addMessage({ 
      id: aiMsgId, 
      role: "ai", 
      content: `I'll extract the data from ${url || 'the requested site'}. Launching the pipeline...`,
      status: "running",
      completedSteps: []
    });
    
    set({ isPipelineActive: true, error: null });
    
    try {
      const result = await ApiClient.submitExtraction(message, url, activeSessionId || undefined);
      
      // Update session if it's new
      if (result.session_id && result.session_id !== activeSessionId) {
        set({ activeSessionId: result.session_id });
      }
      
      // The backend returns { result: [...] } or { status: "success", data: [...] }
      // We assume it's in result.data or result.result
      const extractionData = result.data || result.result || [];
      
      updateMessage(aiMsgId, {
        status: "completed",
        completedSteps: ["plan", "analyze", "browse", "extract", "clean", "validate"],
        data: Array.isArray(extractionData) ? extractionData : [extractionData],
        content: `Extraction complete. I found ${Array.isArray(extractionData) ? extractionData.length : 1} items matching your criteria.`,
        totalRows: Array.isArray(extractionData) ? extractionData.length : 1,
      });
      
    } catch (err: any) {
      updateMessage(aiMsgId, {
        status: "error",
        content: `Failed to complete extraction: ${err.message}`
      });
      set({ error: err.message });
    } finally {
      set({ isPipelineActive: false });
    }
  }
}));
