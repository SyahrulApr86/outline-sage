import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { MessageContent } from "@/components/MessageContent";

describe("MessageContent", () => {
  it("renders markdown formatting", () => {
    render(<MessageContent content="Ini **penting** dan `kode`." />);
    expect(screen.getByText("penting").tagName).toBe("STRONG");
    expect(screen.getByText("kode").tagName).toBe("CODE");
  });

  it("renders code blocks with syntax highlighting classes", () => {
    render(<MessageContent content={"```js\nconst a = 1;\n```"} />);
    const code = document.querySelector("code");
    expect(code).toHaveClass("hljs");
  });

  it("converts citation labels into badge links", () => {
    render(<MessageContent content="Fakta penting [chunk-1]." />);
    const badge = screen.getByRole("link", { name: "1" });
    expect(badge).toHaveAttribute("href", "#citation-1");
    expect(badge).toHaveClass("citation-badge");
  });

  it("renders external links with target blank", () => {
    render(<MessageContent content="[Outline](https://example.com)" />);
    const link = screen.getByRole("link", { name: "Outline" });
    expect(link).toHaveAttribute("target", "_blank");
  });
});
