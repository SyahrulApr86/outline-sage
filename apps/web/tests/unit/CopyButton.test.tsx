import { afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { CopyButton } from "@/components/CopyButton";

describe("CopyButton", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("copies the given text to the clipboard and shows confirmation", async () => {
    const user = userEvent.setup();

    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", {
      value: { writeText },
      configurable: true,
    });

    render(<CopyButton text="isi jawaban" />);
    await user.click(screen.getByRole("button", { name: "Salin" }));

    expect(writeText).toHaveBeenCalledWith("isi jawaban");
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Disalin" })).toBeInTheDocument();
    });
  });
});
