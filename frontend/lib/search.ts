export function formatScore(score: number | null | undefined): string | null {
  if (score === null || score === undefined || Number.isNaN(score)) {
    return null;
  }
  return score.toFixed(2);
}
