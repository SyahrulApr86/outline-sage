"use client";

import { useEffect, useState } from "react";
import { signOut } from "next-auth/react";
import { ThemeToggle } from "@/components/ThemeToggle";

interface ConversationSummary {
  id: string;
  title: string;
  created_at: string;
}

export interface SidebarUser {
  name?: string | null;
  image?: string | null;
}

export function ConversationSidebar({
  activeId,
  refreshSignal,
  onSelect,
  onNewConversation,
  user,
  isOpen,
  onClose,
}: {
  activeId?: string;
  refreshSignal?: number;
  onSelect: (id: string) => void;
  onNewConversation: () => void;
  user: SidebarUser;
  isOpen: boolean;
  onClose: () => void;
}) {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);

  useEffect(() => {
    let cancelled = false;
    fetch("/api/conversations")
      .then((resp) => (resp.ok ? resp.json() : []))
      .then((data: ConversationSummary[]) => {
        if (!cancelled) setConversations(data);
      })
      .catch(() => {
        if (!cancelled) setConversations([]);
      });
    return () => {
      cancelled = true;
    };
  }, [refreshSignal]);

  const initial = (user.name ?? "?").trim().charAt(0).toUpperCase() || "?";

  return (
    <>
      {isOpen && (
        <div
          data-testid="sidebar-overlay"
          className="fixed inset-0 z-30 bg-black/50 md:hidden"
          onClick={onClose}
        />
      )}
      <nav
        data-testid="conversation-sidebar"
        className={`fixed inset-y-0 left-0 z-40 flex w-64 shrink-0 flex-col border-r border-border-subtle bg-panel transition-transform duration-200 md:static md:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between px-4 py-4">
          <span className="text-sm font-semibold tracking-tight text-text-primary">
            outline-sage
          </span>
          <ThemeToggle />
        </div>

        <div className="px-3">
          <button
            type="button"
            onClick={() => {
              onNewConversation();
              onClose();
            }}
            className="w-full rounded-lg border border-border-standard bg-surface px-3 py-2 text-left text-sm font-medium text-text-primary transition-colors hover:border-transparent hover:bg-accent hover:text-white"
          >
            + Percakapan baru
          </button>
        </div>

        <div className="mt-3 flex-1 overflow-y-auto px-2">
          <ul className="flex flex-col gap-1">
            {conversations.map((conversation) => (
              <li key={conversation.id}>
                <button
                  type="button"
                  onClick={() => {
                    onSelect(conversation.id);
                    onClose();
                  }}
                  className={`w-full rounded-lg px-3 py-2 text-left text-sm text-text-secondary transition-colors hover:bg-surface hover:text-text-primary ${
                    activeId === conversation.id ? "bg-surface text-text-primary" : ""
                  }`}
                >
                  {conversation.title || "Percakapan baru"}
                </button>
              </li>
            ))}
            {conversations.length === 0 && (
              <li className="px-3 py-2 text-sm text-text-tertiary">Belum ada percakapan</li>
            )}
          </ul>
        </div>

        <div className="flex items-center gap-3 border-t border-border-subtle px-4 py-3">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent text-xs font-semibold text-white">
            {initial}
          </div>
          <div className="flex-1 truncate text-sm text-text-secondary">{user.name ?? "User"}</div>
          <button
            type="button"
            onClick={() => signOut({ callbackUrl: "/chat" })}
            className="text-xs font-medium text-text-tertiary hover:text-text-primary"
          >
            Keluar
          </button>
        </div>
      </nav>
    </>
  );
}
