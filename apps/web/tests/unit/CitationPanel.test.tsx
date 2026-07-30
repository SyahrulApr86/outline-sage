import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { CitationPanel } from "@/components/CitationPanel";

describe("CitationPanel", () => {
  it("renders nothing when there are no citations", () => {
    const { container } = render(<CitationPanel citations={[]} />);
    expect(container).toBeEmptyDOMElement();
  });

  it("renders nothing when citations is undefined", () => {
    const { container } = render(<CitationPanel />);
    expect(container).toBeEmptyDOMElement();
  });

  it("renders one entry per citation with title and link", () => {
    render(
      <CitationPanel
        citations={[
          { chunk_id: "c1", source_id: "d1", title: "Panduan A", url: "http://x/a", content: "isi a" },
          { chunk_id: "c2", source_id: "d2", title: "Panduan B", url: "http://x/b", content: "isi b" },
        ]}
      />
    );

    const items = screen.getAllByTestId("citation-item");
    expect(items).toHaveLength(2);
    expect(screen.getByText(/Panduan A/)).toBeInTheDocument();
    expect(screen.getByText(/Panduan B/)).toBeInTheDocument();
  });

  it("hides additional citations behind a toggle", async () => {
    render(
      <CitationPanel
        citations={[{ chunk_id: "c1", source_id: "d1", title: "Panduan A", url: "http://x/a", content: "isi a" }]}
        additionalCitations={[
          { chunk_id: "c2", source_id: "d2", title: "Panduan B", url: "http://x/b", content: "isi b" },
        ]}
      />
    );

    expect(screen.queryByText(/Panduan B/)).not.toBeInTheDocument();

    await userEvent.click(screen.getByText(/Sumber lain yang dipertimbangkan/));

    expect(screen.getByText(/Panduan B/)).toBeInTheDocument();
  });
});
