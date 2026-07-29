"use client";

export function ChatHeader({ onToggleSidebar }: { onToggleSidebar: () => void }) {
  return (
    <header className="flex items-center gap-3 border-b border-border-subtle bg-panel px-4 py-3 md:hidden">
      <button
        type="button"
        onClick={onToggleSidebar}
        aria-label="Buka daftar percakapan"
        className="rounded-lg border border-border-standard bg-surface px-3 py-1.5 text-sm text-text-secondary"
      >
        ☰
      </button>
      <span className="text-sm font-semibold text-text-primary">outline-sage</span>
    </header>
  );
}
