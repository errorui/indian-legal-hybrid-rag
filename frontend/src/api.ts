import type { ChatResult, Meta, PipelineStep } from "./types";

type StreamHandlers = {
  onStep: (step: PipelineStep) => void;
  onBranch: (query: string) => void;
  onResult: (result: ChatResult) => void;
};

export async function getMeta(signal?: AbortSignal): Promise<Meta> {
  const response = await fetch("/api/meta", { signal });
  if (!response.ok) {
    throw new Error("The constitutional corpus is not available.");
  }
  return response.json() as Promise<Meta>;
}

function dispatchEventBlock(block: string, handlers: StreamHandlers): void {
  let eventName = "message";
  const dataLines: string[] = [];
  for (const line of block.split("\n")) {
    if (line.startsWith("event:")) eventName = line.slice(6).trim();
    if (line.startsWith("data:")) dataLines.push(line.slice(5).trimStart());
  }
  if (dataLines.length === 0) return;

  const payload = JSON.parse(dataLines.join("\n")) as unknown;
  if (eventName === "step") handlers.onStep(payload as PipelineStep);
  if (eventName === "branch") {
    handlers.onBranch((payload as { query: string }).query);
  }
  if (eventName === "result") handlers.onResult(payload as ChatResult);
  if (eventName === "error") {
    const error = payload as { message?: string };
    throw new Error(error.message || "The retrieval pipeline failed.");
  }
}

export async function streamChat(
  query: string,
  handlers: StreamHandlers,
  signal?: AbortSignal,
): Promise<void> {
  const response = await fetch("/api/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
    signal,
  });
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(body?.detail || "Unable to start the retrieval pipeline.");
  }
  if (!response.body) throw new Error("Streaming is not supported by this browser.");

  const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
  let buffer = "";
  while (true) {
    const { value, done } = await reader.read();
    buffer += value ?? "";
    const blocks = buffer.split("\n\n");
    buffer = blocks.pop() ?? "";
    for (const block of blocks) dispatchEventBlock(block, handlers);
    if (done) break;
  }
  if (buffer.trim()) dispatchEventBlock(buffer, handlers);
}
