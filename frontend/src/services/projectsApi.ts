
/**
 * --------------------------------------------------------------------
 * Projeto : OuroBuild
 * Arquivo : projectsApi.ts
 * Descrição : Operações da API relacionadas aos projetos.
 * --------------------------------------------------------------------
 */

import {
  apiGet,
  apiPost,
} from "./api";

export interface Project {
  id: string;
  name: string;
  description: string;
  type: string;

  solution_path: string;
  project_path: string;

  compilation_target: string;
  compilation_engine: string;

  publish_path: string;
  publish_profile: string | null;

  aip_path: string;
  visualstudio_setup_path: string;

  output_msi: string;
  network_path: string;

  configuration: string;
  platform: string;

  enabled: boolean;
}

export interface ExecutePipelineRequest {
  environment_id: string;
  version?: string | null;
  revision?: number | null;
}

export async function getProjects(): Promise<Project[]> {
  return apiGet<Project[]>("/projects");
}

export async function executeProject(
  projectId: string,
  request: ExecutePipelineRequest,
): Promise<unknown> {
  return apiPost<
    ExecutePipelineRequest,
    unknown
  >(
    `/projects/${encodeURIComponent(projectId)}/execute`,
    request,
  );
}
