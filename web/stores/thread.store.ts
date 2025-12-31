import { create } from "zustand";
import type { ChatMessage } from "@/types/chat";
import { isApiError, type ApiMessagesListDto } from "@/types/api";
import { GET, POST_STREAM } from "@/lib/api";
import { useAuthStore } from "@/stores/auth.store";

const uid = () =>
  crypto?.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`;

let currentAbort: AbortController | null = null;
let loadSeq = 0;

type PendingFirstMessage = { chatId: string; query: string } | null;

async function withRefreshRetry<T>(fn: () => Promise<T>): Promise<T> {
  try {
    return await fn();
  } catch (e) {
    if (isApiError(e) && e.status === 401) {
      await useAuthStore.getState().refresh();
      return await fn();
    }
    throw e;
  }
}

async function* streamWithRefreshRetry<T>(
  makeStream: () => AsyncGenerator<T>
): AsyncGenerator<T> {
  try {
    yield* makeStream();
  } catch (e) {
    if (isApiError(e) && e.status === 401) {
      await useAuthStore.getState().refresh();
      yield* makeStream();
      return;
    }
    throw e;
  }
}

interface ThreadState {
  activeChatId: string | null;
  messages: ChatMessage[];
  isStreaming: boolean;
  pending: PendingFirstMessage;

  setPending: (chatId: string, query: string) => void;
  consumePending: (chatId: string) => string | null;

  clearThread: () => void;
  cancelStream: () => void;

  loadMessages: (chatId: string) => Promise<void>;
  sendMessage: (chatId: string, query: string) => Promise<void>;
}

export const useThreadStore = create<ThreadState>((set, get) => ({
  activeChatId: null,
  messages: [],
  isStreaming: false,
  pending: null,

  setPending: (chatId, query) => set({ pending: { chatId, query } }),

  consumePending: (chatId) => {
    const p = get().pending;
    if (!p || p.chatId !== chatId) return null;
    set({ pending: null });
    return p.query;
  },

  clearThread: () => {
    get().cancelStream();
    loadSeq += 1;
    set({
      activeChatId: null,
      messages: [],
      isStreaming: false,
      pending: null,
    });
  },

  cancelStream: () => {
    if (currentAbort) {
      currentAbort.abort();
      currentAbort = null;
    }
    set({ isStreaming: false });
  },

  loadMessages: async (chatId: string) => {
    if (get().isStreaming && get().activeChatId === chatId) return;

    if (get().activeChatId && get().activeChatId !== chatId) {
      get().cancelStream();
    }

    const seq = ++loadSeq;

    const data = (await withRefreshRetry(() =>
      GET(`/chats/${chatId}/messages`)
    )) as ApiMessagesListDto | null;

    if (seq !== loadSeq) return;

    set({
      activeChatId: chatId,
      isStreaming: false,
      messages: (data?.messages ?? []).map((m, i) => ({
        id: `${chatId}:${i}`,
        role: m.role,
        content: m.content,
      })),
    });
  },

  sendMessage: async (chatId: string, query: string) => {
    const text = query.trim();
    if (!text) return;

    get().cancelStream();

    const userId = uid();
    const assistantId = uid();

    set((s) => ({
      activeChatId: chatId,
      isStreaming: true,
      messages: [
        ...(s.activeChatId === chatId ? s.messages : []),
        { id: userId, role: "user", content: text },
        { id: assistantId, role: "assistant", content: "" },
      ],
    }));

    const abort = new AbortController();
    currentAbort = abort;

    try {
      const make = () =>
        POST_STREAM(
          `/chats/${chatId}/messages`,
          { query: text },
          { signal: abort.signal }
        );

      for await (const evt of streamWithRefreshRetry(make)) {
        if (evt.event === "done") break;
        if (!evt.data) continue;

        set((s) => ({
          messages: s.messages.map((m) =>
            m.id === assistantId ? { ...m, content: m.content + evt.data } : m
          ),
        }));
      }
    } catch (e) {
      if (e instanceof DOMException && e.name === "AbortError") return;
      throw e;
    } finally {
      if (currentAbort === abort) currentAbort = null;
      set({ isStreaming: false });
    }
  },
}));
