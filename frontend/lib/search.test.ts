import { formatScore } from "@/lib/search";

describe("formatScore", () => {
  it("formats numeric relevance scores", () => {
    expect(formatScore(0.92)).toBe("0.92");
  });

  it("returns null when a score is not available", () => {
    expect(formatScore(null)).toBeNull();
  });
});
