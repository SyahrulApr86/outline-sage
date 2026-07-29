import type { ChatMessage, ChatStreamEvent } from "./chat-types";

/**
 * Parse satu baris SSE dari backend API Service. Return null untuk baris
 * kosong, [DONE], atau baris yang bukan event data.
 */
export function parseSSELine(line: string): ChatStreamEvent | null {
  if (!line.startsWith("data: ")) {
    return null;
  }
  const data = line.slice("data: ".length).trim();
  if (data === "" || data === "[DONE]") {
    return null;
  }
  try {
    return JSON.parse(data) as ChatStreamEvent;
  } catch {
    return null;
  }
}

/**
 * Terapkan satu event stream ke pesan assistant terakhir (immutable update).
 * Dipisah dari hook supaya bisa diuji tanpa DOM/fetch.
 */
export function applyStreamEvent(messages: ChatMessage[], event: ChatStreamEvent): ChatMessage[] {
  if (messages.length === 0) {
    return messages;
  }
  const next = [...messages];
  const lastIndex = next.length - 1;
  const last = next[lastIndex];

  if (event.type === "text-delta") {
    next[lastIndex] = { ...last, content: last.content + event.delta };
  } else if (event.type === "data-citation") {
    next[lastIndex] = { ...last, citations: event.citations };
  }

  return next;
}
