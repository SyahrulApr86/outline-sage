import NextAuth from "next-auth";
import type { NextAuthConfig, Session } from "next-auth";
import type { JWT } from "next-auth/jwt";

const config: NextAuthConfig = {
  trustHost: true, // required behind a reverse proxy, else UntrustedHost error

  providers: [
    {
      id: "keycloak",
      name: "Keycloak",
      type: "oidc",
      issuer: process.env.KEYCLOAK_ISSUER,
      clientId: process.env.KEYCLOAK_CLIENT_ID,
      clientSecret: process.env.KEYCLOAK_CLIENT_SECRET,
    },
  ],
  callbacks: {
    async jwt({ token, account }: { token: JWT; account: unknown }) {
      const acc = account as { access_token?: string } | null;
      if (acc?.access_token) {
        token.accessToken = acc.access_token;
      }
      return token;
    },
    async session({ session, token }: { session: Session; token: JWT }) {
      (session as Session & { accessToken?: string }).accessToken = token.accessToken as
        | string
        | undefined;
      return session;
    },
  },
};

export const { handlers, signIn, signOut, auth } = NextAuth(config);
