import type { SearchResponse } from "@/types/search";

const DEFAULT_ERROR = "We couldn't complete the search. Please try again.";

function getApiBaseUrl(): string {
  const value = process.env.NEXT_PUBLIC_API_URL;
  if (!value) {
    throw new Error("NEXT_PUBLIC_API_URL is not configured.");
  }
  return value.replace(/\/$/, "");
}

export async function searchDocuments(query: string): Promise<SearchResponse> {
  const response = await fetch(`${getApiBaseUrl()}/api/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }

  return (await response.json()) as SearchResponse;
}

async function readErrorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === "string" && body.detail.trim()) {
      return DEFAULT_ERROR;
    }
  } catch {
    // Ignore JSON parse errors and return the friendly default.
  }
  return DEFAULT_ERROR;
}
