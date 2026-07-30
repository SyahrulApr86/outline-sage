"use client";

import { useState } from "react";
import { ChatWindow } from "@/components/ChatWindow";
import { ConversationSidebar, type SidebarUser } from "@/components/ConversationSidebar";

export function ChatShell({ user }: { user: SidebarUser }) {
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const [resetKey, setResetKey] = useState(0);
  const [refreshSignal, setRefreshSignal] = useState(0);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen bg-bg text-text-primary">
      <ConversationSidebar
        activeId={conversationId}
        refreshSignal={refreshSignal}
        onSelect={(id) => {
          setConversationId(id);
          setResetKey((k) => k + 1);
        }}
        onNewConversation={() => {
          setConversationId(undefined);
          setResetKey((k) => k + 1);
        }}
        user={user}
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />
      <ChatWindow
        conversationId={conversationId}
        key={resetKey}
        onConversationId={(id) => {
          setConversationId(id);
          setRefreshSignal((s) => s + 1);
        }}
        onToggleSidebar={() => setIsSidebarOpen((open) => !open)}
      />
    </div>
  );
}
