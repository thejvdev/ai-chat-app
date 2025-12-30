import { create } from "zustand";
import type { Chat } from "@/types/chat";
import { GET, POST } from "@/lib/api";
import type { ApiChatDto, ApiChatsListDto } from "@/types/api";

interface ChatsState {
  chats: Chat[];
  loadChats: () => Promise<void>;
  createChat: (query: string) => Promise<string | null>;
}

export const useChatsStore = create<ChatsState>((set, get) => ({
  chats: [],

  loadChats: async () => {
    try {
      const data = (await GET("/chats")) as ApiChatsListDto;
      set({
        chats: (data.chats ?? []).map((c) => ({ id: c.id, title: c.title })),
      });
    } catch {}
  },

  createChat: async (query: string) => {
    const trimmed = query.trim();
    if (!trimmed) return null;

    const newChat = (await POST("/chats", { query: trimmed })) as ApiChatDto;

    set({
      chats: [{ id: newChat.id, title: newChat.title }, ...get().chats],
    });

    return newChat.id;
  },
}));
