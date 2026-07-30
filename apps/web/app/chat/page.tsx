import { redirect } from "next/navigation";
import { auth } from "@/lib/auth";
import { isAuthorized } from "@/lib/guard";
import { ChatShell } from "@/components/ChatShell";

export const dynamic = "force-dynamic";

export default async function ChatPage() {
  const session = await auth();

  // !session isn't enough here, auth() can return a truthy empty session
  if (!isAuthorized(session as { accessToken?: string } | null)) {
    redirect("/api/auth/signin");
  }

  return (
    <main>
      <ChatShell user={{ name: session!.user?.name ?? null, image: session!.user?.image ?? null }} />
    </main>
  );
}
