import { create } from "zustand";

interface Message {
  id: string;
  role: "user" | "ai";
  content: string;
  data?: any[];
  status?: "running" | "completed" | "error";
  completedSteps?: string[];
}

interface ChatState {
  activeSessionId: string | null;
  sessions: any[];
  messages: Message[];
  setActiveSession: (id: string) => void;
  addMessage: (msg: Message) => void;
  updateMessage: (id: string, updates: Partial<Message>) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  activeSessionId: null,
  sessions: [],
  messages: [],
  setActiveSession: (id) => set({ activeSessionId: id }),
  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  updateMessage: (id, updates) =>
    set((state) => ({
      messages: state.messages.map((m) => (m.id === id ? { ...m, ...updates } : m)),
    })),
}));
