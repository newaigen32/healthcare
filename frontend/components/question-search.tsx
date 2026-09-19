"use client";

import { FormEvent, KeyboardEvent, useState } from "react";

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
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  async function runSearch() {
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
      setTotal(response.total);
    } catch {
      setResults([]);
      setTotal(0);
      setErrorMessage(FRIENDLY_ERROR);
    } finally {
      setIsLoading(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void runSearch();
  }

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Enter") {
      event.preventDefault();
      void runSearch();
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
            onKeyDown={handleKeyDown}
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
        total={total}
        results={results}
        isLoading={isLoading}
        errorMessage={errorMessage}
        hasSearched={hasSearched}
      />
    </div>
  );
}
