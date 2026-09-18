import type { SearchResponse } from "@/types/search";

const DEFAULT_ERROR = "We couldn't complete the search. Please try again.";
const UNREACHABLE_ERROR =
  "Could not reach the search service. Start the FastAPI backend on http://localhost:8000 and try again.";

function getApiBaseUrl(): string {
  const value = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  return value.replace(/\/$/, "");
}

export async function searchDocuments(query: string): Promise<SearchResponse> {
  let response: Response;
  try {
    response = await fetch(`${getApiBaseUrl()}/api/search`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query }),
    });
  } catch {
    throw new Error(UNREACHABLE_ERROR);
  }

  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }

  return (await response.json()) as SearchResponse;
}

async function readErrorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === "string" && body.detail.trim()) {
      return body.detail;
    }
  } catch {
    // Ignore JSON parse errors and return the friendly default.
  }
  return DEFAULT_ERROR;
}
