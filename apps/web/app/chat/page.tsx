import { redirect } from "next/navigation";
import { auth } from "@/lib/auth";
import { isAuthorized } from "@/lib/guard";
import { ChatShell } from "@/components/ChatShell";

export const dynamic = "force-dynamic";

export default async function ChatPage() {
  const session = await auth();

  // auth() dari next-auth v5 beta bisa mengembalikan objek session yang
  // truthy (mis. { user: {} }) walau tidak ada cookie sama sekali, jadi
  // `!session` saja tidak cukup untuk menolak akses. accessToken hanya
  // terisi lewat callback jwt saat login OIDC benar-benar terjadi (lihat
  // lib/auth.ts), jadi itu sinyal yang dipakai di sini dan di BFF proxy
  // (lib/guard.ts) untuk otorisasi yang sebenarnya.
  if (!isAuthorized(session as { accessToken?: string } | null)) {
    redirect("/api/auth/signin");
  }

  return (
    <main>
      <ChatShell user={{ name: session!.user?.name ?? null, image: session!.user?.image ?? null }} />
    </main>
  );
}
