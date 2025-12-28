import { create } from "zustand";
import type { Message } from "@/types/chat";

interface ThreadState {
  messages: Message[];
  sendMessage: (query: string) => void;
}

export const useThreadStore = create<ThreadState>(() => ({
  messages: [],

  sendMessage: (query: string) => {},
}));
