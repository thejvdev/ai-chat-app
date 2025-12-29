"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth.store";
import { useChatsStore } from "@/stores/chats.store";

export default function AppLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const router = useRouter();
  const status = useAuthStore((s) => s.status);
  const loadChats = useChatsStore((s) => s.loadChats);

  useEffect(() => {
    if (status === "guest") {
      router.replace("/login");
    }
  }, [status, router]);

  useEffect(() => {
    if (status === "authed") {
      loadChats();
    }
  }, [status, loadChats]);

  if (status !== "authed") return null;

  return children;
}
