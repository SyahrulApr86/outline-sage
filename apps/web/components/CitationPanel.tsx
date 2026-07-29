import type { Citation } from "@/lib/chat-types";

export function CitationPanel({ citations }: { citations?: Citation[] }) {
  if (!citations || citations.length === 0) {
    return null;
  }

  return (
    <div data-testid="citation-panel" className="mt-3 border-t border-border-subtle pt-3">
      <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-text-tertiary">
        Rujukan
      </h3>
      <ul className="flex flex-col gap-2">
        {citations.map((citation, index) => (
          <li
            key={citation.chunk_id}
            data-testid="citation-item"
            id={`citation-${index + 1}`}
            className="rounded-lg border border-border-subtle bg-surface px-3 py-2 text-xs"
          >
            <a
              href={citation.url}
              target="_blank"
              rel="noreferrer"
              className="font-medium text-accent-violet hover:text-accent-hover"
            >
              [{index + 1}] {citation.title}
            </a>
            <p className="mt-1 line-clamp-2 text-text-secondary">{citation.content}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
