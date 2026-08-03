import { create } from "zustand";

interface ChatState {
  activeSessionId: string | null;
  sessions: any[];
  messages: any[];
  setActiveSession: (id: string) => void;
  addMessage: (msg: any) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  activeSessionId: null,
  sessions: [],
  messages: [],
  setActiveSession: (id) => set({ activeSessionId: id }),
  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
}));
