export interface SearchRequest {
  query: string;
}

export interface SearchResult {
  id: string;
  title: string;
  content: string;
  source: string;
  category?: string;
  score?: number;
}

export interface SearchResponse {
  query: string;
  total: number;
  results: SearchResult[];
}
