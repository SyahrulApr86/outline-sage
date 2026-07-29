"use client";

import { useEffect, useState } from "react";

interface ConversationSummary {
  id: string;
  title: string;
  created_at: string;
}

export function ConversationSidebar({ onSelect }: { onSelect: (id: string) => void }) {
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
  }, []);

  return (
    <nav data-testid="conversation-sidebar">
      <ul>
        {conversations.map((conversation) => (
          <li key={conversation.id}>
            <button type="button" onClick={() => onSelect(conversation.id)}>
              {conversation.title || "Percakapan baru"}
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
}
