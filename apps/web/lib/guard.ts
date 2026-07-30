export function isAuthorized(session: { accessToken?: string } | null | undefined): boolean {
  return Boolean(session?.accessToken);
}
