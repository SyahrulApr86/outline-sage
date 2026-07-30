"use client";

import { useState } from "react";
import type { Citation } from "@/lib/chat-types";

function CitationList({ citations, offset }: { citations: Citation[]; offset: number }) {
  return (
    <ul className="flex flex-col gap-2">
      {citations.map((citation, index) => (
        <li
          key={`${citation.chunk_id}-${offset + index}`}
          data-testid="citation-item"
          id={`citation-${offset + index + 1}`}
          className="rounded-lg border border-border-subtle bg-surface px-3 py-2 text-xs"
        >
          <a
            href={citation.url}
            target="_blank"
            rel="noreferrer"
            className="font-medium text-accent-violet hover:text-accent-hover"
          >
            [{offset + index + 1}] {citation.title}
          </a>
          <p className="mt-1 line-clamp-2 text-text-secondary">{citation.content}</p>
        </li>
      ))}
    </ul>
  );
}

export function CitationPanel({
  citations,
  additionalCitations,
}: {
  citations?: Citation[];
  additionalCitations?: Citation[];
}) {
  const [showAdditional, setShowAdditional] = useState(false);
  const hasCitations = citations && citations.length > 0;
  const hasAdditional = additionalCitations && additionalCitations.length > 0;

  if (!hasCitations && !hasAdditional) {
    return null;
  }

  return (
    <div data-testid="citation-panel" className="mt-3 border-t border-border-subtle pt-3">
      {hasCitations && (
        <>
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-text-tertiary">
            Rujukan
          </h3>
          <CitationList citations={citations!} offset={0} />
        </>
      )}

      {hasAdditional && (
        <div className={hasCitations ? "mt-3" : undefined}>
          <button
            type="button"
            onClick={() => setShowAdditional((v) => !v)}
            className="text-xs font-medium text-text-tertiary hover:text-text-secondary"
          >
            {showAdditional ? "▾" : "▸"} Sumber lain yang dipertimbangkan ({additionalCitations!.length})
          </button>
          {showAdditional && (
            <div className="mt-2">
              <CitationList citations={additionalCitations!} offset={citations?.length ?? 0} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
