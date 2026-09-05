import {
  Check,
  ChevronLeft,
  CircleOff,
  Edit,
  FolderCog,
  Loader2,
  Plus,
  RefreshCw,
  X,
} from "lucide-react";
import {
  useEffect,
  useState,
} from "react";

import type {
  FormEvent,
} from "react";

import {
  createProject,
  getProjects,
  updateProject,
  updateProjectStatus,
  type CompilationEngine,
  type CompilationTarget,
  type CreateProjectRequest,
  type Project,
  type ProjectType,
  type UpdateProjectRequest,
} from "../services/projectsApi";

type ProjectsPageMode =
  | "list"
  | "create"
  | "edit";

interface ProjectFormData {
  id: string;
  name: string;
  description: string;
  type: ProjectType;

  solution_path: string;
  project_path: string;

  compilation_target: CompilationTarget;
  compilation_engine: CompilationEngine;

  publish_path: string;
  publish_profile: string;

  aip_path: string;
  visualstudio_setup_path: string;

  output_msi: string;
  network_path: string;

  configuration: string;
  platform: string;

  enabled: boolean;
}

const emptyForm: ProjectFormData = {
  id: "",
  name: "",
  description: "",
  type: "client",

  solution_path: "",
  project_path: "",

  compilation_target: "solution",
  compilation_engine: "msbuild",

  publish_path: "",
  publish_profile: "",

  aip_path: "",
  visualstudio_setup_path: "",

  output_msi: "",
  network_path: "",

  configuration: "Release",
  platform: "AnyCPU",

  enabled: true,
};

function ProjectsPage() {
  const [mode, setMode] =
    useState<ProjectsPageMode>("list");

  const [projects, setProjects] =
    useState<Project[]>([]);

  const [form, setForm] =
    useState<ProjectFormData>(emptyForm);

  const [isLoading, setIsLoading] =
    useState(true);

  const [isRefreshing, setIsRefreshing] =
    useState(false);

  const [isSaving, setIsSaving] =
    useState(false);

  const [
    processingProjectId,
    setProcessingProjectId,
  ] = useState<string | null>(null);

  const [errorMessage, setErrorMessage] =
    useState("");

  const [successMessage, setSuccessMessage] =
    useState("");

  useEffect(() => {
    void loadProjects();
  }, []);

  async function loadProjects(
    refreshing = false,
  ) {
    try {
      setErrorMessage("");

      if (refreshing) {
        setIsRefreshing(true);
      } else {
        setIsLoading(true);
      }

      const result = await getProjects();

      setProjects(result);
    } catch {
      setErrorMessage(
        "Não foi possível carregar os projetos.",
      );
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }

  function clearMessages() {
    setErrorMessage("");
    setSuccessMessage("");
  }

  function openCreate() {
    clearMessages();

    setForm({
      ...emptyForm,
    });

    setMode("create");
  }

  function openEdit(
    project: Project,
  ) {
    clearMessages();

    setForm({
      id: project.id,
      name: project.name,
      description: project.description,
      type: project.type,

      solution_path:
        project.solution_path ?? "",

      project_path:
        project.project_path ?? "",

      compilation_target:
        project.compilation_target,

      compilation_engine:
        project.compilation_engine,

      publish_path:
        project.publish_path,

      publish_profile:
        project.publish_profile ?? "",

      aip_path:
        project.aip_path,

      visualstudio_setup_path:
        project.visualstudio_setup_path ?? "",

      output_msi:
        project.output_msi,

      network_path:
        project.network_path,

      configuration:
        project.configuration,

      platform:
        project.platform,

      enabled:
        project.enabled,
    });

    setMode("edit");
  }

  function backToList() {
    clearMessages();

    setMode("list");
  }

  function updateField<
    K extends keyof ProjectFormData
  >(
    field: K,
    value: ProjectFormData[K],
  ) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function buildCreateRequest(): CreateProjectRequest {
    return {
      id: form.id.trim(),
      name: form.name.trim(),
      description: form.description.trim(),
      type: form.type,

      solution_path:
        form.solution_path.trim() || null,

      project_path:
        form.project_path.trim() || null,

      compilation_target:
        form.compilation_target,

      compilation_engine:
        form.compilation_engine,

      publish_path:
        form.publish_path.trim(),

      publish_profile:
        form.publish_profile.trim() || null,

      aip_path:
        form.aip_path.trim(),

      visualstudio_setup_path:
        form.visualstudio_setup_path.trim() ||
        null,

      output_msi:
        form.output_msi.trim(),

      network_path:
        form.network_path.trim(),

      configuration:
        form.configuration.trim(),

      platform:
        form.platform.trim(),

      enabled:
        form.enabled,
    };
  }

  function buildUpdateRequest(): UpdateProjectRequest {
    return {
      name: form.name.trim(),
      description: form.description.trim(),
      type: form.type,

      solution_path:
        form.solution_path.trim() || null,

      project_path:
        form.project_path.trim() || null,

      compilation_target:
        form.compilation_target,

      compilation_engine:
        form.compilation_engine,

      publish_path:
        form.publish_path.trim(),

      publish_profile:
        form.publish_profile.trim() || null,

      aip_path:
        form.aip_path.trim(),

      visualstudio_setup_path:
        form.visualstudio_setup_path.trim() ||
        null,

      output_msi:
        form.output_msi.trim(),

      network_path:
        form.network_path.trim(),

      configuration:
        form.configuration.trim(),

      platform:
        form.platform.trim(),

      enabled:
        form.enabled,
    };
  }

  function validateForm(): string | null {
    if (
      mode === "create" &&
      !form.id.trim()
    ) {
      return "Informe o identificador do projeto.";
    }

    if (!form.name.trim()) {
      return "Informe o nome do projeto.";
    }

    if (!form.description.trim()) {
      return "Informe a descrição do projeto.";
    }

    if (!form.publish_path.trim()) {
      return "Informe o caminho de publicação.";
    }

    if (!form.aip_path.trim()) {
      return "Informe o arquivo AIP.";
    }

    if (!form.output_msi.trim()) {
      return "Informe o nome do MSI.";
    }

    if (!form.network_path.trim()) {
      return "Informe o caminho de rede.";
    }

    if (!form.configuration.trim()) {
      return "Informe a configuração.";
    }

    if (!form.platform.trim()) {
      return "Informe a plataforma.";
    }

    return null;
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    clearMessages();

    const validationError =
      validateForm();

    if (validationError) {
      setErrorMessage(
        validationError,
      );
      return;
    }

    try {
      setIsSaving(true);

      if (mode === "create") {
        await createProject(
          buildCreateRequest(),
        );

        setSuccessMessage(
          "Projeto cadastrado com sucesso.",
        );
      } else {
        await updateProject(
          form.id,
          buildUpdateRequest(),
        );

        setSuccessMessage(
          "Projeto alterado com sucesso.",
        );
      }

      await loadProjects(true);

      setMode("list");
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "";

      setErrorMessage(
        message ||
          "Não foi possível salvar o projeto.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function handleStatus(
    project: Project,
  ) {
    clearMessages();

    const action =
      project.enabled
        ? "desativar"
        : "ativar";

    const confirmed =
      window.confirm(
        `Deseja ${action} o projeto "${project.name}"?`,
      );

    if (!confirmed) {
      return;
    }

    try {
      setProcessingProjectId(
        project.id,
      );

      const updated =
        await updateProjectStatus(
          project.id,
          {
            enabled:
              !project.enabled,
          },
        );

      setProjects(
        (current) =>
          current.map(
            (item) =>
              item.id === updated.id
                ? updated
                : item,
          ),
      );

      setSuccessMessage(
        updated.enabled
          ? "Projeto ativado com sucesso."
          : "Projeto desativado com sucesso.",
      );
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "";

      setErrorMessage(
        message ||
          "Não foi possível alterar o status do projeto.",
      );
    } finally {
      setProcessingProjectId(
        null,
      );
    }
  }

  function renderMessage() {
    if (errorMessage) {
      return (
        <div className="error-message">
          {errorMessage}
        </div>
      );
    }

    if (successMessage) {
      return (
        <div className="success-message">
          {successMessage}
        </div>
      );
    }

    return null;
  }

  function renderProjectsList() {
    if (isLoading) {
      return (
        <div className="empty-state">
          <Loader2
            size={24}
            className="spin"
          />

          <strong>
            Carregando projetos...
          </strong>
        </div>
      );
    }

    if (projects.length === 0) {
      return (
        <div className="empty-state">
          <FolderCog size={24} />

          <strong>
            Nenhum projeto cadastrado.
          </strong>

          <span>
            Cadastre o primeiro projeto
            para disponibilizá-lo no OuroBuild.
          </span>
        </div>
      );
    }

    return (
      <div className="content-card">
        <div className="card-header">
          <div>
            <h2>
              Projetos cadastrados
            </h2>

            <p>
              Gerencie os projetos utilizados
              pelo processo de build e setup.
            </p>
          </div>

          <button
            className="secondary-button"
            type="button"
            onClick={() =>
              void loadProjects(true)
            }
            disabled={isRefreshing}
          >
            <RefreshCw
              size={14}
              className={
                isRefreshing
                  ? "spin"
                  : undefined
              }
            />

            Atualizar
          </button>
        </div>

        <div className="project-admin-list">
          {projects.map(
            (project) => (
              <div
                className="project-admin-row"
                key={project.id}
              >
                <div className="project-admin-icon">
                  <FolderCog size={19} />
                </div>

                <div className="project-admin-info">
                  <strong>
                    {project.name}
                  </strong>

                  <span>
                    {project.id}
                  </span>
                </div>

                <span
                  className={`project-admin-type ${
                    project.type === "server"
                      ? "project-admin-type-server"
                      : ""
                  }`}
                >
                  {project.type === "server"
                    ? "Servidor"
                    : "Cliente"}
                </span>

                <span
                  className={`status-badge ${
                    project.enabled
                      ? "status-badge-active"
                      : "status-badge-inactive"
                  }`}
                >
                  {project.enabled ? (
                    <>
                      <Check size={12} />
                      Ativo
                    </>
                  ) : (
                    <>
                      <X size={12} />
                      Inativo
                    </>
                  )}
                </span>

                <div className="project-admin-actions">
                  <button
                    className="table-action-button"
                    type="button"
                    onClick={() =>
                      openEdit(project)
                    }
                  >
                    <Edit size={14} />
                    Editar
                  </button>

                  <button
                    className="table-action-button"
                    type="button"
                    onClick={() =>
                      void handleStatus(
                        project,
                      )
                    }
                    disabled={
                      processingProjectId ===
                      project.id
                    }
                  >
                    {processingProjectId ===
                    project.id ? (
                      <Loader2
                        size={14}
                        className="spin"
                      />
                    ) : project.enabled ? (
                      <CircleOff size={14} />
                    ) : (
                      <Check size={14} />
                    )}

                    {project.enabled
                      ? "Desativar"
                      : "Ativar"}
                  </button>
                </div>
              </div>
            ),
          )}
        </div>
      </div>
    );
  }

  function renderProjectForm() {
    const isEdit =
      mode === "edit";

    return (
      <form
        className="content-card"
        onSubmit={handleSubmit}
      >
        <div className="card-header">
          <div>
            <h2>
              {isEdit
                ? "Editar projeto"
                : "Novo projeto"}
            </h2>

            <p>
              {isEdit
                ? "Altere as configurações do projeto."
                : "Cadastre um novo projeto no OuroBuild."}
            </p>
          </div>
        </div>

        <div className="form-grid">
          <div className="form-field">
            <label htmlFor="project-id">
              Identificador
            </label>

            <input
              id="project-id"
              value={form.id}
              disabled={isEdit}
              onChange={(event) =>
                updateField(
                  "id",
                  event.target.value,
                )
              }
              placeholder="ex.: ouronet"
            />
          </div>

          <div className="form-field">
            <label htmlFor="project-name">
              Nome
            </label>

            <input
              id="project-name"
              value={form.name}
              onChange={(event) =>
                updateField(
                  "name",
                  event.target.value,
                )
              }
              placeholder="Nome do projeto"
            />
          </div>

          <div className="form-field">
            <label htmlFor="project-type">
              Tipo
            </label>

            <select
              id="project-type"
              value={form.type}
              onChange={(event) =>
                updateField(
                  "type",
                  event.target.value as ProjectType,
                )
              }
            >
              <option value="client">
                Cliente
              </option>

              <option value="server">
                Servidor
              </option>
            </select>
          </div>

          <div className="form-field">
            <label htmlFor="project-enabled">
              Status
            </label>

            <select
              id="project-enabled"
              value={
                form.enabled
                  ? "active"
                  : "inactive"
              }
              onChange={(event) =>
                updateField(
                  "enabled",
                  event.target.value ===
                    "active",
                )
              }
            >
              <option value="active">
                Ativo
              </option>

              <option value="inactive">
                Inativo
              </option>
            </select>
          </div>

          <div className="form-field form-field-full">
            <label htmlFor="project-description">
              Descrição
            </label>

            <textarea
              id="project-description"
              value={form.description}
              onChange={(event) =>
                updateField(
                  "description",
                  event.target.value,
                )
              }
              placeholder="Descrição do projeto"
            />
          </div>

          <div className="form-field">
            <label htmlFor="solution-path">
              Solution Path
            </label>

            <input
              id="solution-path"
              value={form.solution_path}
              onChange={(event) =>
                updateField(
                  "solution_path",
                  event.target.value,
                )
              }
            />
          </div>

          <div className="form-field">
            <label htmlFor="project-path">
              Project Path
            </label>

            <input
              id="project-path"
              value={form.project_path}
              onChange={(event) =>
                updateField(
                  "project_path",
                  event.target.value,
                )
              }
            />
          </div>

          <div className="form-field">
            <label htmlFor="compilation-target">
              Target de compilação
            </label>

            <select
              id="compilation-target"
              value={
                form.compilation_target
              }
              onChange={(event) =>
                updateField(
                  "compilation_target",
                  event.target.value as CompilationTarget,
                )
              }
            >
              <option value="project">
                Projeto
              </option>

              <option value="solution">
                Solution
              </option>
            </select>
          </div>

          <div className="form-field">
            <label htmlFor="compilation-engine">
              Engine de compilação
            </label>

            <select
              id="compilation-engine"
              value={
                form.compilation_engine
              }
              onChange={(event) =>
                updateField(
                  "compilation_engine",
                  event.target.value as CompilationEngine,
                )
              }
            >
              <option value="dotnet">
                .NET
              </option>

              <option value="msbuild">
                MSBuild
              </option>
            </select>
          </div>

          <div className="form-field">
            <label htmlFor="publish-path">
              Publish Path
            </label>

            <input
              id="publish-path"
              value={form.publish_path}
              onChange={(event) =>
                updateField(
                  "publish_path",
                  event.target.value,
                )
              }
            />
          </div>

          <div className="form-field">
            <label htmlFor="publish-profile">
              Publish Profile
            </label>

            <input
              id="publish-profile"
              value={form.publish_profile}
              onChange={(event) =>
                updateField(
                  "publish_profile",
                  event.target.value,
                )
              }
            />
          </div>

          <div className="form-field">
            <label htmlFor="aip-path">
              AIP Path
            </label>

            <input
              id="aip-path"
              value={form.aip_path}
              onChange={(event) =>
                updateField(
                  "aip_path",
                  event.target.value,
                )
              }
            />
          </div>

          <div className="form-field">
            <label htmlFor="visualstudio-setup-path">
              Visual Studio Setup Path
            </label>

            <input
              id="visualstudio-setup-path"
              value={
                form.visualstudio_setup_path
              }
              onChange={(event) =>
                updateField(
                  "visualstudio_setup_path",
                  event.target.value,
                )
              }
            />
          </div>

          <div className="form-field">
            <label htmlFor="output-msi">
              Output MSI
            </label>

            <input
              id="output-msi"
              value={form.output_msi}
              onChange={(event) =>
                updateField(
                  "output_msi",
                  event.target.value,
                )
              }
            />
          </div>

          <div className="form-field">
            <label htmlFor="network-path">
              Network Path
            </label>

            <input
              id="network-path"
              value={form.network_path}
              onChange={(event) =>
                updateField(
                  "network_path",
                  event.target.value,
                )
              }
            />
          </div>

          <div className="form-field">
            <label htmlFor="configuration">
              Configuration
            </label>

            <input
              id="configuration"
              value={form.configuration}
              onChange={(event) =>
                updateField(
                  "configuration",
                  event.target.value,
                )
              }
            />
          </div>

          <div className="form-field">
            <label htmlFor="platform">
              Platform
            </label>

            <input
              id="platform"
              value={form.platform}
              onChange={(event) =>
                updateField(
                  "platform",
                  event.target.value,
                )
              }
            />
          </div>
        </div>

        <div className="form-actions">
          <button
            className="secondary-button"
            type="button"
            onClick={backToList}
            disabled={isSaving}
          >
            <ChevronLeft size={14} />
            Voltar
          </button>

          <button
            className="primary-button"
            type="submit"
            disabled={isSaving}
          >
            {isSaving ? (
              <Loader2
                size={14}
                className="spin"
              />
            ) : (
              <Plus size={14} />
            )}

            {isEdit
              ? "Salvar alterações"
              : "Cadastrar projeto"}
          </button>
        </div>
      </form>
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
            Projetos
          </h1>

          <p>
            Gerencie os projetos disponíveis
            para build e setup.
          </p>
        </div>

        {mode === "list" && (
          <button
            className="primary-button"
            type="button"
            onClick={openCreate}
          >
            <Plus size={15} />
            Novo projeto
          </button>
        )}
      </div>

      {renderMessage()}

      {mode === "list"
        ? renderProjectsList()
        : renderProjectForm()}
    </section>
  );
}

export default ProjectsPage;