"use client";

import * as React from "react";
import { Command } from "lucide-react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";

import { NavChats } from "@/components/sidebar/nav-chats";
import { NavUser } from "@/components/sidebar/nav-user";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";

import type { User } from "@/types/user";

import { removeChat, clearChats } from "@/lib/chat-actions";
import { useChatsStore } from "@/stores/chats.store";
import { useThreadStore } from "@/stores/thread.store";
import { useAuthStore } from "@/stores/auth.store";

function getAvatarFallback(name: string) {
  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase() ?? "")
    .join("");
}

export function AppSidebar(props: React.ComponentProps<typeof Sidebar>) {
  const { isMobile } = useSidebar();
  const router = useRouter();
  const pathname = usePathname();

  const chats = useChatsStore((s) => s.chats);
  const activeChatId = useThreadStore((s) => s.activeChatId);

  const user = useAuthStore((s) => s.user) as User | null;
  const logout = useAuthStore((s) => s.logout);

  const name = user?.name ?? "User";
  const email = user?.email ?? "";
  const avatarFallback = React.useMemo(() => getAvatarFallback(name), [name]);

  const handleRemoveChat = React.useCallback(
    async (chatId: string) => {
      await removeChat(chatId);

      const isOnThatChatPage = pathname.startsWith(`/chats/${chatId}`);
      const wasActive = activeChatId === chatId;

      if (wasActive || isOnThatChatPage) {
        router.replace("/");
      }
    },
    [activeChatId, pathname, router]
  );

  const handleClearChats = React.useCallback(async () => {
    await clearChats();
    router.replace("/");
  }, [router]);

  const handleLogout = React.useCallback(() => {
    void logout();
  }, [logout]);

  return (
    <Sidebar variant="inset" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <Link href="/">
                <div className="bg-sidebar-primary text-sidebar-primary-foreground flex aspect-square size-8 items-center justify-center rounded-lg">
                  <Command className="size-4" />
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-medium">AI Chat</span>
                  <span className="truncate text-xs">Synapse</span>
                </div>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <NavChats chats={chats} onRemove={handleRemoveChat} />
      </SidebarContent>

      <SidebarFooter>
        <NavUser
          name={name}
          email={email}
          avatarFallback={avatarFallback}
          isMobile={isMobile}
          onLogout={handleLogout}
          onDeleteAllChats={handleClearChats}
        />
      </SidebarFooter>
    </Sidebar>
  );
}
