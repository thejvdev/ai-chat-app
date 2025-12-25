import { create } from "zustand";
import type { User } from "@/types/user";
import { isApiError, type ApiUser } from "@/types/api";
import { GET, POST } from "@/lib/api";

type AuthStatus = "authed" | "guest" | "checking";

interface AuthState {
  user: User | null;
  status: AuthStatus;

  init: () => Promise<void>;
  refresh: () => Promise<void>;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => {
  const loadUser = async (): Promise<void> => {
    const apiUser = (await GET("/auth/me")) as ApiUser | null;
    if (apiUser) {
      const { id, email, full_name } = apiUser;
      set({ user: { id, email, name: full_name }, status: "authed" });
    } else {
      set({ user: null, status: "guest" });
    }
  };

  const loadUserOrGuest = async (): Promise<void> => {
    try {
      await loadUser();
    } catch {
      set({ user: null, status: "guest" });
    }
  };

  const tryRefresh = async (): Promise<boolean> => {
    try {
      const data = await POST("/auth/refresh");
      return Boolean(data?.ok);
    } catch {
      return false;
    }
  };

  return {
    user: null,
    status: "checking",

    init: async () => {
      set({ status: "checking" });

      try {
        await loadUser();
      } catch (err) {
        if (!isApiError(err)) {
          return set({ user: null, status: "guest" });
        }
        if (err.status === 401 && (await tryRefresh())) {
          await loadUserOrGuest();
          return;
        }
        set({ user: null, status: "guest" });
      }
    },

    refresh: async () => {
      const ok = await tryRefresh();
      if (!ok) {
        return set({ user: null, status: "guest" });
      }
      await loadUserOrGuest();
    },

    logout: async () => {
      try {
        await POST("/auth/logout");
      } finally {
        set({ user: null, status: "guest" });
      }
    },
  };
});
