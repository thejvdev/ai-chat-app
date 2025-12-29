"use client";

import { Collapsible } from "@/components/ui/collapsible";
import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";

import type { ChatItem } from "@/types/chat";

export function NavMain({
  chats,
  onOpen,
}: {
  chats: ChatItem[];
  onOpen: (chatId: string) => void;
}) {
  return (
    <SidebarGroup>
      <SidebarGroupLabel>Chats</SidebarGroupLabel>
      <SidebarMenu>
        {chats.map((c) => (
          <Collapsible key={c.title} asChild>
            <SidebarMenuItem>
              <SidebarMenuButton
                asChild
                onClick={() => onOpen(c.chatId)}
                tooltip={c.title}
              >
                <a href={c.chatId}>
                  <span>{c.title}</span>
                </a>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </Collapsible>
        ))}
      </SidebarMenu>
    </SidebarGroup>
  );
}
