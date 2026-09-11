import {
  Check,
  ChevronLeft,
  CircleOff,
  Edit,
  FolderCog,
  ListChecks,
  Loader2,
  Plus,
  RefreshCw,
  Trash2,
  X,
} from "lucide-react";
import {
  useEffect,
  useState,
} from "react";
import type { FormEvent } from "react";

import {
  createProject,
  createProjectCleanupRule,
  deleteProjectCleanupRule,
  getProjectCleanupRules,
  getProjects,
  updateProject,
  updateProjectCleanupRule,
  updateProjectStatus,
  type CleanupRule,
  type CleanupRuleAction,
  type CleanupRuleTarget,
  type CompilationEngine,
  type CompilationTarget,
  type CreateProjectRequest,
  type Project,
  type ProjectType,
  type UpdateProjectRequest,
} from "../services/projectsApi";

type ProjectsPageMode = "list" | "create" | "edit";
type ProjectConfigurationTab =
  | "data"
  | "build"
  | "setup"
  | "cleanup";

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
  configuration: string;
  platform: string;
  enabled: boolean;
}

interface CleanupRuleFormData {
  target: CleanupRuleTarget;
  pattern: string;
  action: CleanupRuleAction;
  recursive: boolean;
  description: string;
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
  configuration: "Release",
  platform: "AnyCPU",
  enabled: true,
};

const emptyCleanupRuleForm: CleanupRuleFormData = {
  target: "file",
  pattern: "",
  action: "preserve",
  recursive: true,
  description: "",
  enabled: true,
};

const tabButtonBaseStyle = {
  minHeight: "42px",
  padding: "0 16px",
  borderBottom: "2px solid transparent",
  background: "transparent",
  color: "#64748b",
  cursor: "pointer",
  fontSize: "11px",
  fontWeight: 650,
  whiteSpace: "nowrap" as const,
};

function ProjectsPage() {
  const [mode, setMode] = useState<ProjectsPageMode>("list");
  const [activeTab, setActiveTab] =
    useState<ProjectConfigurationTab>("data");
  const [projects, setProjects] = useState<Project[]>([]);
  const [form, setForm] = useState<ProjectFormData>(emptyForm);
  const [cleanupRules, setCleanupRules] = useState<CleanupRule[]>([]);
  const [cleanupForm, setCleanupForm] =
    useState<CleanupRuleFormData>(emptyCleanupRuleForm);
  const [editingCleanupRuleId, setEditingCleanupRuleId] =
    useState<number | null>(null);
  const [isCleanupFormVisible, setIsCleanupFormVisible] =
    useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isCleanupLoading, setIsCleanupLoading] = useState(false);
  const [isCleanupSaving, setIsCleanupSaving] = useState(false);
  const [processingProjectId, setProcessingProjectId] =
    useState<string | null>(null);
  const [processingCleanupRuleId, setProcessingCleanupRuleId] =
    useState<number | null>(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    void loadProjects();
  }, []);

  async function loadProjects(refreshing = false) {
    try {
      setErrorMessage("");
      if (refreshing) {
        setIsRefreshing(true);
      } else {
        setIsLoading(true);
      }
      setProjects(await getProjects());
    } catch {
      setErrorMessage("Não foi possível carregar os projetos.");
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }

  async function loadCleanupRules(projectId: string) {
    try {
      setIsCleanupLoading(true);
      setErrorMessage("");
      setCleanupRules(await getProjectCleanupRules(projectId));
    } catch (error) {
      setCleanupRules([]);
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Não foi possível carregar as exceções de limpeza.",
      );
    } finally {
      setIsCleanupLoading(false);
    }
  }

  function clearMessages() {
    setErrorMessage("");
    setSuccessMessage("");
  }

  function resetCleanupForm() {
    setEditingCleanupRuleId(null);
    setCleanupForm({ ...emptyCleanupRuleForm });
    setIsCleanupFormVisible(false);
  }

  function getProjectFormData(project: Project): ProjectFormData {
    return {
      id: project.id,
      name: project.name,
      description: project.description,
      type: project.type,
      solution_path: project.solution_path ?? "",
      project_path: project.project_path ?? "",
      compilation_target: project.compilation_target,
      compilation_engine: project.compilation_engine,
      publish_path: project.publish_path,
      publish_profile: project.publish_profile ?? "",
      aip_path: project.aip_path,
      visualstudio_setup_path: project.visualstudio_setup_path ?? "",
      output_msi: project.output_msi,
      configuration: project.configuration,
      platform: project.platform,
      enabled: project.enabled,
    };
  }

  function openCreate() {
    clearMessages();
    resetCleanupForm();
    setCleanupRules([]);
    setForm({ ...emptyForm });
    setActiveTab("data");
    setMode("create");
  }

  function openEdit(project: Project) {
    clearMessages();
    resetCleanupForm();
    setForm(getProjectFormData(project));
    setActiveTab("data");
    setMode("edit");
  }

  function openCleanup(project: Project) {
    clearMessages();
    resetCleanupForm();
    setCleanupRules([]);
    setForm(getProjectFormData(project));
    setMode("edit");
    setActiveTab("cleanup");
    void loadCleanupRules(project.id);
  }

  function backToList() {
    clearMessages();
    resetCleanupForm();
    setCleanupRules([]);
    setActiveTab("data");
    setMode("list");
  }

  function updateField<K extends keyof ProjectFormData>(
    field: K,
    value: ProjectFormData[K],
  ) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function openTab(tab: ProjectConfigurationTab) {
    clearMessages();
    setActiveTab(tab);
    if (tab === "cleanup" && mode === "edit" && form.id) {
      void loadCleanupRules(form.id);
    }
  }

  function buildCreateRequest(): CreateProjectRequest {
    return {
      id: form.id.trim(),
      name: form.name.trim(),
      description: form.description.trim(),
      type: form.type,
      solution_path: form.solution_path.trim() || null,
      project_path: form.project_path.trim() || null,
      compilation_target: form.compilation_target,
      compilation_engine: form.compilation_engine,
      publish_path: form.publish_path.trim(),
      publish_profile: form.publish_profile.trim() || null,
      aip_path: form.aip_path.trim(),
      visualstudio_setup_path: form.visualstudio_setup_path.trim() || null,
      output_msi: form.output_msi.trim(),
      configuration: form.configuration.trim(),
      platform: form.platform.trim(),
      enabled: form.enabled,
    };
  }

  function buildUpdateRequest(): UpdateProjectRequest {
    return {
      name: form.name.trim(),
      description: form.description.trim(),
      type: form.type,
      solution_path: form.solution_path.trim() || null,
      project_path: form.project_path.trim() || null,
      compilation_target: form.compilation_target,
      compilation_engine: form.compilation_engine,
      publish_path: form.publish_path.trim(),
      publish_profile: form.publish_profile.trim() || null,
      aip_path: form.aip_path.trim(),
      visualstudio_setup_path: form.visualstudio_setup_path.trim() || null,
      output_msi: form.output_msi.trim(),
      configuration: form.configuration.trim(),
      platform: form.platform.trim(),
      enabled: form.enabled,
    };
  }

  function validateForm(): string | null {
    if (mode === "create" && !form.id.trim()) {
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
    if (!form.configuration.trim()) {
      return "Informe a configuração.";
    }
    if (!form.platform.trim()) {
      return "Informe a plataforma.";
    }
    return null;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearMessages();

    const validationError = validateForm();
    if (validationError) {
      setErrorMessage(validationError);
      return;
    }

    try {
      setIsSaving(true);
      if (mode === "create") {
        await createProject(buildCreateRequest());
        setSuccessMessage("Projeto cadastrado com sucesso.");
      } else {
        await updateProject(form.id, buildUpdateRequest());
        setSuccessMessage("Projeto alterado com sucesso.");
      }

      await loadProjects(true);
      backToList();
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Não foi possível salvar o projeto.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function handleStatus(project: Project) {
    clearMessages();
    const action = project.enabled ? "desativar" : "ativar";
    if (!window.confirm(`Deseja ${action} o projeto "${project.name}"?`)) {
      return;
    }

    try {
      setProcessingProjectId(project.id);
      const updated = await updateProjectStatus(project.id, {
        enabled: !project.enabled,
      });
      setProjects((current) =>
        current.map((item) =>
          item.id === updated.id ? updated : item,
        ),
      );
      setSuccessMessage(
        updated.enabled
          ? "Projeto ativado com sucesso."
          : "Projeto desativado com sucesso.",
      );
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Não foi possível alterar o status do projeto.",
      );
    } finally {
      setProcessingProjectId(null);
    }
  }

  function openNewCleanupRule() {
    clearMessages();
    setEditingCleanupRuleId(null);
    setCleanupForm({ ...emptyCleanupRuleForm });
    setIsCleanupFormVisible(true);
  }

  function openEditCleanupRule(rule: CleanupRule) {
    clearMessages();
    setEditingCleanupRuleId(rule.id);
    setCleanupForm({
      target: rule.target,
      pattern: rule.pattern,
      action: rule.action,
      recursive: rule.recursive,
      description: rule.description ?? "",
      enabled: rule.enabled,
    });
    setIsCleanupFormVisible(true);
  }

  function closeCleanupRuleForm() {
    if (!isCleanupSaving) {
      resetCleanupForm();
    }
  }

  async function saveCleanupRule() {
    if (mode !== "edit" || !form.id) {
      return;
    }

    const pattern = cleanupForm.pattern.trim();
    if (!pattern) {
      setErrorMessage("Informe o padrão da exceção.");
      return;
    }

    try {
      setIsCleanupSaving(true);
      clearMessages();

      const request = {
        target: cleanupForm.target,
        pattern,
        action: cleanupForm.action,
        recursive: cleanupForm.recursive,
        description: cleanupForm.description.trim() || null,
        enabled: cleanupForm.enabled,
      };

      if (editingCleanupRuleId === null) {
        await createProjectCleanupRule(form.id, request);
        setSuccessMessage("Exceção criada com sucesso.");
      } else {
        await updateProjectCleanupRule(
          form.id,
          editingCleanupRuleId,
          request,
        );
        setSuccessMessage("Exceção atualizada com sucesso.");
      }

      resetCleanupForm();
      await loadCleanupRules(form.id);
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Não foi possível salvar a exceção.",
      );
    } finally {
      setIsCleanupSaving(false);
    }
  }

  async function deleteCleanupRule(rule: CleanupRule) {
    if (mode !== "edit" || !form.id) {
      return;
    }

    if (!window.confirm(`Excluir a exceção "${rule.pattern}"?`)) {
      return;
    }

    try {
      setProcessingCleanupRuleId(rule.id);
      clearMessages();
      await deleteProjectCleanupRule(form.id, rule.id);
      setSuccessMessage("Exceção excluída com sucesso.");
      await loadCleanupRules(form.id);
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Não foi possível excluir a exceção.",
      );
    } finally {
      setProcessingCleanupRuleId(null);
    }
  }

  function renderMessage() {
    if (errorMessage) {
      return <div className="error-message">{errorMessage}</div>;
    }
    if (successMessage) {
      return <div className="success-message">{successMessage}</div>;
    }
    return null;
  }

  function renderProjectsList() {
    if (isLoading) {
      return (
        <div className="empty-state">
          <Loader2 size={24} className="spin" />
          <strong>Carregando projetos...</strong>
        </div>
      );
    }

    if (projects.length === 0) {
      return (
        <div className="empty-state">
          <FolderCog size={24} />
          <strong>Nenhum projeto cadastrado.</strong>
          <span>
            Cadastre o primeiro projeto para disponibilizá-lo no OuroBuild.
          </span>
        </div>
      );
    }

    return (
      <div className="content-card">
        <div className="card-header">
          <div>
            <h2>Projetos cadastrados</h2>
            <p>
              Gerencie os projetos utilizados pelo processo de build e setup.
            </p>
          </div>

          <button
            className="secondary-button"
            type="button"
            onClick={() => void loadProjects(true)}
            disabled={isRefreshing}
          >
            <RefreshCw
              size={14}
              className={isRefreshing ? "spin" : undefined}
            />
            Atualizar
          </button>
        </div>

        <div className="project-admin-list">
          {projects.map((project) => (
            <div className="project-admin-row" key={project.id}>
              <div className="project-admin-icon">
                <FolderCog size={19} />
              </div>

              <div className="project-admin-info">
                <strong>{project.name}</strong>
                <span>{project.id}</span>
              </div>

              <span
                className={`project-admin-type ${
                  project.type === "server"
                    ? "project-admin-type-server"
                    : ""
                }`}
              >
                {project.type === "server" ? "Servidor" : "Cliente"}
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
                  onClick={() => openCleanup(project)}
                >
                  <ListChecks size={14} />
                  Exceções
                </button>

                <button
                  className="table-action-button"
                  type="button"
                  onClick={() => openEdit(project)}
                >
                  <Edit size={14} />
                  Editar
                </button>

                <button
                  className="table-action-button"
                  type="button"
                  onClick={() => void handleStatus(project)}
                  disabled={processingProjectId === project.id}
                >
                  {processingProjectId === project.id ? (
                    <Loader2 size={14} className="spin" />
                  ) : project.enabled ? (
                    <CircleOff size={14} />
                  ) : (
                    <Check size={14} />
                  )}
                  {project.enabled ? "Desativar" : "Ativar"}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  function renderTabNavigation(isEdit: boolean) {
    const tabs: Array<{
      id: ProjectConfigurationTab;
      label: string;
      icon: typeof FolderCog;
      disabled?: boolean;
    }> = [
      { id: "data", label: "Dados do projeto", icon: FolderCog },
      { id: "build", label: "Build", icon: Check },
      { id: "setup", label: "Setup", icon: Plus },
      {
        id: "cleanup",
        label: "Exceções",
        icon: ListChecks,
        disabled: !isEdit,
      },
    ];

    return (
      <div
        style={{
          display: "flex",
          alignItems: "stretch",
          gap: "2px",
          overflowX: "auto",
          borderBottom: "1px solid #e2e8f0",
          marginBottom: "22px",
        }}
      >
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              disabled={tab.disabled}
              onClick={() => openTab(tab.id)}
              style={{
                ...tabButtonBaseStyle,
                color: tab.disabled
                  ? "#cbd5e1"
                  : isActive
                    ? "#1d4ed8"
                    : "#64748b",
                borderBottomColor: isActive
                  ? "#2563eb"
                  : "transparent",
                cursor: tab.disabled ? "not-allowed" : "pointer",
              }}
            >
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "7px",
                }}
              >
                <tab.icon size={14} />
                {tab.label}
              </span>
            </button>
          );
        })}
      </div>
    );
  }

  function renderDataTab() {
    return (
      <div className="form-grid">
        <div className="form-field">
          <label htmlFor="project-id">Identificador</label>
          <input
            id="project-id"
            value={form.id}
            disabled={mode === "edit"}
            onChange={(event) => updateField("id", event.target.value)}
            placeholder="ex.: ouronet"
          />
        </div>

        <div className="form-field">
          <label htmlFor="project-name">Nome</label>
          <input
            id="project-name"
            value={form.name}
            onChange={(event) => updateField("name", event.target.value)}
            placeholder="Nome do projeto"
          />
        </div>

        <div className="form-field">
          <label htmlFor="project-type">Tipo</label>
          <select
            id="project-type"
            value={form.type}
            onChange={(event) =>
              updateField("type", event.target.value as ProjectType)
            }
          >
            <option value="client">Cliente</option>
            <option value="server">Servidor</option>
          </select>
        </div>

        <div className="form-field">
          <label htmlFor="project-enabled">Status</label>
          <select
            id="project-enabled"
            value={form.enabled ? "active" : "inactive"}
            onChange={(event) =>
              updateField("enabled", event.target.value === "active")
            }
          >
            <option value="active">Ativo</option>
            <option value="inactive">Inativo</option>
          </select>
        </div>

        <div className="form-field form-field-full">
          <label htmlFor="project-description">Descrição</label>
          <textarea
            id="project-description"
            value={form.description}
            onChange={(event) =>
              updateField("description", event.target.value)
            }
            placeholder="Descrição do projeto"
          />
        </div>

        <div className="form-field">
          <label htmlFor="solution-path">Solution Path</label>
          <input
            id="solution-path"
            value={form.solution_path}
            onChange={(event) =>
              updateField("solution_path", event.target.value)
            }
          />
        </div>

        <div className="form-field">
          <label htmlFor="project-path">Project Path</label>
          <input
            id="project-path"
            value={form.project_path}
            onChange={(event) =>
              updateField("project_path", event.target.value)
            }
          />
        </div>
      </div>
    );
  }

  function renderBuildTab() {
    return (
      <div className="form-grid">
        <div className="form-field">
          <label htmlFor="compilation-target">Target de compilação</label>
          <select
            id="compilation-target"
            value={form.compilation_target}
            onChange={(event) =>
              updateField(
                "compilation_target",
                event.target.value as CompilationTarget,
              )
            }
          >
            <option value="project">Projeto</option>
            <option value="solution">Solution</option>
          </select>
        </div>

        <div className="form-field">
          <label htmlFor="compilation-engine">Engine de compilação</label>
          <select
            id="compilation-engine"
            value={form.compilation_engine}
            onChange={(event) =>
              updateField(
                "compilation_engine",
                event.target.value as CompilationEngine,
              )
            }
          >
            <option value="dotnet">.NET</option>
            <option value="msbuild">MSBuild</option>
          </select>
        </div>

        <div className="form-field">
          <label htmlFor="configuration">Configuration</label>
          <input
            id="configuration"
            value={form.configuration}
            onChange={(event) =>
              updateField("configuration", event.target.value)
            }
          />
        </div>

        <div className="form-field">
          <label htmlFor="platform">Platform</label>
          <input
            id="platform"
            value={form.platform}
            onChange={(event) => updateField("platform", event.target.value)}
          />
        </div>
      </div>
    );
  }

  function renderSetupTab() {
    return (
      <div className="form-grid">
        <div className="form-field">
          <label htmlFor="publish-path">Publish Path</label>
          <input
            id="publish-path"
            value={form.publish_path}
            onChange={(event) =>
              updateField("publish_path", event.target.value)
            }
          />
        </div>

        <div className="form-field">
          <label htmlFor="publish-profile">Publish Profile</label>
          <input
            id="publish-profile"
            value={form.publish_profile}
            onChange={(event) =>
              updateField("publish_profile", event.target.value)
            }
          />
        </div>

        <div className="form-field">
          <label htmlFor="aip-path">AIP Path</label>
          <input
            id="aip-path"
            value={form.aip_path}
            onChange={(event) =>
              updateField("aip_path", event.target.value)
            }
          />
        </div>

        <div className="form-field">
          <label htmlFor="visualstudio-setup-path">
            Visual Studio Setup Path
          </label>
          <input
            id="visualstudio-setup-path"
            value={form.visualstudio_setup_path}
            onChange={(event) =>
              updateField(
                "visualstudio_setup_path",
                event.target.value,
              )
            }
          />
        </div>

        <div className="form-field form-field-full">
          <label htmlFor="output-msi">Output MSI</label>
          <input
            id="output-msi"
            value={form.output_msi}
            onChange={(event) =>
              updateField("output_msi", event.target.value)
            }
          />
        </div>
      </div>
    );
  }

  function renderCleanupTab() {
    return (
      <div>
        <div
          style={{
            padding: "13px 14px",
            border: "1px solid #dbeafe",
            borderRadius: "9px",
            background: "#eff6ff",
            color: "#1e40af",
            fontSize: "11px",
            lineHeight: 1.5,
            marginBottom: "18px",
          }}
        >
          <strong>Como funciona</strong>
          <div style={{ marginTop: "4px" }}>
            As regras específicas deste projeto complementam as regras globais
            de limpeza. Quando houver conflito, a regra específica do projeto
            tem prioridade.
          </div>
        </div>

        <div className="dashboard-grid">
          <div className="content-card">
            <div className="card-header">
              <div>
                <h2>
                  {editingCleanupRuleId === null
                    ? "Nova exceção"
                    : "Editar exceção"}
                </h2>
                <p>
                  Defina o arquivo ou diretório e a ação que deverá ser aplicada.
                </p>
              </div>

              <button
                className="primary-button"
                type="button"
                onClick={openNewCleanupRule}
                disabled={isCleanupSaving}
              >
                <Plus size={14} />
                Nova exceção
              </button>
            </div>

            {!isCleanupFormVisible ? (
              <div className="empty-state compact">
                <ListChecks size={26} />
                <strong>Nenhuma edição em andamento</strong>
                <span>
                  Clique em "Nova exceção" para cadastrar uma regra para este
                  projeto.
                </span>
              </div>
            ) : (
              <div>
                <div className="form-grid">
                  <div className="form-field">
                    <label htmlFor="cleanup-target">Tipo</label>
                    <select
                      id="cleanup-target"
                      value={cleanupForm.target}
                      onChange={(event) =>
                        setCleanupForm((current) => ({
                          ...current,
                          target: event.target.value as CleanupRuleTarget,
                        }))
                      }
                      disabled={isCleanupSaving}
                    >
                      <option value="file">Arquivo</option>
                      <option value="directory">Diretório</option>
                    </select>
                  </div>

                  <div className="form-field">
                    <label htmlFor="cleanup-action">Ação</label>
                    <select
                      id="cleanup-action"
                      value={cleanupForm.action}
                      onChange={(event) =>
                        setCleanupForm((current) => ({
                          ...current,
                          action: event.target.value as CleanupRuleAction,
                        }))
                      }
                      disabled={isCleanupSaving}
                    >
                      <option value="preserve">Preservar</option>
                      <option value="remove">Remover</option>
                    </select>
                  </div>

                  <div className="form-field form-field-full">
                    <label htmlFor="cleanup-pattern">Padrão</label>
                    <input
                      id="cleanup-pattern"
                      value={cleanupForm.pattern}
                      onChange={(event) =>
                        setCleanupForm((current) => ({
                          ...current,
                          pattern: event.target.value,
                        }))
                      }
                      placeholder="ex.: *.config ou Xml"
                      disabled={isCleanupSaving}
                      autoFocus
                    />
                  </div>

                  <div className="form-field form-field-full">
                    <label htmlFor="cleanup-description">Descrição</label>
                    <input
                      id="cleanup-description"
                      value={cleanupForm.description}
                      onChange={(event) =>
                        setCleanupForm((current) => ({
                          ...current,
                          description: event.target.value,
                        }))
                      }
                      placeholder="Explique por que este item deve ser preservado ou removido."
                      disabled={isCleanupSaving}
                    />
                  </div>
                </div>

                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: "18px",
                    marginTop: "16px",
                  }}
                >
                  <label
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                      color: "#334155",
                      fontSize: "11px",
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={cleanupForm.recursive}
                      onChange={(event) =>
                        setCleanupForm((current) => ({
                          ...current,
                          recursive: event.target.checked,
                        }))
                      }
                      disabled={isCleanupSaving}
                    />
                    Aplicar recursivamente
                  </label>

                  <label
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                      color: "#334155",
                      fontSize: "11px",
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={cleanupForm.enabled}
                      onChange={(event) =>
                        setCleanupForm((current) => ({
                          ...current,
                          enabled: event.target.checked,
                        }))
                      }
                      disabled={isCleanupSaving}
                    />
                    Regra ativa
                  </label>
                </div>

                <div className="form-actions">
                  <button
                    className="secondary-button"
                    type="button"
                    onClick={closeCleanupRuleForm}
                    disabled={isCleanupSaving}
                  >
                    <X size={14} />
                    Cancelar
                  </button>

                  <button
                    className="primary-button"
                    type="button"
                    onClick={() => {
                      void saveCleanupRule();
                    }}
                    disabled={isCleanupSaving}
                  >
                    {isCleanupSaving ? (
                      <Loader2 size={14} className="spin" />
                    ) : (
                      <Check size={14} />
                    )}
                    {editingCleanupRuleId === null
                      ? "Adicionar exceção"
                      : "Salvar alteração"}
                  </button>
                </div>
              </div>
            )}
          </div>

          <div className="content-card">
            <div className="card-header">
              <div>
                <h2>Regras específicas do projeto</h2>
                <p>Exceções cadastradas para {form.name}.</p>

                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    alignItems: "center",
                    gap: "8px",
                    marginTop: "8px",
                  }}
                >
                  <span
                    style={{
                      color: "#64748b",
                      fontSize: "9px",
                      fontWeight: 600,
                    }}
                  >
                    Legenda:
                  </span>

                  <span
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "5px",
                      padding: "3px 8px",
                      borderRadius: "999px",
                      background: "#dcfce7",
                      color: "#166534",
                      fontSize: "9px",
                      fontWeight: 700,
                    }}
                  >
                    <span
                      aria-hidden="true"
                      style={{
                        width: "6px",
                        height: "6px",
                        borderRadius: "50%",
                        background: "#22c55e",
                      }}
                    />
                    Preservar
                  </span>

                  <span
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "5px",
                      padding: "3px 8px",
                      borderRadius: "999px",
                      background: "#fee2e2",
                      color: "#b91c1c",
                      fontSize: "9px",
                      fontWeight: 700,
                    }}
                  >
                    <span
                      aria-hidden="true"
                      style={{
                        width: "6px",
                        height: "6px",
                        borderRadius: "50%",
                        background: "#ef4444",
                      }}
                    />
                    Remover
                  </span>
                </div>
              </div>

              <span className="status-badge status-badge-active">
                {cleanupRules.length} {cleanupRules.length === 1 ? "regra" : "regras"}
              </span>
            </div>

            {isCleanupLoading ? (
              <div className="empty-state compact">
                <Loader2 size={22} className="spin" />
                <span>Carregando regras...</span>
              </div>
            ) : cleanupRules.length === 0 ? (
              <div className="empty-state compact">
                <ListChecks size={24} />
                <strong>Nenhuma exceção cadastrada</strong>
                <span>
                  Este projeto utiliza somente as regras globais atualmente.
                </span>
              </div>
            ) : (
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "8px",
                }}
              >
                {cleanupRules.map((rule) => (
                  <div
                    key={rule.id}
                    style={{
                      display: "grid",
                      gridTemplateColumns: "minmax(0, 1fr) auto",
                      gap: "12px",
                      alignItems: "center",
                      padding: "12px",
                      border: "1px solid #e2e8f0",
                      borderRadius: "9px",
                      background: "#ffffff",
                    }}
                  >
                    <div style={{ minWidth: 0 }}>
                      <strong
                        style={{
                          display: "block",
                          color: "#0f172a",
                          fontSize: "11px",
                          overflowWrap: "anywhere",
                        }}
                      >
                        {rule.pattern}
                      </strong>

                      <span
                        style={{
                          display: "block",
                          marginTop: "4px",
                          color: "#64748b",
                          fontSize: "10px",
                        }}
                      >
                        {rule.target === "file" ? "Arquivo" : "Diretório"}
                        {" · "}
                        <span
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            padding: "2px 7px",
                            borderRadius: "999px",
                            background:
                              rule.action === "preserve"
                                ? "#dcfce7"
                                : "#fee2e2",
                            color:
                              rule.action === "preserve"
                                ? "#166534"
                                : "#b91c1c",
                            fontSize: "9px",
                            fontWeight: 700,
                            verticalAlign: "middle",
                          }}
                        >
                          {rule.action === "preserve" ? "Preservar" : "Remover"}
                        </span>
                        {" · "}
                        {rule.recursive ? "Recursivo" : "Não recursivo"}
                        {" · Prioridade "}
                        {rule.priority}
                      </span>

                      {rule.description && (
                        <span
                          style={{
                            display: "block",
                            marginTop: "5px",
                            color: "#94a3b8",
                            fontSize: "10px",
                          }}
                        >
                          {rule.description}
                        </span>
                      )}

                      <span
                        style={{
                          display: "inline-block",
                          marginTop: "7px",
                          padding: "3px 7px",
                          borderRadius: "999px",
                          background: rule.enabled ? "#dcfce7" : "#f1f5f9",
                          color: rule.enabled ? "#166534" : "#64748b",
                          fontSize: "9px",
                          fontWeight: 700,
                        }}
                      >
                        {rule.enabled ? "Ativa" : "Inativa"}
                      </span>
                    </div>

                    <div className="project-admin-actions">
                      <button
                        className="table-action-button"
                        type="button"
                        onClick={() => openEditCleanupRule(rule)}
                        disabled={
                          processingCleanupRuleId !== null || isCleanupSaving
                        }
                      >
                        <Edit size={14} />
                        Editar
                      </button>

                      <button
                        className="table-action-button"
                        type="button"
                        onClick={() => void deleteCleanupRule(rule)}
                        disabled={
                          processingCleanupRuleId !== null || isCleanupSaving
                        }
                        title="Excluir"
                      >
                        {processingCleanupRuleId === rule.id ? (
                          <Loader2 size={14} className="spin" />
                        ) : (
                          <Trash2 size={14} />
                        )}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  function renderProjectForm() {
    const isEdit = mode === "edit";

    return (
      <form className="content-card" onSubmit={handleSubmit}>
        <div className="card-header">
          <div>
            <h2>{isEdit ? "Editar projeto" : "Novo projeto"}</h2>
            <p>
              {isEdit
                ? "Altere as configurações do projeto."
                : "Cadastre um novo projeto no OuroBuild."}
            </p>
          </div>
        </div>

        {renderTabNavigation(isEdit)}

        {activeTab === "data" && renderDataTab()}
        {activeTab === "build" && renderBuildTab()}
        {activeTab === "setup" && renderSetupTab()}
        {activeTab === "cleanup" && renderCleanupTab()}

        <div className="form-actions">
          <button
            className="secondary-button"
            type="button"
            onClick={backToList}
            disabled={isSaving || isCleanupSaving}
          >
            <ChevronLeft size={14} />
            Voltar
          </button>

          <button
            className="primary-button"
            type="submit"
            disabled={isSaving || isCleanupSaving}
          >
            {isSaving ? (
              <Loader2 size={14} className="spin" />
            ) : (
              <Check size={14} />
            )}
            {isEdit ? "Salvar alterações" : "Cadastrar projeto"}
          </button>
        </div>
      </form>
    );
  }

  return (
    <section>
      <div className="page-heading">
        <div>
          <span className="page-eyebrow">ADMINISTRAÇÃO</span>
          <h1>Projetos</h1>
          <p>Gerencie os projetos disponíveis para build e setup.</p>
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

      {mode === "list" ? renderProjectsList() : renderProjectForm()}
    </section>
  );
}

export default ProjectsPage;
