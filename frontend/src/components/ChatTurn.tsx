import type { ChatTurn as ChatTurnType } from "../types";
import { MarkdownContent } from "./MarkdownContent";
import { PipelineTrace } from "./PipelineTrace";
import { SourcesPanel } from "./SourcesPanel";

interface ChatTurnProps {
  turn: ChatTurnType;
}

export function ChatTurn({ turn }: ChatTurnProps) {
  return (
    <article className="space-y-5">
      <div className="ml-auto max-w-2xl rounded-2xl rounded-br-md bg-slate-800 px-4 py-3 text-sm leading-6 text-slate-100">
        {turn.query}
      </div>
      <PipelineTrace steps={turn.steps} subQueries={turn.sub_queries} running={false} />
      <div className="max-w-4xl">
        <div className="mb-2 flex items-center gap-2 text-xs text-slate-500">
          <span className="font-semibold tracking-wide text-amber-200 uppercase">Grounded response</span>
          <span>·</span>
          <span>{turn.mode === "generated" ? "Generated from retrieved sources" : "Retrieval-only mode"}</span>
        </div>
        <MarkdownContent content={turn.answer} />
        <SourcesPanel sources={turn.sources} />
      </div>
    </article>
  );
}
