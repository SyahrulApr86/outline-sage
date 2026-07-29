"use client";

import { useState } from "react";
import { ChatWindow } from "@/components/ChatWindow";
import { ConversationSidebar } from "@/components/ConversationSidebar";

export function ChatShell() {
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);

  return (
    <>
      <ConversationSidebar onSelect={setConversationId} />
      <ChatWindow conversationId={conversationId} key={conversationId ?? "new"} />
    </>
  );
}
