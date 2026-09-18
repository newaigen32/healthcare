import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { formatScore } from "@/lib/search";
import type { SearchResult } from "@/types/search";

type SearchResultCardProps = {
  result: SearchResult;
};

export function SearchResultCard({ result }: SearchResultCardProps) {
  const scoreLabel = formatScore(result.score);

  return (
    <Card>
      <CardHeader className="gap-3">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <CardTitle className="text-lg">{result.title}</CardTitle>
          <div className="flex flex-wrap items-center gap-2">
            {result.category ? (
              <Badge variant="secondary">{result.category}</Badge>
            ) : null}
            {scoreLabel ? (
              <Badge variant="outline">Relevance {scoreLabel}</Badge>
            ) : null}
          </div>
        </div>
        <CardDescription>Source: {result.source}</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm leading-6 text-foreground/90">“{result.content}”</p>
      </CardContent>
    </Card>
  );
}
