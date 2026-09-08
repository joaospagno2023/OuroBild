import { apiGet } from "./api";

export interface PipelineHistoryItem {
  execution_id: string;
  project_id: string;
  project_name: string;
  session_id: string;
  version: string | null;
  success: boolean;
  status: "completed" | "failed";
  message: string;
  started_at: string | null;
  finished_at: string | null;
  elapsed_seconds: number;
  failed_step: string | null;
  steps_count: number;
}

export interface PipelineHistoryDetail extends PipelineHistoryItem {
  output_folder: string | null;
  artifacts: string[];
  steps: Record<string, unknown>[];
  build: Record<string, unknown> | null;
  publish: Record<string, unknown> | null;
}

export async function getHistory(): Promise<PipelineHistoryItem[]> {
  return apiGet<PipelineHistoryItem[]>("/history");
}

export interface PipelineHistoryLogs {
  execution_id: string;
  content: string;
}

export async function getHistoryLogs(
  executionId: string,
): Promise<PipelineHistoryLogs> {
  return apiGet<PipelineHistoryLogs>(
    `/history/${executionId}/logs`,
  );
}

export async function getHistoryDetail(
  executionId: string,
): Promise<PipelineHistoryDetail> {
  return apiGet<PipelineHistoryDetail>(
    `/history/${executionId}`,
  );
}
