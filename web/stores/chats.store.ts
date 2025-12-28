import { create } from "zustand";
import type { ChatItem } from "@/types/chat";

interface ChatsState {
  chats: ChatItem[];

  loadChats: () => void;
  createChat: () => void;
  removeChat: () => void;
  clearChats: () => void;
}

export const useChatsStore = create<ChatsState>((set, get) => ({
  chats: [],

  loadChats: () => {},

  createChat: () => {},

  removeChat: () => {},

  clearChats: () => {},
}));
