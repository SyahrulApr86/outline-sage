export interface Citation {
  chunk_id: string;
  source_id: string;
  title: string;
  url: string;
  content: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
}

export interface TextDeltaEvent {
  type: "text-delta";
  delta: string;
}

export interface CitationEvent {
  type: "data-citation";
  citations: Citation[];
}

export type ChatStreamEvent = TextDeltaEvent | CitationEvent;
