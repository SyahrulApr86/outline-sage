import { auth } from "@/lib/auth";
import { isAuthorized } from "@/lib/guard";

const API_SERVICE_URL = process.env.API_SERVICE_URL ?? "http://localhost:8000";

export async function POST(request: Request): Promise<Response> {
  const session = await auth();
  const accessToken = (session as { accessToken?: string } | null)?.accessToken;

  if (!isAuthorized({ accessToken })) {
    return new Response(JSON.stringify({ error: "unauthorized" }), { status: 401 });
  }

  const body = await request.text();

  const upstream = await fetch(`${API_SERVICE_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body,
  });

  return new Response(upstream.body, {
    status: upstream.status,
    headers: { "Content-Type": "text/event-stream" },
  });
}
