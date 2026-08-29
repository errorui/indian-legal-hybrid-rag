import { useCallback, useEffect, useRef, useState } from "react";
import { getMeta, streamChat } from "./api";
import { ChatTurn } from "./components/ChatTurn";
import { Composer } from "./components/Composer";
import { Header } from "./components/Header";
import { PipelineTrace } from "./components/PipelineTrace";
import type { ChatTurn as ChatTurnType, Meta, PipelineStep } from "./types";

export default function App() {
  const [meta, setMeta] = useState<Meta | null>(null);
  const [turns, setTurns] = useState<ChatTurnType[]>([]);
  const [activeSteps, setActiveSteps] = useState<PipelineStep[]>([]);
  const [activeSubQueries, setActiveSubQueries] = useState<string[]>([]);
  const [activeQuery, setActiveQuery] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const controller = new AbortController();
    getMeta(controller.signal)
      .then(setMeta)
      .catch((reason: unknown) => {
        if (controller.signal.aborted) return;
        setError(reason instanceof Error ? reason.message : "Unable to load corpus metadata.");
      });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [turns.length, activeSteps.length, running]);

  const ask = useCallback(async (query: string) => {
    setRunning(true);
    setError(null);
    setActiveSteps([]);
    setActiveSubQueries([]);
    setActiveQuery(query);
    try {
      await streamChat(query, {
        onStep: (step) => setActiveSteps((current) => [...current, step]),
        onBranch: (subQuery) =>
          setActiveSubQueries((current) => [...current, subQuery]),
        onResult: (result) => {
          setTurns((current) => [...current, { ...result, id: crypto.randomUUID() }]);
          setActiveQuery(null);
        },
      });
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The request failed.");
    } finally {
      setRunning(false);
    }
  }, []);

  return (
    <div className="flex min-h-screen flex-col bg-slate-950 text-slate-100">
      <Header meta={meta} ready={Boolean(meta)} />
      <main className="min-h-0 flex-1">
        <section className="flex min-h-[55vh] min-w-0 flex-col lg:max-h-[calc(100vh-68px)]">
          <div className="flex-1 overflow-y-auto px-5 py-8 md:px-10">
            <div className="mx-auto max-w-4xl space-y-12">
              {turns.length === 0 ? (
                <div className="max-w-2xl py-8 md:py-16">
                  <p className="text-xs font-semibold tracking-[0.18em] text-amber-200 uppercase">Evidence before answers</p>
                  <h1 className="mt-4 font-serif text-4xl leading-tight font-semibold text-slate-50 md:text-5xl">
                    Explore the Constitution with every source in view.
                  </h1>
                  <p className="mt-5 max-w-xl text-base leading-7 text-slate-400">
                    Ask a constitutional question. The assistant combines lexical and semantic retrieval, reranks matching child chunks, and opens the unique parent sections for inspection.
                  </p>
                  <div className="mt-8 flex flex-wrap gap-2">
                    {["What does Article 21A guarantee?", "How are Money Bills defined?", "Explain freedom of speech under Article 19"].map((prompt) => (
                      <button key={prompt} disabled={running || !meta} onClick={() => ask(prompt)} className="rounded-full border border-slate-800 bg-slate-900/60 px-3 py-2 text-left text-xs text-slate-400 transition hover:border-slate-700 hover:text-slate-200 disabled:cursor-not-allowed disabled:opacity-50">
                        {prompt}
                      </button>
                    ))}
                  </div>
                </div>
              ) : turns.map((turn) => <ChatTurn key={turn.id} turn={turn} />)}

              {activeQuery ? (
                <article className="space-y-5" aria-live="polite">
                  <div className="ml-auto max-w-2xl rounded-2xl rounded-br-md bg-slate-800 px-4 py-3 text-sm leading-6 text-slate-100">
                    {activeQuery}
                  </div>
                  <PipelineTrace steps={activeSteps} subQueries={activeSubQueries} running={running} />
                </article>
              ) : null}
              {error ? (
                <div role="alert" className="rounded-xl border border-red-400/20 bg-red-400/10 px-4 py-3 text-sm text-red-200">
                  {error}
                </div>
              ) : null}
              <div ref={endRef} />
            </div>
          </div>
          <Composer disabled={running || !meta} onSubmit={ask} />
        </section>
      </main>
      <footer className="border-t border-slate-800 bg-slate-950 px-4 py-2 text-center text-[11px] text-slate-600">
        {meta?.disclaimer ?? "Educational research tool only; not legal advice."}
      </footer>
    </div>
  );
}
