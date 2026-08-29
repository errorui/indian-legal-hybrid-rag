import type { ParentSource } from "../types";
import { MarkdownContent } from "./MarkdownContent";

interface SourcesPanelProps {
  sources: ParentSource[];
}

function headingFor(source: ParentSource): string {
  return source.heading_path.join(" › ") || "Untitled constitutional section";
}

export function SourcesPanel({ sources }: SourcesPanelProps) {
  if (sources.length === 0) return null;

  return (
    <section className="mt-8 border-t border-slate-800 pt-5">
      <div className="flex items-baseline justify-between gap-3">
        <h2 className="text-sm font-semibold text-slate-200">Sources</h2>
        <span className="text-xs text-slate-500">{sources.length} unique</span>
      </div>
      <div className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {sources.map((source) => (
          <details key={source.parent_id} className="group min-w-0 rounded-xl border border-slate-800 bg-slate-900/60 open:col-span-full open:border-slate-700">
              <summary className="flex cursor-pointer list-none items-start gap-3 p-3.5 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-300">
                <span className="grid size-7 shrink-0 place-items-center rounded-md bg-slate-800 text-xs font-semibold text-amber-200">
                  {source.rank}
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-sm font-medium text-slate-200">{headingFor(source)}</span>
                  <span className="mt-1 block font-mono text-[11px] text-slate-500">
                    {source.parent_id} · score {source.score.toFixed(3)}
                  </span>
                </span>
                <span className="mt-1 text-slate-500 transition-transform group-open:rotate-180">⌄</span>
              </summary>
              <div className="border-t border-slate-800 px-4 py-4">
                <div className="max-h-96 overflow-y-auto pr-2 selection:bg-amber-200/20">
                  <MarkdownContent content={source.text} compact />
                </div>
                <div className="mt-4 border-t border-slate-800 pt-3">
                  <p className="text-[11px] font-semibold tracking-wider text-slate-500 uppercase">
                    {source.matched_children.length} matched child chunk{source.matched_children.length === 1 ? "" : "s"}
                  </p>
                  {source.matched_children.map((child) => (
                    <p key={child.child_id} className="mt-2 font-mono text-[11px] text-slate-500">
                      {child.child_id} · {child.block_type} · {child.reranker_score.toFixed(3)}
                    </p>
                  ))}
                </div>
              </div>
            </details>
        ))}
      </div>
    </section>
  );
}
