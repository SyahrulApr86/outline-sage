"use client";

import { useState } from "react";
import { ChatWindow } from "@/components/ChatWindow";
import { ConversationSidebar, type SidebarUser } from "@/components/ConversationSidebar";

export function ChatShell({ user }: { user: SidebarUser }) {
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen bg-bg text-text-primary">
      <ConversationSidebar
        onSelect={setConversationId}
        onNewConversation={() => setConversationId(undefined)}
        user={user}
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />
      <ChatWindow
        conversationId={conversationId}
        key={conversationId ?? "new"}
        onToggleSidebar={() => setIsSidebarOpen((open) => !open)}
      />
    </div>
  );
}
