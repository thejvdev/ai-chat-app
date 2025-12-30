"use client";

import Link from "next/link";
import { Collapsible } from "@/components/ui/collapsible";
import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";

import type { Chat } from "@/types/chat";

export function NavMain({ chats }: { chats: Chat[] }) {
  return (
    <SidebarGroup>
      <SidebarGroupLabel>Chats</SidebarGroupLabel>
      <SidebarMenu>
        {chats.map((c) => (
          <Collapsible key={c.id} asChild>
            <SidebarMenuItem>
              <SidebarMenuButton asChild tooltip={c.title}>
                <Link href={`/chats/${c.id}`}>
                  <span>{c.title}</span>
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </Collapsible>
        ))}
      </SidebarMenu>
    </SidebarGroup>
  );
}
