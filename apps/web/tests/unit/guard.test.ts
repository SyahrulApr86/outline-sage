import { describe, expect, it } from "vitest";
import { isAuthorized } from "@/lib/guard";

describe("isAuthorized", () => {
  it("returns false for null session", () => {
    expect(isAuthorized(null)).toBe(false);
  });

  it("returns false for session without accessToken", () => {
    expect(isAuthorized({})).toBe(false);
  });

  it("returns true for session with accessToken", () => {
    expect(isAuthorized({ accessToken: "token-abc" })).toBe(true);
  });
});
