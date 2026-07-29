/** Guard otorisasi BFF proxy: session harus punya accessToken (TSD-003 bagian 6, BFF Proxy). */
export function isAuthorized(session: { accessToken?: string } | null | undefined): boolean {
  return Boolean(session?.accessToken);
}
