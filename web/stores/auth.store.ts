import { create } from "zustand";
import type { User } from "@/types/user";
import { isApiError, type ApiUserDto } from "@/types/api";
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
    const apiUser = (await GET("/auth/me")) as ApiUserDto | null;

    if (!apiUser) {
      set({ user: null, status: "guest" });
      return;
    }

    set({
      user: { id: apiUser.id, email: apiUser.email, name: apiUser.full_name },
      status: "authed",
    });
  };

  const tryRefresh = async (): Promise<boolean> => {
    try {
      const data = (await POST("/auth/refresh")) as { ok?: boolean } | null;
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
        if (isApiError(err) && err.status === 401 && (await tryRefresh())) {
          try {
            await loadUser();
          } catch {
            set({ user: null, status: "guest" });
          }
          return;
        }

        set({ user: null, status: "guest" });
      }
    },

    refresh: async () => {
      const ok = await tryRefresh();
      if (!ok) {
        set({ user: null, status: "guest" });
        return;
      }

      try {
        await loadUser();
      } catch {
        set({ user: null, status: "guest" });
      }
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
