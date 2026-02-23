import { create } from "zustand";

import type { ApiMessagesListDto } from "@/types/api";
import type { ChatMessage } from "@/types/chat";
import { GET } from "@/lib/api";
import { POST_SSE } from "@/lib/sse";
import { withRefreshRetry, sseWithRefreshRetry } from "@/lib/retry";

const uid = () =>
  globalThis.crypto?.randomUUID
    ? globalThis.crypto.randomUUID()
    : `${Date.now()}-${Math.random()}`;

let currentAbort: AbortController | null = null;

interface ThreadState {
  activeChatId: string | null;
  messages: ChatMessage[];
  isStreaming: boolean;
  streamingMessage: string;

  clearThread: () => void;
  cancelStream: () => void;

  loadMessages: (chatId: string) => Promise<void>;
  sendMessage: (chatId: string, query: string) => Promise<string | null>;
}

export const useThreadStore = create<ThreadState>((set, get) => ({
  activeChatId: null,
  messages: [],
  isStreaming: false,
  streamingMessage: "Thinking",

  clearThread: () => {
    get().cancelStream();
    set({
      activeChatId: null,
      messages: [],
      isStreaming: false,
      streamingMessage: "Thinking",
    });
  },

  cancelStream: () => {
    if (currentAbort) {
      currentAbort.abort();
      currentAbort = null;
    }
    set({ isStreaming: false, streamingMessage: "Thinking" });
  },

  loadMessages: async (chatId: string) => {
    if (get().isStreaming && get().activeChatId === chatId) return;

    if (get().activeChatId && get().activeChatId !== chatId) {
      get().cancelStream();
    }

    const data = (await withRefreshRetry(() =>
      GET(`/chats/${chatId}/messages`),
    )) as ApiMessagesListDto | null;

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

  sendMessage: async (
    chatId: string,
    query: string,
  ): Promise<string | null> => {
    const text = query.trim();
    if (!text) return null;

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
        POST_SSE(`/chats/${chatId}/stream`, { query: text }, abort.signal);

      for await (const event of sseWithRefreshRetry(make)) {
        if (event.type === "meta") {
          set({ streamingMessage: event.message ?? "Thinking" });
          continue;
        }

        if (event.type === "stream") {
          const chunk = event.content ?? "";
          if (!chunk) continue;

          set((s) => ({
            messages: s.messages.map((m) =>
              m.id === assistantId ? { ...m, content: m.content + chunk } : m,
            ),
          }));
          continue;
        }

        if (event.type === "error") {
          break;
        }

        if (event.done) break;
      }
    } catch (e) {
      if (e instanceof DOMException && e.name === "AbortError") return chatId;
      throw e;
    } finally {
      if (currentAbort === abort) {
        currentAbort = null;
        set({ isStreaming: false, streamingMessage: "Thinking" });
      }
    }

    return chatId;
  },
}));
