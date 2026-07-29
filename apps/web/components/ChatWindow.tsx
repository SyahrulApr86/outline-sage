"use client";

import { useEffect, useRef, useState, type KeyboardEvent } from "react";
import { useChatStream } from "@/lib/useChatStream";
import { CitationPanel } from "@/components/CitationPanel";
import { MessageContent } from "@/components/MessageContent";
import { ChatHeader } from "@/components/ChatHeader";
import { ThinkingIndicator } from "@/components/ThinkingIndicator";
import { CopyButton } from "@/components/CopyButton";

const SCROLL_BOTTOM_THRESHOLD_PX = 80;
const TEXTAREA_MAX_HEIGHT_PX = 200;

export function ChatWindow({
  conversationId,
  onToggleSidebar = () => {},
}: {
  conversationId?: string;
  onToggleSidebar?: () => void;
}) {
  const { messages, sendMessage, isStreaming, error } = useChatStream(conversationId);
  const [input, setInput] = useState("");
  const listRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const isAtBottomRef = useRef(true);

  useEffect(() => {
    if (isAtBottomRef.current) {
      bottomRef.current?.scrollIntoView?.({ behavior: "smooth" });
    }
  }, [messages]);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, TEXTAREA_MAX_HEIGHT_PX)}px`;
  }, [input]);

  const handleScroll = () => {
    const el = listRef.current;
    if (!el) return;
    isAtBottomRef.current =
      el.scrollHeight - el.scrollTop - el.clientHeight < SCROLL_BOTTOM_THRESHOLD_PX;
  };

  const submit = (text: string) => {
    if (!text.trim() || isStreaming) return;
    isAtBottomRef.current = true;
    void sendMessage(text);
    setInput("");
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submit(input);
    }
  };

  return (
    <div data-testid="chat-window" className="flex flex-1 flex-col bg-bg">
      <ChatHeader onToggleSidebar={onToggleSidebar} />
      <div
        ref={listRef}
        onScroll={handleScroll}
        data-testid="message-list"
        className="flex-1 overflow-y-auto px-6 py-6"
      >
        {messages.length === 0 && (
          <div className="flex h-full items-center justify-center text-sm text-text-tertiary">
            Tanya apa saja tentang isi wiki.
          </div>
        )}
        <div className="mx-auto flex max-w-2xl flex-col gap-4">
          {messages.map((message, index) => {
            const isLast = index === messages.length - 1;
            const isEmptyStreamingAssistant =
              message.role === "assistant" && message.content === "" && isStreaming && isLast;

            return (
              <div
                key={index}
                data-testid="message"
                data-role={message.role}
                className={`flex flex-col ${message.role === "user" ? "items-end" : "items-start"}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg border px-4 py-3 text-sm leading-relaxed ${
                    message.role === "user"
                      ? "border-transparent bg-accent text-white"
                      : "border-border-subtle bg-panel text-text-primary"
                  }`}
                >
                  {message.role === "assistant" ? (
                    isEmptyStreamingAssistant ? (
                      <ThinkingIndicator />
                    ) : (
                      <MessageContent content={message.content} />
                    )
                  ) : (
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  )}
                  {message.role === "assistant" && <CitationPanel citations={message.citations} />}
                </div>
                {message.role === "assistant" && message.content && (
                  <div className="mt-1 px-1">
                    <CopyButton text={message.content} />
                  </div>
                )}
              </div>
            );
          })}
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

      <form
        onSubmit={(event) => {
          event.preventDefault();
          submit(input);
        }}
        className="border-t border-border-subtle bg-panel px-6 py-4"
      >
        <div className="mx-auto flex max-w-2xl items-end gap-2">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isStreaming}
            aria-label="Pertanyaan"
            placeholder="Tanya sesuatu tentang wiki... (Enter untuk kirim, Shift+Enter baris baru)"
            rows={1}
            className="max-h-[200px] flex-1 resize-none rounded-lg border border-border-standard bg-surface px-4 py-2.5 text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 focus:ring-offset-bg"
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
