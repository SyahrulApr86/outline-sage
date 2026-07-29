import { afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ChatWindow } from "@/components/ChatWindow";

function sseResponse(lines: string[]): Response {
  const encoder = new TextEncoder();
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      for (const line of lines) {
        controller.enqueue(encoder.encode(`data: ${line}\n\n`));
      }
      controller.enqueue(encoder.encode("data: [DONE]\n\n"));
      controller.close();
    },
  });
  return new Response(stream, { status: 200 });
}

describe("ChatWindow integration", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders streamed text and citation panel from mixed SSE events", async () => {
    const events = [
      JSON.stringify({ type: "text-delta", delta: "Jawaban " }),
      JSON.stringify({ type: "text-delta", delta: "lengkap [chunk-1]." }),
      JSON.stringify({
        type: "data-citation",
        citations: [{ chunk_id: "p1", source_id: "d1", title: "Dokumen A", url: "http://x/a", content: "isi asli" }],
      }),
    ];

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(sseResponse(events))
    );

    render(<ChatWindow />);

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Pertanyaan"), "apa itu X?");
    await user.click(screen.getByRole("button", { name: "Kirim" }));

    await waitFor(() => {
      expect(screen.getByText(/Jawaban lengkap \[chunk-1\]\./)).toBeInTheDocument();
    });

    expect(screen.getByTestId("citation-panel")).toBeInTheDocument();
    expect(screen.getByText(/Dokumen A/)).toBeInTheDocument();
  });

  it("shows an error state when the stream request fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response(null, { status: 500 }))
    );

    render(<ChatWindow />);

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Pertanyaan"), "pertanyaan gagal");
    await user.click(screen.getByRole("button", { name: "Kirim" }));

    await waitFor(() => {
      expect(screen.getByTestId("chat-error")).toBeInTheDocument();
    });
  });
});
