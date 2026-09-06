import {
  apiGet,
  apiPut,
} from "./api";

export type SetupEngine =
  | "advanced_installer"
  | "visual_studio";

export interface StorageConfiguration {
  root_path: string;
}

export interface BuildToolsConfiguration {
  msbuild_path: string;
  advanced_installer_path: string;
  robocopy_path: string;
}

export interface SetupConfiguration {
  engine: SetupEngine;
  output_root: string;
  aip_root: string;
  excluirpastawork: boolean;
}

export interface LoggingConfiguration {
  enabled: boolean;
  path: string;
  level: string;
}

export interface Configuration {
  application_name: string;
  version: string;
  log_level: string;
  base_path: string;
  installer_path: string;
  publish_path: string;
  storage: StorageConfiguration;
  build_tools: BuildToolsConfiguration;
  setup: SetupConfiguration;
  logging: LoggingConfiguration;
}

export interface PathSelectionResponse {
  path: string | null;
}

export async function getConfiguration(): Promise<Configuration> {
  return apiGet<Configuration>(
    "/configuration",
  );
}

export async function updateConfiguration(
  configuration: Configuration,
): Promise<Configuration> {
  return apiPut<
    Configuration,
    Configuration
  >(
    "/configuration",
    configuration,
  );
}

export async function browseFolder(
  initialPath?: string,
): Promise<PathSelectionResponse> {
  const query = initialPath
    ? `?initial_path=${encodeURIComponent(initialPath)}`
    : "";

  return apiGet<PathSelectionResponse>(
    `/configuration/browse-folder${query}`,
  );
}

export async function browseFile(
  initialPath?: string,
): Promise<PathSelectionResponse> {
  const query = initialPath
    ? `?initial_path=${encodeURIComponent(initialPath)}`
    : "";

  return apiGet<PathSelectionResponse>(
    `/configuration/browse-file${query}`,
  );
}