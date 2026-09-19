import type { SearchRequest, SearchResponse } from "@/types/search";

const FRIENDLY_ERROR = "We couldn't complete the search. Please try again.";

function getApiBaseUrl(): string {
  const value = process.env.NEXT_PUBLIC_API_URL;
  if (!value) {
    throw new Error(FRIENDLY_ERROR);
  }
  return value.replace(/\/$/, "");
}

export async function searchDocuments(query: string): Promise<SearchResponse> {
  const payload: SearchRequest = { query };

  let response: Response;
  try {
    response = await fetch(`${getApiBaseUrl()}/api/search`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new Error(FRIENDLY_ERROR);
  }

  if (!response.ok) {
    throw new Error(FRIENDLY_ERROR);
  }

  const body = (await response.json()) as SearchResponse;
  return {
    query: body.query,
    total: body.total,
    results: body.results,
  };
}
