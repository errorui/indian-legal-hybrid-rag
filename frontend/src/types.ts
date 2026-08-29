export type StepStatus = "complete" | "skipped" | "error";

export interface PipelineStep {
  id: string;
  label: string;
  status: StepStatus;
  duration_ms: number;
  detail: string;
  branch_number?: number | null;
  branch_query?: string | null;
}

export interface ChildMatch {
  child_id: string;
  text: string;
  block_type: string;
  reranker_score: number;
}

export interface ParentSource {
  parent_id: string;
  doc_id: string;
  heading_path: string[];
  text: string;
  rank: number;
  score: number;
  matched_children: ChildMatch[];
}

export interface ChatResult {
  query: string;
  answer: string;
  sub_queries: string[];
  mode: "generated" | "retrieval_only";
  sources: ParentSource[];
  steps: PipelineStep[];
}

export interface Meta {
  corpus_name: string;
  corpus_date: string;
  parent_count: number;
  child_count: number;
  pipeline: string[];
  disclaimer: string;
}

export interface ChatTurn extends ChatResult {
  id: string;
}
