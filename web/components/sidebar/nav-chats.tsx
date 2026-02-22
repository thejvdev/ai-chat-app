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

  const chatUrl = React.useCallback(
    (id: string) => new URL(chatHref(id), window.location.origin).toString(),
    []
  );

  const handleCopyLink = React.useCallback(
    async (id: string) => {
      await navigator.clipboard.writeText(chatUrl(id));
    },
    [chatUrl]
  );

  const handleOpenNewTab = React.useCallback(
    (id: string) => {
      window.open(chatUrl(id), "_blank", "noopener,noreferrer");
    },
    [chatUrl]
  );

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
        {chats.length > 0 ? (
          chats.map((c) => (
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

                  <DropdownMenuItem
                    onSelect={() => handleDelete(c.id)}
                    className="
                      text-destructive
                      focus:text-destructive
                      focus:bg-destructive/10
                      hover:bg-destructive/10
                    "
                  >
                    <Trash2 className="text-destructive" />
                    <span>Delete</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </SidebarMenuItem>
          ))
        ) : (
          <div className="flex h-8 items-center justify-center text-sm text-muted-foreground">
            No chats yet
          </div>
        )}
      </SidebarMenu>
    </SidebarGroup>
  );
}
