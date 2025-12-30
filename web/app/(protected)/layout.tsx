"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { AppSidebar } from "@/components/sidebar/app-sidebar";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";

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

  return (
    <SidebarProvider className="h-svh">
      <AppSidebar />

      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2">
          <div className="flex items-center gap-2 px-4">
            <SidebarTrigger className="-ml-1" />
            <Separator
              orientation="vertical"
              className="mr-2 data-[orientation=vertical]:h-4"
            />
          </div>
        </header>

        {children}
      </SidebarInset>
    </SidebarProvider>
  );
}
