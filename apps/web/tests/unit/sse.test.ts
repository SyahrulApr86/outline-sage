import { describe, expect, it } from "vitest";
import { applyStreamEvent, parseSSELine } from "@/lib/sse";
import type { ChatMessage } from "@/lib/chat-types";

describe("parseSSELine", () => {
  it("parses a text-delta event", () => {
    const event = parseSSELine('data: {"type":"text-delta","delta":"halo"}');
    expect(event).toEqual({ type: "text-delta", delta: "halo" });
  });

  it("returns null for [DONE] sentinel", () => {
    expect(parseSSELine("data: [DONE]")).toBeNull();
  });

  it("returns null for non-data lines", () => {
    expect(parseSSELine("event: ping")).toBeNull();
  });

  it("returns null for malformed json", () => {
    expect(parseSSELine("data: {not valid json")).toBeNull();
  });
});

describe("applyStreamEvent", () => {
  const base: ChatMessage[] = [
    { role: "user", content: "pertanyaan" },
    { role: "assistant", content: "" },
  ];

  it("appends text-delta to the last message", () => {
    const result = applyStreamEvent(base, { type: "text-delta", delta: "halo" });
    expect(result[1].content).toBe("halo");
    expect(result[0].content).toBe("pertanyaan"); // pesan lain tidak berubah
  });

  it("accumulates multiple text-delta calls", () => {
    let messages = applyStreamEvent(base, { type: "text-delta", delta: "ha" });
    messages = applyStreamEvent(messages, { type: "text-delta", delta: "lo" });
    expect(messages[1].content).toBe("halo");
  });

  it("attaches citations from data-citation event", () => {
    const citations = [
      { chunk_id: "c1", source_id: "d1", title: "A", url: "u1", content: "isi" },
    ];
    const result = applyStreamEvent(base, { type: "data-citation", citations });
    expect(result[1].citations).toEqual(citations);
  });

  it("returns messages unchanged when list is empty", () => {
    expect(applyStreamEvent([], { type: "text-delta", delta: "x" })).toEqual([]);
  });
});
