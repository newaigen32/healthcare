export type SearchResult = {
  id: string;
  title: string;
  content: string;
  source: string;
  category: string | null;
  score: number | null;
};

export type SearchResponse = {
  query: string;
  results: SearchResult[];
};

export type SearchError = {
  message: string;
};
