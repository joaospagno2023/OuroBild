import {
  useEffect,
  useState,
} from "react";

import {
  ChevronLeft,
  FolderOpen,
  Save,
  Settings,
} from "lucide-react";

import {
  browseFile,
  browseFolder,
  getConfiguration,
  updateConfiguration,
} from "../services/configurationApi";

import type {
  Configuration,
} from "../services/configurationApi";


type ConfigurationPageMode =
  | "loading"
  | "ready";


function ConfigurationPage() {
  const [
    mode,
    setMode,
  ] = useState<ConfigurationPageMode>(
    "loading",
  );

  const [
    configuration,
    setConfiguration,
  ] = useState<Configuration | null>(
    null,
  );

  const [
    isSaving,
    setIsSaving,
  ] = useState(false);

  const [
    browsingField,
    setBrowsingField,
  ] = useState<string | null>(
    null,
  );

  const [
    message,
    setMessage,
  ] = useState("");

  const [
    error,
    setError,
  ] = useState("");


  useEffect(() => {
    void loadConfiguration();
  }, []);


  async function loadConfiguration() {
    setMode("loading");
    setError("");
    setMessage("");

    try {
      const result =
        await getConfiguration();

      setConfiguration(result);
      setMode("ready");
    } catch {
      setError(
        "Não foi possível carregar as configurações.",
      );
      setMode("ready");
    }
  }


  function updateField<
    T extends keyof Configuration,
  >(
    field: T,
    value: Configuration[T],
  ) {
    setConfiguration(
      (current) => {
        if (!current) {
          return current;
        }

        return {
          ...current,
          [field]: value,
        };
      },
    );
  }


  function updateStorageRootPath(
    value: string,
  ) {
    setConfiguration(
      (current) => {
        if (!current) {
          return current;
        }

        return {
          ...current,
          storage: {
            ...current.storage,
            root_path: value,
          },
        };
      },
    );
  }


  function updateBuildTool(
    field: keyof Configuration["build_tools"],
    value: string,
  ) {
    setConfiguration(
      (current) => {
        if (!current) {
          return current;
        }

        return {
          ...current,
          build_tools: {
            ...current.build_tools,
            [field]: value,
          },
        };
      },
    );
  }


  function updateSetup(
    field: keyof Configuration["setup"],
    value:
      | string
      | boolean,
  ) {
    setConfiguration(
      (current) => {
        if (!current) {
          return current;
        }

        return {
          ...current,
          setup: {
            ...current.setup,
            [field]: value,
          },
        };
      },
    );
  }


  function updateLogging(
    field: keyof Configuration["logging"],
    value:
      | string
      | boolean,
  ) {
    setConfiguration(
      (current) => {
        if (!current) {
          return current;
        }

        return {
          ...current,
          logging: {
            ...current.logging,
            [field]: value,
          },
        };
      },
    );
  }


  async function handleBrowse(
    fieldKey: string,
    currentPath: string,
    type: "folder" | "file",
    onChange: (
      value: string,
    ) => void,
  ) {
    setBrowsingField(fieldKey);
    setError("");
    setMessage("");

    try {
      const result =
        type === "folder"
          ? await browseFolder(
              currentPath,
            )
          : await browseFile(
              currentPath,
            );

      if (result.path) {
        onChange(result.path);
      }
    } catch {
      setError(
        type === "folder"
          ? "Não foi possível abrir o seletor de pastas."
          : "Não foi possível abrir o seletor de arquivos.",
      );
    } finally {
      setBrowsingField(null);
    }
  }


  async function handleSubmit(
    event: React.FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!configuration) {
      return;
    }

    setIsSaving(true);
    setError("");
    setMessage("");

    try {
      const result =
        await updateConfiguration(
          configuration,
        );

      setConfiguration(result);

      setMessage(
        "Configurações salvas com sucesso.",
      );
    } catch {
      setError(
        "Não foi possível salvar as configurações.",
      );
    } finally {
      setIsSaving(false);
    }
  }


  function renderPathField(
    fieldKey: string,
    label: string,
    value: string,
    onChange: (
      value: string,
    ) => void,
    type: "folder" | "file",
  ) {
    const isBrowsing =
      browsingField === fieldKey;

    return (
      <div className="form-field">
        <label>
          {label}
        </label>

        <div
          style={{
            display: "flex",
            gap: "8px",
            width: "100%",
          }}
        >
          <input
            value={value}
            readOnly
            title={value}
            style={{
              flex: 1,
            }}
          />

          <button
            className="secondary-button"
            type="button"
            title={
              type === "folder"
                ? "Buscar pasta"
                : "Buscar arquivo"
            }
            disabled={
              isSaving ||
              browsingField !== null
            }
            onClick={() =>
              void handleBrowse(
                fieldKey,
                value,
                type,
                onChange,
              )
            }
          >
            <FolderOpen
              size={14}
            />

            {isBrowsing
              ? "Abrindo..."
              : type === "folder"
                ? "Buscar pasta"
                : "Buscar arquivo"}
          </button>
        </div>
      </div>
    );
  }


  if (
    mode === "loading"
  ) {
    return (
      <section>
        <div className="page-heading">
          <div>
            <span className="page-eyebrow">
              ADMINISTRAÇÃO
            </span>

            <h1>
              Configurações
            </h1>

            <p>
              Carregando as configurações do
              OuroBuild...
            </p>
          </div>
        </div>
      </section>
    );
  }


  if (!configuration) {
    return (
      <section>
        <div className="page-heading">
          <div>
            <span className="page-eyebrow">
              ADMINISTRAÇÃO
            </span>

            <h1>
              Configurações
            </h1>

            <p>
              Não foi possível carregar a
              configuração.
            </p>
          </div>

          <button
            className="secondary-button"
            type="button"
            onClick={() =>
              void loadConfiguration()
            }
          >
            Tentar novamente
          </button>
        </div>
      </section>
    );
  }


  return (
    <section>
      <div className="page-heading">
        <div>
          <span className="page-eyebrow">
            ADMINISTRAÇÃO
          </span>

          <h1>
            Configurações
          </h1>

          <p>
            Gerencie os parâmetros operacionais
            utilizados pelo OuroBuild.
          </p>
        </div>
      </div>

      {message && (
        <div className="success-message">
          {message}
        </div>
      )}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <form
        onSubmit={handleSubmit}
      >
        <div className="content-card">
          <div className="card-header">
            <div>
              <h2>
                Aplicação
              </h2>

              <p>
                Identificação e nível geral de
                log da aplicação.
              </p>
            </div>

            <Settings
              size={20}
            />
          </div>

          <div className="form-grid">
            <div className="form-field">
              <label>
                Nome da aplicação
              </label>

              <input
                value={
                  configuration.application_name
                }
                onChange={(event) =>
                  updateField(
                    "application_name",
                    event.target.value,
                  )
                }
              />
            </div>

            <div className="form-field">
              <label>
                Versão
              </label>

              <input
                value={
                  configuration.version
                }
                onChange={(event) =>
                  updateField(
                    "version",
                    event.target.value,
                  )
                }
              />
            </div>

            <div className="form-field">
              <label>
                Nível de log
              </label>

              <select
                value={
                  configuration.log_level
                }
                onChange={(event) =>
                  updateField(
                    "log_level",
                    event.target.value,
                  )
                }
              >
                <option value="DEBUG">
                  DEBUG
                </option>

                <option value="INFO">
                  INFO
                </option>

                <option value="WARNING">
                  WARNING
                </option>

                <option value="ERROR">
                  ERROR
                </option>
              </select>
            </div>
          </div>
        </div>

        <div className="content-card">
          <div className="card-header">
            <div>
              <h2>
                Caminhos
              </h2>

              <p>
                Diretórios principais utilizados
                pela aplicação.
              </p>
            </div>
          </div>

          <div className="form-grid">
            {renderPathField(
              "base_path",
              "Base",
              configuration.base_path,
              (value) =>
                updateField(
                  "base_path",
                  value,
                ),
              "folder",
            )}

            {renderPathField(
              "installer_path",
              "Installer",
              configuration.installer_path,
              (value) =>
                updateField(
                  "installer_path",
                  value,
                ),
              "folder",
            )}

            {renderPathField(
              "publish_path",
              "Publish",
              configuration.publish_path,
              (value) =>
                updateField(
                  "publish_path",
                  value,
                ),
              "folder",
            )}

            {renderPathField(
              "storage.root_path",
              "Armazenamento",
              configuration.storage.root_path,
              updateStorageRootPath,
              "folder",
            )}
          </div>
        </div>

        <div className="content-card">
          <div className="card-header">
            <div>
              <h2>
                Ferramentas de Build
              </h2>

              <p>
                Executáveis utilizados durante o
                processo de Build.
              </p>
            </div>
          </div>

          <div className="form-grid">
            {renderPathField(
              "build_tools.msbuild_path",
              "MSBuild",
              configuration.build_tools
                .msbuild_path,
              (value) =>
                updateBuildTool(
                  "msbuild_path",
                  value,
                ),
              "file",
            )}

            {renderPathField(
              "build_tools.advanced_installer_path",
              "Advanced Installer",
              configuration.build_tools
                .advanced_installer_path,
              (value) =>
                updateBuildTool(
                  "advanced_installer_path",
                  value,
                ),
              "file",
            )}

            {renderPathField(
              "build_tools.robocopy_path",
              "Robocopy",
              configuration.build_tools
                .robocopy_path,
              (value) =>
                updateBuildTool(
                  "robocopy_path",
                  value,
                ),
              "file",
            )}
          </div>
        </div>

        <div className="content-card">
          <div className="card-header">
            <div>
              <h2>
                Setup
              </h2>

              <p>
                Configurações utilizadas na geração
                dos instaladores.
              </p>
            </div>
          </div>

          <div className="form-grid">
            <div className="form-field">
              <label>
                Engine
              </label>

              <select
                value={
                  configuration.setup.engine
                }
                onChange={(event) =>
                  updateSetup(
                    "engine",
                    event.target.value,
                  )
                }
              >
                <option value="advanced_installer">
                  Advanced Installer
                </option>

                <option value="visual_studio">
                  Visual Studio
                </option>
              </select>
            </div>

            {renderPathField(
              "setup.output_root",
              "Output",
              configuration.setup.output_root,
              (value) =>
                updateSetup(
                  "output_root",
                  value,
                ),
              "folder",
            )}

            {renderPathField(
              "setup.aip_root",
              "AIP",
              configuration.setup.aip_root,
              (value) =>
                updateSetup(
                  "aip_root",
                  value,
                ),
              "folder",
            )}

            <div className="form-field">
              <label>
                Excluir pasta Work
              </label>

              <select
                value={
                  configuration.setup
                    .excluirpastawork
                    ? "true"
                    : "false"
                }
                onChange={(event) =>
                  updateSetup(
                    "excluirpastawork",
                    event.target.value ===
                      "true",
                  )
                }
              >
                <option value="false">
                  Não
                </option>

                <option value="true">
                  Sim
                </option>
              </select>
            </div>
          </div>
        </div>

        <div className="content-card">
          <div className="card-header">
            <div>
              <h2>
                Logging
              </h2>

              <p>
                Configurações dos arquivos de log.
              </p>
            </div>
          </div>

          <div className="form-grid">
            <div className="form-field">
              <label>
                Habilitado
              </label>

              <select
                value={
                  configuration.logging
                    .enabled
                    ? "true"
                    : "false"
                }
                onChange={(event) =>
                  updateLogging(
                    "enabled",
                    event.target.value ===
                      "true",
                  )
                }
              >
                <option value="true">
                  Sim
                </option>

                <option value="false">
                  Não
                </option>
              </select>
            </div>

            {renderPathField(
              "logging.path",
              "Diretório dos logs",
              configuration.logging.path,
              (value) =>
                updateLogging(
                  "path",
                  value,
                ),
              "folder",
            )}

            <div className="form-field">
              <label>
                Nível
              </label>

              <select
                value={
                  configuration.logging.level
                }
                onChange={(event) =>
                  updateLogging(
                    "level",
                    event.target.value,
                  )
                }
              >
                <option value="DEBUG">
                  DEBUG
                </option>

                <option value="INFO">
                  INFO
                </option>

                <option value="WARNING">
                  WARNING
                </option>

                <option value="ERROR">
                  ERROR
                </option>
              </select>
            </div>
          </div>
        </div>

        <div className="form-actions">
          <button
            className="secondary-button"
            type="button"
            onClick={() =>
              window.history.back()
            }
            disabled={
              isSaving ||
              browsingField !== null
            }
          >
            <ChevronLeft
              size={14}
            />

            Voltar
          </button>

          <button
            className="primary-button"
            type="submit"
            disabled={
              isSaving ||
              browsingField !== null
            }
          >
            <Save
              size={14}
            />

            {isSaving
              ? "Salvando..."
              : "Salvar configurações"}
          </button>
        </div>
      </form>
    </section>
  );
}


export default ConfigurationPage;