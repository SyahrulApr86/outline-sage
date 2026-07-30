"use client";

import { useEffect, useState } from "react";

export function ThinkingBlock({ thinking, isThinking }: { thinking: string; isThinking: boolean }) {
  const [expanded, setExpanded] = useState(isThinking);

  useEffect(() => {
    setExpanded(isThinking);
  }, [isThinking]);

  if (!thinking) {
    return null;
  }

  return (
    <div className="mb-2 rounded-md border border-border-subtle bg-background/50 text-xs">
      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        className="flex w-full items-center gap-1.5 px-2.5 py-1.5 text-text-tertiary hover:text-text-secondary"
      >
        <span>{expanded ? "▾" : "▸"}</span>
        <span>{isThinking ? "Berpikir…" : "Proses berpikir"}</span>
      </button>
      {expanded && (
        <div className="whitespace-pre-wrap border-t border-border-subtle px-2.5 py-2 text-text-tertiary">
          {thinking}
        </div>
      )}
    </div>
  );
}
