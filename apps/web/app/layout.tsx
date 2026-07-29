import type { ReactNode } from "react";

export const metadata = {
  title: "outline-sage",
  description: "RAG assistant untuk Outline wiki",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="id">
      <body>{children}</body>
    </html>
  );
}
