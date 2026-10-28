import { tokenExpiresAt } from "../auth/token";
import { NEXT_STATUSES } from "../lib/labels";

const encode = (payload: object) => `h.${btoa(JSON.stringify(payload))}.s`;

describe("tokenExpiresAt", () => {
  it("reads exp in milliseconds", () => {
    expect(tokenExpiresAt(encode({ exp: 100 }))).toBe(100_000);
  });

  it("returns null for malformed tokens", () => {
    expect(tokenExpiresAt("garbage")).toBeNull();
  });
});

describe("status transitions", () => {
  it("never allows leaving DELIVERED and only reaches IN_REPAIR from approval or testing", () => {
    expect(NEXT_STATUSES.DELIVERED).toEqual([]);
    const sources = Object.entries(NEXT_STATUSES)
      .filter(([, next]) => next.includes("IN_REPAIR"))
      .map(([from]) => from)
      .sort();
    expect(sources).toEqual(["AWAITING_APPROVAL", "IN_TESTING"]);
  });
});
