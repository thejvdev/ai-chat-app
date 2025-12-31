"use client";

import * as React from "react";
import Link from "next/link";
import {
  ArrowUpRight,
  Link as LinkIcon,
  MoreHorizontal,
  Trash2,
} from "lucide-react";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuAction,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";

import type { Chat } from "@/types/chat";

interface NavChatsProps {
  chats: Chat[];
  onRemove: (chatId: string) => Promise<void>;
}

const chatHref = (id: string) => `/chats/${id}`;

export function NavChats({ chats, onRemove }: NavChatsProps) {
  const { isMobile } = useSidebar();

  const handleCopyLink = React.useCallback(async (id: string) => {
    const href = chatHref(id);
    await navigator.clipboard.writeText(href);
  }, []);

  const handleOpenNewTab = React.useCallback((id: string) => {
    const href = chatHref(id);
    window.open(href, "_blank", "noopener,noreferrer");
  }, []);

  const handleDelete = React.useCallback(
    (id: string) => {
      void onRemove(id);
    },
    [onRemove]
  );

  return (
    <SidebarGroup className="group-data-[collapsible=icon]:hidden">
      <SidebarGroupLabel>Chats</SidebarGroupLabel>

      <SidebarMenu>
        {chats.map((c) => (
          <SidebarMenuItem key={c.id}>
            <SidebarMenuButton asChild>
              <Link href={chatHref(c.id)}>
                <span>{c.title}</span>
              </Link>
            </SidebarMenuButton>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <SidebarMenuAction showOnHover>
                  <MoreHorizontal />
                  <span className="sr-only">More</span>
                </SidebarMenuAction>
              </DropdownMenuTrigger>

              <DropdownMenuContent
                className="w-56 rounded-lg"
                side={isMobile ? "bottom" : "right"}
                align={isMobile ? "end" : "start"}
              >
                <DropdownMenuItem onSelect={() => void handleCopyLink(c.id)}>
                  <LinkIcon className="text-muted-foreground" />
                  <span>Copy Link</span>
                </DropdownMenuItem>

                <DropdownMenuItem onSelect={() => handleOpenNewTab(c.id)}>
                  <ArrowUpRight className="text-muted-foreground" />
                  <span>Open in New Tab</span>
                </DropdownMenuItem>

                <DropdownMenuSeparator />

                <DropdownMenuItem onSelect={() => handleDelete(c.id)}>
                  <Trash2 className="text-muted-foreground" />
                  <span>Delete</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        ))}
      </SidebarMenu>
    </SidebarGroup>
  );
}
