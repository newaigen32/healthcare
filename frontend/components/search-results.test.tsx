import React, { act } from "react";
import { createRoot } from "react-dom/client";

import { SearchResults } from "@/components/search-results";

describe("SearchResults", () => {
  it("renders no-results copy", async () => {
    const container = document.createElement("div");
    document.body.appendChild(container);
    const root = createRoot(container);

    await act(async () => {
      root.render(
        <SearchResults
          query="unknown topic"
          total={0}
          results={[]}
          isLoading={false}
          errorMessage={null}
          hasSearched={true}
        />
      );
    });

    expect(container.textContent).toContain("No matching documents were found.");
    root.unmount();
    container.remove();
  });
});
