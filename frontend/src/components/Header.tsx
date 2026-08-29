import type { Meta } from "../types";
import { BrandMark } from "./BrandMark";

interface HeaderProps {
  meta: Meta | null;
  ready: boolean;
}

export function Header({ meta, ready }: HeaderProps) {
  return (
    <header className="flex min-h-17 items-center justify-between border-b border-slate-800 bg-slate-950/90 px-5 backdrop-blur md:px-7">
      <div className="flex items-center gap-3">
        <BrandMark />
        <div>
          <p className="font-serif text-base font-semibold tracking-wide text-slate-50">
            Constitution Research Assistant
          </p>
          <p className="text-xs text-slate-400">
            {meta ? `${meta.corpus_name} · as on ${meta.corpus_date}` : "Loading corpus metadata…"}
          </p>
        </div>
      </div>
      <div className="flex items-center gap-2 rounded-full border border-slate-800 px-3 py-1.5 text-xs text-slate-300">
        <span className={`size-2 rounded-full ${ready ? "bg-emerald-400" : "bg-amber-400"}`} />
        {ready ? "Corpus ready" : "Connecting"}
      </div>
    </header>
  );
}
