import { describe, expect, it } from "vitest";
import { linkifyCitations } from "@/lib/markdown";

describe("linkifyCitations", () => {
  it("converts a single citation label into an anchor link", () => {
    expect(linkifyCitations("Fakta [chunk-1].")).toBe("Fakta [1](#citation-1).");
  });

  it("converts multiple separate citation labels", () => {
    expect(linkifyCitations("A [chunk-1] dan B [chunk-2].")).toBe(
      "A [1](#citation-1) dan B [2](#citation-2)."
    );
  });

  it("leaves text without citation labels unchanged", () => {
    expect(linkifyCitations("Tidak ada rujukan di sini.")).toBe("Tidak ada rujukan di sini.");
  });
});
