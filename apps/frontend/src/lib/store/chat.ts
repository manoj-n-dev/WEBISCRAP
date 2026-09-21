import { create } from "zustand";
import { ApiClient, ApiError } from "../api/client";
import { playInterfaceSound } from "../useSound";

export type ChatMode = "extraction" | "followup" | "idle";

export interface Attachment {
  id: string;
  name: string;
  size: number;
  status: "uploading" | "ready" | "error";
  kind?: string;
  rows?: number | null;
  error?: string;
}

export interface MessageError {
  code?: string;
  message: string;
  retryAfter?: number;
  scope?: string;
}

export interface Message {
  id: string;
  role: "user" | "ai";
  content: string;
  status?: "running" | "completed" | "error";
  mode?: ChatMode;
  attachments?: Attachment[];
  data?: any[];
  resultRows?: any[] | null;
  resultCount?: number | null;
  completedSteps?: string[];
  totalRows?: number;
  totalCols?: number;
  confidenceScore?: number;
  validationNotes?: string;
  flaggedFields?: number;
  exportUrl?: string;
  warnings?: string[];
  error?: MessageError;
}

export interface SessionSummary {
  id: string;
  title: string;
  timestamp: number;
}

interface ChatState {
  userId: string | null;
  activeSessionId: string | null;
  sessions: SessionSummary[];
  sessionsLoaded: boolean;
  messages: Message[];
  pendingAttachments: Attachment[];
  isPipelineActive: boolean;
  error: string | null;

  bindUser: (userId: string) => void;
  resetAll: () => void;
  startNewChat: () => void;
  setActiveSession: (id: string) => void;
  fetchSessionHistory: (id: string) => Promise<void>;
  loadSessions: () => Promise<void>;
  removeSession: (id: string) => Promise<void>;
  renameSession: (id: string, newTitle: string) => Promise<void>;
  addAttachments: (files: File[]) => Promise<void>;
  removeAttachment: (id: string) => void;
  addMessage: (msg: Message) => void;
  updateMessage: (id: string, updates: Partial<Message>) => void;
  submitExtraction: (message: string, url: string) => Promise<void>;
}

const MAX_UPLOAD_BYTES = 20 * 1024 * 1024;
const ACCEPTED = [".pdf", ".docx", ".csv", ".xlsx", ".xls", ".png", ".jpg", ".jpeg"];

const initial = {
  activeSessionId: null as string | null,
  sessions: [] as SessionSummary[],
  sessionsLoaded: false,
  messages: [] as Message[],
  pendingAttachments: [] as Attachment[],
  isPipelineActive: false,
  error: null as string | null,
};

/** A dataset exists in this chat if any earlier AI message carried rows. */
export function chatHasDataset(messages: Message[]): boolean {
  return messages.some((m) => m.role === "ai" && ((m.totalRows ?? 0) > 0 || (m.data?.length ?? 0) > 0));
}

export const useChatStore = create<ChatState>((set, get) => ({
  userId: null,
  ...initial,

  /** Called after /me: if the signed-in identity changed, drop everything that belonged to the previous one. */
  bindUser: (userId) => {
    const current = get().userId;
    // The sessions list is always fetched with the CURRENT token, so it is already scoped to this identity and is kept
    // (getMe and loadSessions now run in parallel). Everything else that belonged to the previous identity is dropped.
    if (current && current !== userId) set({ ...initial, sessions: get().sessions, sessionsLoaded: get().sessionsLoaded, userId });
    else set({ userId });
  },

  /** Logout / account switch: nothing from the previous identity may stay in memory. */
  resetAll: () => set({ userId: null, ...initial }),

  startNewChat: () => set({ activeSessionId: null, messages: [], pendingAttachments: [], error: null }),

  setActiveSession: (id) => {
    const { activeSessionId, messages } = get();
    if (activeSessionId === id && messages.length > 0) return;   // already loaded (or just created here): never clobber it
    set({ activeSessionId: id, messages: [], pendingAttachments: [], error: null });
    void get().fetchSessionHistory(id);
  },

  fetchSessionHistory: async (id) => {
    try {
      const [historyRes, dataRes] = await Promise.allSettled([ApiClient.getHistory(id), ApiClient.getSessionData(id, 200)]);
      if (get().activeSessionId !== id) return;                  // user navigated away meanwhile
      if (historyRes.status !== "fulfilled") throw historyRes.reason;

      const history: Message[] = (historyRes.value.history || []).map((item: any, i: number) =>
        item.role === "user"
          ? { id: `hist-${i}`, role: "user" as const, content: String(item.content ?? "") }
          : { id: `hist-${i}`, role: "ai" as const, content: String(item.content ?? ""), status: "completed" as const, mode: "followup" as const },
      );

      // Re-attach the dataset (preview) + quality info to the most recent AI answer so the table is not lost on reload
      if (dataRes.status === "fulfilled" && dataRes.value?.cleaned_data?.length) {
        const d = dataRes.value;
        const lastAi = [...history].reverse().find((m) => m.role === "ai");
        const patch: Partial<Message> = {
          mode: "extraction",
          data: d.cleaned_data,
          totalRows: d.total_rows ?? d.cleaned_data.length,
          totalCols: Object.keys(d.cleaned_data[0] || {}).length,
          confidenceScore: d.validation?.confidence_score,
          validationNotes: d.validation?.validation_notes,
          flaggedFields: d.validation?.flagged_rows_count || 0,
        };
        if (lastAi) Object.assign(lastAi, patch);
      }
      set({ messages: history, error: null });
    } catch (err) {
      console.error("Failed to fetch session history:", err);
      set({ error: "Failed to load this chat" });
    }
  },

  loadSessions: async () => {
    try {
      const res = await ApiClient.getSessions();
      set({ sessions: (res.sessions || []) as SessionSummary[], sessionsLoaded: true });
    } catch {
      set({ sessionsLoaded: true });
    }
  },

  removeSession: async (id) => {
    await ApiClient.deleteSession(id);
    set((s) => ({ sessions: s.sessions.filter((x) => x.id !== id) }));
    if (get().activeSessionId === id) get().startNewChat();
  },

  renameSession: async (id, newTitle) => {
    const trimmed = newTitle.trim();
    if (!trimmed) return;
    await ApiClient.renameSession(id, trimmed);
    set((s) => ({
      sessions: s.sessions.map((x) => (x.id === id ? { ...x, title: trimmed } : x)),
    }));
  },

  /** Files become real attachments (chips) uploaded to the chat's session - they are NOT pasted into the text box. */
  addAttachments: async (files) => {
    let sid = get().activeSessionId;
    if (!sid) {
      sid = crypto.randomUUID();
      set({ activeSessionId: sid });
    }
    if (files.length > 0) {
      playInterfaceSound("upload");
    }
    for (const file of files) {
      const id = crypto.randomUUID();
      const ext = "." + (file.name.split(".").pop() || "").toLowerCase();
      const base: Attachment = { id, name: file.name, size: file.size, status: "uploading" };
      if (!ACCEPTED.includes(ext)) {
        set((s) => ({ pendingAttachments: [...s.pendingAttachments, { ...base, status: "error", error: "Unsupported file type" }] }));
        playInterfaceSound("error");
        continue;
      }
      if (file.size > MAX_UPLOAD_BYTES) {
        set((s) => ({ pendingAttachments: [...s.pendingAttachments, { ...base, status: "error", error: "File is larger than 20 MB" }] }));
        playInterfaceSound("error");
        continue;
      }
      set((s) => ({ pendingAttachments: [...s.pendingAttachments, base] }));
      try {
        const res = await ApiClient.uploadFile(file, sid);
        set((s) => ({
          pendingAttachments: s.pendingAttachments.map((a) => (a.id === id ? { ...a, status: "ready", kind: res.kind, rows: res.rows } : a)),
        }));
        playInterfaceSound("upload_done");
      } catch (e) {
        const msg = e instanceof ApiError ? e.message : "Upload failed";
        set((s) => ({ pendingAttachments: s.pendingAttachments.map((a) => (a.id === id ? { ...a, status: "error", error: msg } : a)) }));
        playInterfaceSound("error");
      }
    }
  },

  removeAttachment: (id) => set((s) => ({ pendingAttachments: s.pendingAttachments.filter((a) => a.id !== id) })),

  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  updateMessage: (id, updates) =>
    set((state) => ({ messages: state.messages.map((m) => (m.id === id ? { ...m, ...updates } : m)) })),

  submitExtraction: async (message, url) => {
    const { addMessage, updateMessage, messages } = get();
    const attachments = get().pendingAttachments.filter((a) => a.status === "ready");
    const hasDataset = chatHasDataset(messages);
    const isFollowUp = hasDataset && !url && attachments.length === 0;

    // The session id is created HERE, before the request, so live progress can be polled from the very first run.
    let sid = get().activeSessionId;
    if (!sid) sid = crypto.randomUUID();

    const text = message.trim() || (attachments.length ? `Extract the data from ${attachments.map((a) => a.name).join(", ")}` : "");
    addMessage({ id: crypto.randomUUID(), role: "user", content: text, attachments });
    const aiMsgId = crypto.randomUUID();
    addMessage({
      id: aiMsgId,
      role: "ai",
      content: isFollowUp ? "" : url ? `Extracting data from ${url}…` : attachments.length ? "Reading your file…" : "Working on it…",
      status: "running",
      mode: isFollowUp ? "followup" : "extraction",
      completedSteps: [],
    });
    set({ activeSessionId: sid, pendingAttachments: [], isPipelineActive: true, error: null });
    playInterfaceSound("extraction_start");

    try {
      const result = await ApiClient.submitExtraction(text, url, sid);
      if (result.status === "error") throw new ApiError(result.message || "Something went wrong.", 500, { code: result.code });

      const p = result.data || {};
      const rows: any[] = Array.isArray(p.cleaned_data) ? p.cleaned_data : [];
      const validation = p.validation || {};
      const ranExtraction = p.mode === "extraction" && !p.extraction_empty;

      updateMessage(aiMsgId, {
        status: "completed",
        mode: p.mode,
        content: p.conversation_response?.response_text || "Done.",
        completedSteps: p.completed_steps || [],
        data: ranExtraction ? rows : undefined,
        resultRows: p.result_rows ?? null,
        resultCount: p.conversation_response?.result_count ?? null,
        totalRows: p.dataset_rows ?? rows.length,
        totalCols: p.dataset_cols,
        confidenceScore: ranExtraction ? validation.confidence_score : undefined,
        validationNotes: ranExtraction ? validation.validation_notes : undefined,
        flaggedFields: validation.flagged_rows_count || 0,
        exportUrl: p.export_url,
        warnings: p.warnings,
      });
      playInterfaceSound("extraction_done");
      void get().loadSessions();
    } catch (err) {
      const e = err as ApiError;
      updateMessage(aiMsgId, {
        status: "error",
        content: "",
        error: { code: e.code, message: e.message || "Something went wrong.", retryAfter: e.retryAfter, scope: e.scope },
      });
      set({ error: e.message });
      playInterfaceSound("error");
    } finally {
      set({ isPipelineActive: false });
    }
  },
}));
