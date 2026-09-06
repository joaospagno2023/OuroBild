import {
  apiGet,
  apiPatch,
  apiPost,
  apiPut,
} from "./api";

export type ProjectType =
  | "client"
  | "server";

export type CompilationTarget =
  | "project"
  | "solution";

export type CompilationEngine =
  | "dotnet"
  | "msbuild";

export interface Project {
  id: string;
  name: string;
  description: string;
  type: ProjectType;

  solution_path?: string | null;
  project_path?: string | null;

  compilation_target: CompilationTarget;
  compilation_engine: CompilationEngine;

  publish_path: string;
  publish_profile?: string | null;

  aip_path: string;
  visualstudio_setup_path?: string | null;

  output_msi: string;
  network_path: string;

  configuration: string;
  platform: string;

  enabled: boolean;
}

export interface CreateProjectRequest {
  id: string;
  name: string;
  description: string;
  type: ProjectType;

  solution_path?: string | null;
  project_path?: string | null;

  compilation_target: CompilationTarget;
  compilation_engine: CompilationEngine;

  publish_path: string;
  publish_profile?: string | null;

  aip_path: string;
  visualstudio_setup_path?: string | null;

  output_msi: string;
  network_path: string;

  configuration: string;
  platform: string;

  enabled: boolean;
}

export interface UpdateProjectRequest {
  name: string;
  description: string;
  type: ProjectType;

  solution_path?: string | null;
  project_path?: string | null;

  compilation_target: CompilationTarget;
  compilation_engine: CompilationEngine;

  publish_path: string;
  publish_profile?: string | null;

  aip_path: string;
  visualstudio_setup_path?: string | null;

  output_msi: string;
  network_path: string;

  configuration: string;
  platform: string;

  enabled: boolean;
}

export interface UpdateProjectStatusRequest {
  enabled: boolean;
}

export interface ExecuteProjectRequest {
  environment_id?: string | null;
  version?: string | null;
  revision?: number | null;
}

export interface ExecuteProjectResponse {
  execution_id: string;
  project_id: string;
  status: "pending" | "running" | "completed" | "failed";
  phase: "pipeline" | "setup" | null;
  current_step: string | null;
  current_step_index: number;
  total_steps: number;
  progress_percent: number;
  message: string;
  created_at?: string | null;
  started_at?: string | null;
  finished_at?: string | null;
  elapsed_seconds?: number | null;
  success?: boolean | null;
  failed_step?: string | null;
}

export async function getProjects(): Promise<Project[]> {
  return apiGet<Project[]>("/projects");
}

export async function getProject(
  projectId: string,
): Promise<Project> {
  return apiGet<Project>(
    `/projects/${projectId}`,
  );
}

export async function createProject(
  request: CreateProjectRequest,
): Promise<Project> {
  return apiPost<
    CreateProjectRequest,
    Project
  >(
    "/projects",
    request,
  );
}

export async function updateProject(
  projectId: string,
  request: UpdateProjectRequest,
): Promise<Project> {
  return apiPut<
    UpdateProjectRequest,
    Project
  >(
    `/projects/${projectId}`,
    request,
  );
}

export async function updateProjectStatus(
  projectId: string,
  request: UpdateProjectStatusRequest,
): Promise<Project> {
  return apiPatch<
    UpdateProjectStatusRequest,
    Project
  >(
    `/projects/${projectId}/status`,
    request,
  );
}

export interface PipelineExecutionResponse {
  execution_id: string;
  project_id: string;
  status: "pending" | "running" | "completed" | "failed";
  phase: "pipeline" | "setup" | null;
  current_step: string | null;
  current_step_index: number;
  total_steps: number;
  progress_percent: number;
  message: string;
  created_at: string | null;
  started_at: string | null;
  finished_at: string | null;
  elapsed_seconds: number | null;
  success: boolean | null;
  failed_step: string | null;
}
export async function executeProject(
  projectId: string,
  request: ExecuteProjectRequest,
): Promise<PipelineExecutionResponse> {
  return apiPost<
    ExecuteProjectRequest,
    PipelineExecutionResponse
  >(
    `/projects/${projectId}/execute`,
    request,
  );
}
export async function getExecution(
  executionId: string,
): Promise<PipelineExecutionResponse> {
  return apiGet<PipelineExecutionResponse>(
    `/executions/${executionId}`,
  );
}
