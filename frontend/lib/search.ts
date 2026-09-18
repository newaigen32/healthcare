export function formatScore(score: number | null): string | null {
  if (score === null || Number.isNaN(score)) {
    return null;
  }
  return score.toFixed(2);
}
