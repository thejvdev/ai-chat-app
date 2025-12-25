import { create } from "zustand";
import type { User } from "@/types/user";
import { GET, POST } from "@/lib/api";

type AuthStatus = "authed" | "guest" | "checking";

interface AuthState {
  user: User | null;
  status: AuthStatus;

  init: () => Promise<void>;
  refresh: () => Promise<boolean>;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  status: "guest",

  init: async () => {
    set({ status: "checking" });

    try {
      const user = (await GET("/auth/me")) as User;
      set({ user, status: "authed" });
    } catch {
      set({ user: null, status: "guest" });
    }
  },

  refresh: async () => {
    try {
      const data = await POST("/auth/refresh");
      const ok = Boolean(data?.ok);

      if (ok) {
        await get().init();
      }

      return ok;
    } catch {
      return false;
    }
  },

  logout: async () => {
    try {
      await POST("/auth/logout");
    } finally {
      set({ user: null, status: "guest" });
    }
  },
}));
