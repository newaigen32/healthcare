"use client";

import { FormEvent, useState } from "react";

import { SearchResults } from "@/components/search-results";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { searchDocuments } from "@/lib/api";
import type { SearchResult } from "@/types/search";

const FRIENDLY_ERROR = "We couldn't complete the search. Please try again.";

export function QuestionSearch() {
  const [query, setQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = query.trim();
    if (!trimmed || isLoading) {
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);
    setHasSearched(true);
    setSubmittedQuery(trimmed);

    try {
      const response = await searchDocuments(trimmed);
      setResults(response.results);
    } catch (error) {
      setResults([]);
      setErrorMessage(error instanceof Error ? error.message : FRIENDLY_ERROR);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="space-y-8">
      <form onSubmit={handleSubmit} className="space-y-4">
        <label htmlFor="question" className="sr-only">
          Question
        </label>
        <div className="flex flex-col gap-3 sm:flex-row">
          <Input
            id="question"
            value={query}
            onValueChange={(value) => setQuery(value)}
            placeholder="Ask about SOPs, payer rules, or previous cases..."
            className="h-11 text-base md:text-base"
            autoComplete="off"
          />
          <Button type="submit" size="lg" className="h-11 px-6" disabled={isLoading}>
            {isLoading ? "Searching..." : "Search"}
          </Button>
        </div>
      </form>
      <SearchResults
        query={submittedQuery}
        results={results}
        isLoading={isLoading}
        errorMessage={errorMessage}
        hasSearched={hasSearched}
      />
    </div>
  );
}
