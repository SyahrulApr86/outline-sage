import { describe, expect, it } from "vitest";
import { splitThinking } from "@/lib/think";

describe("splitThinking", () => {
  it("returns content unchanged when there is no think tag", () => {
    expect(splitThinking("hello world")).toEqual({
      thinking: "",
      answer: "hello world",
      isThinking: false,
    });
  });

  it("extracts a closed think block from the answer", () => {
    const result = splitThinking("<think>reasoning here</think>final answer");
    expect(result).toEqual({
      thinking: "reasoning here",
      answer: "final answer",
      isThinking: false,
    });
  });

  it("treats an unclosed think block as still streaming", () => {
    const result = splitThinking("<think>partial reasoning");
    expect(result).toEqual({
      thinking: "partial reasoning",
      answer: "",
      isThinking: true,
    });
  });
});
