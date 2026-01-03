import { create } from "zustand";

import type { Chat } from "@/types/chat";
import type { ApiChatsListDto, ApiChatTitleDto } from "@/types/api";
import { GET, DELETE, PATCH } from "@/lib/api";
import { withRefreshRetry } from "@/lib/retry";

interface ChatsState {
  chats: Chat[];

  loadChats: () => Promise<void>;
  addChat: (chatId: string, title?: string) => void;

  createTitle: (chatId: string, query: string) => Promise<void>;

  removeChat: (chatId: string) => Promise<void>;
  clearChats: () => Promise<void>;
}

export const useChatsStore = create<ChatsState>((set, get) => ({
  chats: [],

  loadChats: async () => {
    const data = await withRefreshRetry(() => GET<ApiChatsListDto>("/chats"));

    set({
      chats: (data.chats ?? []).map((c) => ({ id: c.id, title: c.title })),
    });
  },

  addChat: (chatId: string, title = "New chat") => {
    set((s) => {
      if (s.chats.some((c) => c.id === chatId)) return s;
      return { chats: [{ id: chatId, title }, ...s.chats] };
    });
  },

  createTitle: async (chatId: string, query: string) => {
    const data = await withRefreshRetry<ApiChatTitleDto>(() =>
      PATCH(`/chats/${chatId}`, { query })
    );

    set((s) => ({
      chats: s.chats.map((c) =>
        c.id === chatId ? { ...c, title: data.title } : c
      ),
    }));
  },

  removeChat: async (chatId: string) => {
    const prev = get().chats;

    set((s) => ({ chats: s.chats.filter((c) => c.id !== chatId) }));

    try {
      await withRefreshRetry(() => DELETE(`/chats/${chatId}`));
    } catch (e) {
      set({ chats: prev });
      throw e;
    }
  },

  clearChats: async () => {
    const prev = get().chats;
    if (prev.length === 0) return;

    set({ chats: [] });

    try {
      await withRefreshRetry(() => DELETE("/chats"));
    } catch (e) {
      set({ chats: prev });
      throw e;
    }
  },
}));
