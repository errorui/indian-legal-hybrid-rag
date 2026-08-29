import type { PipelineStep } from "../types";

interface PipelineTraceProps {
  steps: PipelineStep[];
  subQueries: string[];
  running: boolean;
}

interface StepRowProps {
  step: PipelineStep;
}

function StepRow({ step }: StepRowProps) {
  const skipped = step.status === "skipped";

  return (
    <li className="relative flex gap-3 pb-3 last:pb-0">
      <span
        className={`relative z-10 mt-0.5 grid size-5 shrink-0 place-items-center rounded-full border text-[10px] ${
          skipped
            ? "border-slate-600 bg-slate-800 text-slate-400"
            : "border-emerald-400/40 bg-emerald-400/10 text-emerald-300"
        }`}
      >
        {skipped ? "-" : "✓"}
      </span>
      <div className="min-w-0 flex-1">
        <p className="text-xs text-slate-300">{step.label}</p>
        <p className="mt-0.5 text-[11px] leading-4 text-slate-500">
          {step.detail.replace(/^Branch \d+: /, "")} · {step.duration_ms.toLocaleString()} ms
        </p>
      </div>
    </li>
  );
}

export function PipelineTrace({ steps, subQueries, running }: PipelineTraceProps) {
  const fanoutStep = steps.find((step) => step.id === "fanout");
  const generationStep = steps.find((step) => step.id === "generation");
  const stepsByBranch = new Map<number, PipelineStep[]>();

  for (const step of steps) {
    if (step.branch_number == null) continue;
    const branchSteps = stepsByBranch.get(step.branch_number) ?? [];
    branchSteps.push(step);
    stepsByBranch.set(step.branch_number, branchSteps);
  }

  const completedBranches = subQueries.filter((_, index) =>
    stepsByBranch.get(index + 1)?.some((step) => step.label === "Unique parent-context expansion"),
  ).length;
  const summary = running
    ? subQueries.length > 0
      ? `Searching ${subQueries.length} retrieval branch${subQueries.length === 1 ? "" : "es"}`
      : "Planning the search"
    : `Searched ${subQueries.length} retrieval branch${subQueries.length === 1 ? "" : "es"}`;

  return (
    <details
      open={running ? true : undefined}
      className="group max-w-3xl rounded-xl border border-slate-800 bg-slate-900/35"
    >
      <summary className="flex cursor-pointer list-none items-center gap-3 px-4 py-3 text-sm text-slate-400 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-300">
        <span
          className={`size-2 shrink-0 rounded-full ${running ? "animate-pulse bg-amber-300" : "bg-emerald-400"}`}
        />
        <span className="flex-1">{summary}</span>
        <span className="text-xs text-slate-600">
          {subQueries.length > 0 ? `${completedBranches}/${subQueries.length}` : ""}
        </span>
        <span aria-hidden="true" className="text-slate-600 transition-transform group-open:rotate-180">
          ⌄
        </span>
      </summary>

      <div className="border-t border-slate-800 px-4 py-4">
        {fanoutStep ? (
          <ol>
            <StepRow step={fanoutStep} />
          </ol>
        ) : (
          <p className="text-xs text-slate-500">Waiting for query fan-out…</p>
        )}

        <div className="mt-4 space-y-3">
          {subQueries.map((query, index) => {
            const branchNumber = index + 1;
            const branchSteps = stepsByBranch.get(branchNumber);
            return (
              <section
                key={`${branchNumber}-${query}`}
                className="rounded-lg border border-slate-800 bg-slate-950/45 px-3.5 py-3"
              >
                <div className="flex items-start gap-2.5">
                  <span className="grid size-5 shrink-0 place-items-center rounded bg-slate-800 text-[10px] font-semibold text-amber-200">
                    {branchNumber}
                  </span>
                  <div className="min-w-0">
                    <p className="text-[10px] font-semibold tracking-wider text-slate-500 uppercase">
                      Branch question
                    </p>
                    <p className="mt-1 text-xs leading-5 text-slate-300">{query}</p>
                  </div>
                </div>
                {branchSteps && branchSteps.length > 0 ? (
                  <ol className="relative mt-3 border-l border-slate-800 pl-3">
                    {branchSteps.map((step) => (
                      <StepRow key={step.id} step={step} />
                    ))}
                  </ol>
                ) : (
                  <p className="mt-3 pl-7 text-[11px] text-slate-600">Starting branch…</p>
                )}
              </section>
            );
          })}
        </div>

        {generationStep ? (
          <ol className="mt-4">
            <StepRow step={generationStep} />
          </ol>
        ) : null}
      </div>
    </details>
  );
}
