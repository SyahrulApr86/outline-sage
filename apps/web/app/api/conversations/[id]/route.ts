import { auth } from "@/lib/auth";
import { isAuthorized } from "@/lib/guard";

const API_SERVICE_URL = process.env.API_SERVICE_URL ?? "http://localhost:8000";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
): Promise<Response> {
  const session = await auth();
  const accessToken = (session as { accessToken?: string } | null)?.accessToken;

  if (!isAuthorized({ accessToken })) {
    return new Response(JSON.stringify({ error: "unauthorized" }), { status: 401 });
  }

  const { id } = await params;
  const upstream = await fetch(`${API_SERVICE_URL}/api/conversations/${id}`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  return new Response(upstream.body, {
    status: upstream.status,
    headers: { "Content-Type": "application/json" },
  });
}
