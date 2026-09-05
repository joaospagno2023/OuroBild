import {
  apiGet,
  apiPost,
  apiPut,
} from "./api";

export type BuildEnvironmentType =
  | "versioned"
  | "production";

export interface Environment {
  id: string;
  name: string;
  resolver: string;
  root_path: string;
}

export interface CreateEnvironmentRequest {
  id: string;
  name: string;
  resolver: BuildEnvironmentType;
  root_path: string;
}

export interface UpdateEnvironmentRequest {
  name: string;
  resolver: BuildEnvironmentType;
  root_path: string;
}

export async function getEnvironments(): Promise<
  Environment[]
> {
  return apiGet<Environment[]>(
    "/environments",
  );
}

export async function getEnvironment(
  environmentId: string,
): Promise<Environment> {
  return apiGet<Environment>(
    `/environments/${environmentId}`,
  );
}

export async function createEnvironment(
  request: CreateEnvironmentRequest,
): Promise<Environment> {
  return apiPost<
    CreateEnvironmentRequest,
    Environment
  >(
    "/environments",
    request,
  );
}

export async function updateEnvironment(
  environmentId: string,
  request: UpdateEnvironmentRequest,
): Promise<Environment> {
  return apiPut<
    UpdateEnvironmentRequest,
    Environment
  >(
    `/environments/${environmentId}`,
    request,
  );
}