import { QuestionSearch } from "@/components/question-search";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b bg-white">
        <div className="mx-auto flex h-16 max-w-4xl items-center px-4 sm:px-6">
          <p className="text-sm font-semibold tracking-wide text-slate-900">
            Knowledge Assistant
          </p>
        </div>
      </header>
      <main className="mx-auto max-w-4xl px-4 py-10 sm:px-6 sm:py-14">
        <div className="mb-8 space-y-2">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-900">
            Ask a Question
          </h1>
          <p className="max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">
            Search indexed company documents for procedures, payer rules, and
            previous cases. Version 1 returns the most relevant source documents
            without generating an AI answer.
          </p>
        </div>
        <QuestionSearch />
      </main>
    </div>
  );
}
