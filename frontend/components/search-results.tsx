import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { SearchResultCard } from "@/components/search-result-card";
import type { SearchResult } from "@/types/search";

type SearchResultsProps = {
  query: string;
  total: number;
  results: SearchResult[];
  isLoading: boolean;
  errorMessage: string | null;
  hasSearched: boolean;
};

export function SearchResults({
  query,
  total,
  results,
  isLoading,
  errorMessage,
  hasSearched,
}: SearchResultsProps) {
  if (isLoading) {
    return (
      <Alert>
        <AlertTitle>Searching company documents</AlertTitle>
        <AlertDescription>
          Looking for information related to your question...
        </AlertDescription>
      </Alert>
    );
  }

  if (errorMessage) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Search unavailable</AlertTitle>
        <AlertDescription>{errorMessage}</AlertDescription>
      </Alert>
    );
  }

  if (!hasSearched) {
    return (
      <Alert>
        <AlertTitle>Ready when you are</AlertTitle>
        <AlertDescription>
          Ask a question about SOPs, payer rules, or previous cases. Relevant
          documents will appear here.
        </AlertDescription>
      </Alert>
    );
  }

  if (total === 0 || results.length === 0) {
    return (
      <Alert>
        <AlertTitle>No documents found</AlertTitle>
        <AlertDescription>No matching documents were found.</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-muted-foreground">
        Showing {total} result{total === 1 ? "" : "s"} for “{query}”
      </p>
      <div className="space-y-4">
        {results.map((result) => (
          <SearchResultCard key={result.id} result={result} />
        ))}
      </div>
    </div>
  );
}
