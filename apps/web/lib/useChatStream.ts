"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { ChatMessage } from "./chat-types";
import { applyStreamEvent, parseSSELine } from "./sse";

export function useChatStream(conversationId?: string, onConversationId?: (id: string) => void) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(!!conversationId);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const selfAssignedIdRef = useRef<string | null>(null);

  useEffect(() => {
    if (!conversationId) return;
    if (selfAssignedIdRef.current === conversationId) return;
    let cancelled = false;
    setIsLoadingHistory(true);
    fetch(`/api/conversations/${conversationId}`)
      .then((resp) => (resp.ok ? resp.json() : []))
      .then((data: ChatMessage[]) => {
        if (!cancelled) setMessages(data);
      })
      .catch(() => {
        if (!cancelled) setMessages([]);
      })
      .finally(() => {
        if (!cancelled) setIsLoadingHistory(false);
      });
    return () => {
      cancelled = true;
    };
  }, [conversationId]);

  const sendMessage = useCallback(
    async (text: string) => {
      setError(null);
      setMessages((prev) => [...prev, { role: "user", content: text }, { role: "assistant", content: "" }]);
      setIsStreaming(true);

      const controller = new AbortController();
      abortRef.current = controller;

      try {
        const resp = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text, conversation_id: conversationId }),
          signal: controller.signal,
        });

        if (!resp.ok || !resp.body) {
          throw new Error(`chat request failed: ${resp.status}`);
        }

        const reader = resp.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });

          const lines = buffer.split("\n\n");
          buffer = lines.pop() ?? "";

          for (const line of lines) {
            const event = parseSSELine(line);
            if (!event) continue;
            if (event.type === "data-conversation") {
              selfAssignedIdRef.current = event.conversation_id;
              onConversationId?.(event.conversation_id);
              continue;
            }
            setMessages((prev) => applyStreamEvent(prev, event));
          }
        }
      } catch (err) {
        if ((err as Error).name !== "AbortError") {
          setError((err as Error).message);
        }
      } finally {
        setIsStreaming(false);
      }
    },
    [conversationId, onConversationId]
  );

  const stop = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  return { messages, sendMessage, isStreaming, isLoadingHistory, error, stop };
}
