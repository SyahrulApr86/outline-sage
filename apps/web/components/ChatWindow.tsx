"use client";

import { useState, type FormEvent } from "react";
import { useChatStream } from "@/lib/useChatStream";
import { CitationPanel } from "@/components/CitationPanel";

export function ChatWindow({ conversationId }: { conversationId?: string }) {
  const { messages, sendMessage, isStreaming, error } = useChatStream(conversationId);
  const [input, setInput] = useState("");

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (!input.trim() || isStreaming) return;
    void sendMessage(input);
    setInput("");
  };

  return (
    <div data-testid="chat-window">
      <div data-testid="message-list">
        {messages.map((message, index) => (
          <div key={index} data-testid="message" data-role={message.role}>
            <strong>{message.role}:</strong> {message.content}
            {message.role === "assistant" && <CitationPanel citations={message.citations} />}
          </div>
        ))}
      </div>

      {error && (
        <div role="alert" data-testid="chat-error">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          disabled={isStreaming}
          aria-label="Pertanyaan"
        />
        <button type="submit" disabled={isStreaming}>
          Kirim
        </button>
      </form>
    </div>
  );
}
