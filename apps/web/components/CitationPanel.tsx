import type { Citation } from "@/lib/chat-types";

export function CitationPanel({ citations }: { citations?: Citation[] }) {
  if (!citations || citations.length === 0) {
    return null;
  }

  return (
    <div data-testid="citation-panel">
      <h3>Rujukan</h3>
      <ul>
        {citations.map((citation, index) => (
          <li key={citation.chunk_id} data-testid="citation-item" id={`citation-${index + 1}`}>
            <a href={citation.url} target="_blank" rel="noreferrer">
              [{index + 1}] {citation.title}
            </a>
            <p>{citation.content}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
