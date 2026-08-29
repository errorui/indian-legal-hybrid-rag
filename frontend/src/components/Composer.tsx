import { FormEvent, KeyboardEvent, useState } from "react";

interface ComposerProps {
  disabled: boolean;
  onSubmit: (query: string) => void;
}

export function Composer({ disabled, onSubmit }: ComposerProps) {
  const [query, setQuery] = useState("");

  function submit() {
    const normalized = query.trim();
    if (!normalized || disabled) return;
    onSubmit(normalized);
    setQuery("");
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    submit();
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submit();
    }
  }

  return (
    <form onSubmit={handleSubmit} className="border-t border-slate-800 bg-slate-950/90 p-4 backdrop-blur md:px-7 md:py-5">
      <div className="mx-auto flex max-w-4xl items-end gap-2 rounded-2xl border border-slate-700 bg-slate-900 p-2 shadow-2xl shadow-black/20 focus-within:border-amber-200/50">
        <label htmlFor="legal-query" className="sr-only">Ask about the Constitution of India</label>
        <textarea
          id="legal-query"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          onKeyDown={handleKeyDown}
          rows={2}
          maxLength={1000}
          disabled={disabled}
          placeholder="Ask about an article, right, power, or constitutional doctrine…"
          className="max-h-40 min-h-12 flex-1 resize-none bg-transparent px-3 py-2 text-sm leading-6 text-slate-100 outline-none placeholder:text-slate-600 disabled:cursor-not-allowed"
        />
        <button
          type="submit"
          disabled={disabled || query.trim().length < 2}
          className="grid size-10 shrink-0 place-items-center rounded-xl bg-amber-200 text-slate-950 transition hover:bg-amber-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-300 disabled:cursor-not-allowed disabled:bg-slate-800 disabled:text-slate-600"
          aria-label="Send question"
        >
          <svg viewBox="0 0 24 24" className="size-4" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="m5 12 14-7-4 14-3-6-7-1Z" strokeLinejoin="round" />
          </svg>
        </button>
      </div>
      <p className="mt-2 text-center text-[11px] text-slate-600">Enter to send · Shift + Enter for a new line</p>
    </form>
  );
}
