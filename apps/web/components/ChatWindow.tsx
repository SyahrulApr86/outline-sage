"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { useChatStream } from "@/lib/useChatStream";
import { CitationPanel } from "@/components/CitationPanel";
import { MessageContent } from "@/components/MessageContent";
import { ChatHeader } from "@/components/ChatHeader";

export function ChatWindow({
  conversationId,
  onToggleSidebar = () => {},
}: {
  conversationId?: string;
  onToggleSidebar?: () => void;
}) {
  const { messages, sendMessage, isStreaming, error } = useChatStream(conversationId);
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView?.({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (!input.trim() || isStreaming) return;
    void sendMessage(input);
    setInput("");
  };

  return (
    <div data-testid="chat-window" className="flex flex-1 flex-col bg-bg">
      <ChatHeader onToggleSidebar={onToggleSidebar} />
      <div data-testid="message-list" className="flex-1 overflow-y-auto px-6 py-6">
        {messages.length === 0 && (
          <div className="flex h-full items-center justify-center text-sm text-text-tertiary">
            Tanya apa saja tentang isi wiki.
          </div>
        )}
        <div className="mx-auto flex max-w-2xl flex-col gap-4">
          {messages.map((message, index) => (
            <div
              key={index}
              data-testid="message"
              data-role={message.role}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-lg border px-4 py-3 text-sm leading-relaxed ${
                  message.role === "user"
                    ? "border-transparent bg-accent text-white"
                    : "border-border-subtle bg-panel text-text-primary"
                }`}
              >
                {message.role === "assistant" ? (
                  <MessageContent content={message.content} />
                ) : (
                  <p className="whitespace-pre-wrap">{message.content}</p>
                )}
                {message.role === "assistant" && <CitationPanel citations={message.citations} />}
              </div>
            </div>
          ))}
        </div>
        <div ref={bottomRef} />
      </div>

      {error && (
        <div
          role="alert"
          data-testid="chat-error"
          className="mx-6 mb-2 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm text-red-300"
        >
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="border-t border-border-subtle bg-panel px-6 py-4">
        <div className="mx-auto flex max-w-2xl items-center gap-2">
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            disabled={isStreaming}
            aria-label="Pertanyaan"
            placeholder="Tanya sesuatu tentang wiki..."
            className="flex-1 rounded-lg border border-border-standard bg-surface px-4 py-2.5 text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 focus:ring-offset-bg"
          />
          <button
            type="submit"
            disabled={isStreaming}
            className="rounded-lg bg-accent px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-50"
          >
            Kirim
          </button>
        </div>
      </form>
    </div>
  );
}
