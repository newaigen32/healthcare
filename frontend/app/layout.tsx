import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Knowledge Assistant",
  description: "Search company documents indexed in Azure AI Search.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
