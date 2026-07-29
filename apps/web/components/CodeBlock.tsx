"use client";

import { useRef, useState, type ComponentPropsWithoutRef } from "react";

export function CodeBlock(props: ComponentPropsWithoutRef<"pre">) {
  const preRef = useRef<HTMLPreElement>(null);
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    const text = preRef.current?.textContent ?? "";
    navigator.clipboard?.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  };

  return (
    <div className="group relative">
      <pre ref={preRef} {...props} />
      <button
        type="button"
        onClick={handleCopy}
        aria-label="Salin kode"
        className="absolute right-2 top-2 rounded-md border border-border-standard bg-panel px-2 py-1 text-xs text-text-tertiary opacity-0 transition-opacity hover:text-text-primary group-hover:opacity-100"
      >
        {copied ? "Disalin" : "Salin"}
      </button>
    </div>
  );
}
