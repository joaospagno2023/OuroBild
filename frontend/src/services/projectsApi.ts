import {
  apiDelete,
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

export type SetupPublicationMode =
  | "local"
  | "network";

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

  configuration: string;
  platform: string;

  enabled: boolean;
}

export interface UpdateProjectStatusRequest {
  enabled: boolean;
}


export type CleanupRuleTarget =
  | "file"
  | "directory";

export type CleanupRuleAction =
  | "remove"
  | "preserve";

export interface CleanupRule {
  id: number;
  target: CleanupRuleTarget;
  pattern: string;
  action: CleanupRuleAction;
  recursive: boolean;
  project_id?: string | null;
  description?: string | null;
  priority: number;
  enabled: boolean;
}

export interface CleanupRuleCreateRequest {
  target: CleanupRuleTarget;
  pattern: string;
  action: CleanupRuleAction;
  recursive: boolean;
  description?: string | null;
  enabled: boolean;
}

export interface CleanupRuleUpdateRequest {
  target: CleanupRuleTarget;
  pattern: string;
  action: CleanupRuleAction;
  recursive: boolean;
  description?: string | null;
  enabled: boolean;
}

export interface ExecuteProjectRequest {
  environment_id?: string | null;
  version?: string | null;
  revision?: number | null;
  publication_mode?: SetupPublicationMode;
}

export interface PublishSetupsRequest {
  execution_ids: string[];
  version: string;
  revision: number;
}

export interface PublishSetupProjectResult {
  success: boolean;
  message: string;
  project_id: string;
  source_path?: string | null;
  destination_path?: string | null;
  backup_path?: string | null;
  backup_created: boolean;
  backup_removed: boolean;
  files_copied: number;
  duration_seconds: number;
}

export interface PublishSetupsStartResult {
  batch_id: string;
  success: boolean;
  status: "pending" | "running" | "completed" | "failed";
  message: string;
  execution_ids: string[];
  project_ids: string[];
  source_path?: string | null;
}

export interface SetupPublicationProjectStatus {
  project_id: string;
  execution_id: string;
  status: "waiting" | "publishing" | "success" | "error";
  message: string;
}

export interface SetupPublicationStatusResult {
  batch_id: string;
  status: "pending" | "running" | "completed" | "failed";
  success: boolean | null;
  message: string | null;
  total: number;
  completed: number;
  failed: number;
  progress_percent: number;
  projects: SetupPublicationProjectStatus[];
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

export async function getProjectCleanupRules(
  projectId: string,
): Promise<CleanupRule[]> {
  return apiGet<CleanupRule[]>(
    `/projects/${projectId}/cleanup-rules`,
  );
}

export async function createProjectCleanupRule(
  projectId: string,
  request: CleanupRuleCreateRequest,
): Promise<CleanupRule> {
  return apiPost<
    CleanupRuleCreateRequest,
    CleanupRule
  >(
    `/projects/${projectId}/cleanup-rules`,
    request,
  );
}

export async function updateProjectCleanupRule(
  projectId: string,
  ruleId: number,
  request: CleanupRuleUpdateRequest,
): Promise<CleanupRule> {
  return apiPut<
    CleanupRuleUpdateRequest,
    CleanupRule
  >(
    `/projects/${projectId}/cleanup-rules/${ruleId}`,
    request,
  );
}

export async function deleteProjectCleanupRule(
  projectId: string,
  ruleId: number,
): Promise<void> {
  await apiDelete<void>(
    `/projects/${projectId}/cleanup-rules/${ruleId}`,
  );
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

export async function publishSetups(
  request: PublishSetupsRequest,
): Promise<PublishSetupsStartResult> {
  return apiPost<
    PublishSetupsRequest,
    PublishSetupsStartResult
  >(
    "/publishes/setups/network",
    request,
  );
}

export async function getSetupPublicationStatus(
  batchId: string,
): Promise<SetupPublicationStatusResult> {
  return apiGet<SetupPublicationStatusResult>(
    `/publishes/setups/network/${batchId}`,
  );
}
