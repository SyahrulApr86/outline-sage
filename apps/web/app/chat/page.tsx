import { redirect } from "next/navigation";
import { auth } from "@/lib/auth";
import { ChatShell } from "@/components/ChatShell";

export default async function ChatPage() {
  const session = await auth();
  if (!session) {
    redirect("/api/auth/signin");
  }

  return (
    <main>
      <ChatShell user={{ name: session.user?.name ?? null, image: session.user?.image ?? null }} />
    </main>
  );
}
