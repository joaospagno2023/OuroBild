import {
  AlertTriangle,
  Check,
  ChevronDown,
  Circle,
  Loader2,
  Rocket,
  Search,
  Server,
  Users,
  X,
} from "lucide-react";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  executeProject,
  getExecution,
  getProjects,
  getSetupPublicationStatus,
  publishSetups,
  type PipelineExecutionResponse,
  type Project,
  type SetupPublicationMode,
  type SetupPublicationStatusResult,
} from "../services/projectsApi";

import {
  getEnvironments,
  type Environment,
} from "../services/environmentsApi";


type ExecutionStatus =
  | "waiting"
  | "pending"
  | "running"
  | "success"
  | "error";


type PublicationStatus =
  | "idle"
  | "publishing"
  | "success"
  | "error";


type ProjectExecution =
  Project & {
    status: ExecutionStatus;
    progress: number;
    executionId: string | null;
    phase: "pipeline" | "setup" | null;
    currentStep: string | null;
    currentStepIndex: number;
    totalSteps: number;
    message: string;
    failedStep: string | null;
  };


const ENVIRONMENT_LABELS: Record<string, string> = {
  production: "Produção",
  versioned: "Versionado",
};


function getEnvironmentLabel(
  environmentId: string,
): string {
  return (
    ENVIRONMENT_LABELS[environmentId] ??
    environmentId
  );
}


function createInitialExecutions(
  projects: Project[],
): ProjectExecution[] {
  return projects.map((project) => ({
    ...project,
    status: "waiting",
    progress: 0,
    executionId: null,
    phase: null,
    currentStep: null,
    currentStepIndex: 0,
    totalSteps: 0,
    message: "Aguardando execução",
    failedStep: null,
  }));
}


function SetupPage() {
  const [
    selectedProjects,
    setSelectedProjects,
  ] = useState<string[]>([]);

  const [
    projects,
    setProjects,
  ] = useState<Project[]>([]);

  const [
    environments,
    setEnvironments,
  ] = useState<Environment[]>([]);

  const [
    isLoading,
    setIsLoading,
  ] = useState(true);

  const [
    loadError,
    setLoadError,
  ] = useState("");

  const [
    environment,
    setEnvironment,
  ] = useState("production");

  const [
    version,
    setVersion,
  ] = useState("1.0.0");

  const [
    revision,
    setRevision,
  ] = useState("0");

  const [
    configuration,
    setConfiguration,
  ] = useState("Release");

  const [
    publicationMode,
    setPublicationMode,
  ] = useState<SetupPublicationMode>(
    "local",
  );

  const [
    executions,
    setExecutions,
  ] = useState<ProjectExecution[]>([]);

  const [
    isGenerating,
    setIsGenerating,
  ] = useState(false);

  const [
    publicationStatus,
    setPublicationStatus,
  ] = useState<PublicationStatus>("idle");

  const [
    publicationMessage,
    setPublicationMessage,
  ] = useState("");

  const [
    publicationCompleted,
    setPublicationCompleted,
  ] = useState(0);

  const [
    publicationFailed,
    setPublicationFailed,
  ] = useState(0);

  const [
    toastMessage,
    setToastMessage,
  ] = useState("");

  const [
    projectSearch,
    setProjectSearch,
  ] = useState("");

  const [
    projectFilter,
    setProjectFilter,
  ] = useState<"all" | "client" | "server">(
    "all",
  );

  useEffect(() => {
    if (!toastMessage) {
      return;
    }

    const timeoutId = window.setTimeout(() => {
      setToastMessage("");
    }, 4000);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [toastMessage]);


  useEffect(() => {
    let isMounted = true;

    async function loadSetupData() {
      try {
        setIsLoading(true);
        setLoadError("");

        const [
          projectResult,
          environmentResult,
        ] = await Promise.all([
          getProjects(),
          getEnvironments(),
        ]);

        if (!isMounted) {
          return;
        }

        const availableProjects =
          projectResult.filter(
            (project) => project.enabled,
          );

        const availableEnvironments =
          environmentResult
            .filter(
              (item) =>
                item.id === "production" ||
                item.id === "versioned",
            )
            .sort(
              (left, right) =>
                left.id === "production"
                  ? -1
                  : right.id === "production"
                    ? 1
                    : 0,
            );

        setProjects(
          availableProjects,
        );

        setEnvironments(
          availableEnvironments,
        );

        setExecutions(
          createInitialExecutions(
            availableProjects,
          ),
        );

        setSelectedProjects([]);

        const productionEnvironment =
          availableEnvironments.find(
            (item) =>
              item.id === "production",
          );

        const defaultEnvironment =
          productionEnvironment ??
          availableEnvironments[0];

        if (defaultEnvironment) {
          setEnvironment(
            defaultEnvironment.id,
          );
        } else {
          setEnvironment("");

          setLoadError(
            "Nenhum ambiente válido foi encontrado.",
          );
        }
      } catch (error) {
        if (!isMounted) {
          return;
        }

        setProjects([]);
        setEnvironments([]);
        setExecutions([]);
        setSelectedProjects([]);
        setEnvironment("");

        setLoadError(
          error instanceof Error
            ? error.message
            : "Não foi possível carregar os projetos e ambientes.",
        );
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void loadSetupData();

    return () => {
      isMounted = false;
    };
  }, []);


  const allSelected =
    projects.length > 0 &&
    selectedProjects.length ===
      projects.length;


  const selectedCount =
    selectedProjects.length;


  const filteredProjects = useMemo(
    () => {
      const search = projectSearch.trim().toLowerCase();

      return projects.filter((project) => {
        const matchesSearch =
          search.length === 0 ||
          project.name.toLowerCase().includes(search) ||
          project.description.toLowerCase().includes(search);

        const matchesFilter =
          projectFilter === "all" ||
          (projectFilter === "client" && project.type === "client") ||
          (projectFilter === "server" && project.type !== "client");

        return matchesSearch && matchesFilter;
      });
    },
    [projects, projectSearch, projectFilter],
  );


  const selectedProjectData =
    useMemo(
      () =>
        projects.filter(
          (project) =>
            selectedProjects.includes(
              project.id,
            ),
        ),
      [
        projects,
        selectedProjects,
      ],
    );


  function toggleProject(
    projectId: string,
  ) {
    setSelectedProjects(
      (current) => {
        if (
          current.includes(
            projectId,
          )
        ) {
          return current.filter(
            (id) =>
              id !== projectId,
          );
        }

        return [
          ...current,
          projectId,
        ];
      },
    );
  }


  function toggleAll() {
    if (allSelected) {
      setSelectedProjects([]);
      return;
    }

    setSelectedProjects(
      projects.map(
        (project) => project.id,
      ),
    );
  }


  async function pollExecution(
    projectId: string,
    executionId: string,
  ): Promise<PipelineExecutionResponse> {
    const pollIntervalMs = 1000;

    while (true) {
      const execution =
        await getExecution(
          executionId,
        );

      updateExecution(
        projectId,
        execution,
      );

      if (
        execution.status ===
          "completed" ||
        execution.status ===
          "failed"
      ) {
        return execution;
      }

      await new Promise(
        (resolve) =>
          window.setTimeout(
            resolve,
            pollIntervalMs,
          ),
      );
    }
  }


  function updateExecution(
    projectId: string,
    execution: PipelineExecutionResponse,
  ) {
    setExecutions(
      (current) =>
        current.map(
          (item) =>
            item.id === projectId
              ? {
                  ...item,
                  status:
                    execution.status ===
                    "pending"
                      ? "pending"
                      : execution.status ===
                          "running"
                        ? "running"
                        : execution.status ===
                            "completed"
                          ? "success"
                          : "error",
                  progress:
                    Math.round(
                      execution.progress_percent,
                    ),
                  executionId:
                    execution.execution_id,
                  phase:
                    execution.phase,
                  currentStep:
                    execution.current_step,
                  currentStepIndex:
                    execution.current_step_index,
                  totalSteps:
                    execution.total_steps,
                  message:
                    execution.message,
                  failedStep:
                    execution.failed_step,
                }
              : item,
        ),
    );
  }


  function closePublicationModal() {
    if (publicationStatus === "publishing") {
      return;
    }

    setPublicationStatus("idle");
    setPublicationMessage("");
    setPublicationCompleted(0);
    setPublicationFailed(0);
  }

  async function pollSetupPublication(
    batchId: string,
  ): Promise<SetupPublicationStatusResult> {
    const pollIntervalMs = 1000;

    while (true) {
      const status = await getSetupPublicationStatus(batchId);

      setPublicationCompleted(status.completed);
      setPublicationFailed(status.failed);

      if (status.message) {
        setPublicationMessage(status.message);
      }

      if (
        status.status === "completed" ||
        status.status === "failed"
      ) {
        return status;
      }

      await new Promise<void>((resolve) => {
        window.setTimeout(resolve, pollIntervalMs);
      });
    }
  }

  async function generateSetups() {
    if (isGenerating) {
      return;
    }

    if (selectedCount === 0) {
      setToastMessage(
        "Selecione pelo menos um projeto para gerar o Setup.",
      );
      return;
    }

    if (!environment) {
      setToastMessage(
        "Selecione um ambiente para continuar.",
      );
      return;
    }

    const trimmedRevision =
      revision.trim();

    if (trimmedRevision === "") {
      setToastMessage(
        "Informe a revisão.",
      );
      return;
    }

    const numericRevision =
      Number(trimmedRevision);

    if (
      !Number.isInteger(
        numericRevision,
      ) ||
      numericRevision < 0
    ) {
      setToastMessage(
        "A revisão deve ser um número inteiro maior ou igual a 0.",
      );
      return;
    }

    if (
      environment === "production" &&
      numericRevision !== 0
    ) {
      setToastMessage(
        "Para o ambiente Produção, a revisão deve ser 0.",
      );
      return;
    }

    if (
      environment === "versioned" &&
      numericRevision <= 0
    ) {
      setToastMessage(
        "Para este ambiente, a revisão deve ser maior que 0.",
      );
      return;
    }

    const parsedRevision =
      numericRevision;

    const trimmedVersion =
      version.trim();

    if (
      publicationMode === "network" &&
      trimmedVersion === ""
    ) {
      setToastMessage(
        "Informe a versão para copiar o Setup para a rede.",
      );
      return;
    }

    const executionIds: string[] = [];
    let allGenerationsSucceeded = true;

    setIsGenerating(true);
    setPublicationStatus("idle");
    setPublicationMessage("");
    setPublicationCompleted(0);
    setPublicationFailed(0);

    const selectedIds = [
      ...selectedProjects,
    ];

    setExecutions(
      (current) =>
        current.map(
          (execution) =>
            selectedIds.includes(
              execution.id,
            )
              ? {
                  ...execution,
                  status: "pending",
                  progress: 0,
                  executionId:
                    null,
                  phase: null,
                  currentStep: null,
                  currentStepIndex:
                    0,
                  totalSteps: 0,
                  message:
                    "Aguardando execução",
                  failedStep: null,
                }
              : execution,
        ),
    );

    try {
      for (
        let index = 0;
        index <
        selectedIds.length;
        index += 1
      ) {
        const projectId =
          selectedIds[index];

        setExecutions(
          (current) =>
            current.map(
              (execution) =>
                execution.id ===
                projectId
                  ? {
                      ...execution,
                      status:
                        "pending",
                      progress: 0,
                      message:
                        "Iniciando execução...",
                    }
                  : execution,
            ),
        );

        try {
          const initialExecution =
            await executeProject(
              projectId,
              {
                environment_id:
                  environment,
                version:
                  version.trim() ||
                  null,
                revision:
                  parsedRevision,
                publication_mode:
                  publicationMode,
              },
            );

          executionIds.push(
            initialExecution.execution_id,
          );

          updateExecution(
            projectId,
            initialExecution,
          );

          const finalExecution =
            await pollExecution(
              projectId,
              initialExecution.execution_id,
            );

          if (
            finalExecution.status !== "completed" ||
            finalExecution.success !== true
          ) {
            allGenerationsSucceeded = false;
          }
        } catch (error) {
          const message =
            error instanceof Error
              ? error.message
              : "Erro durante a execução.";

          allGenerationsSucceeded = false;

          setExecutions(
            (current) =>
              current.map(
                (execution) =>
                  execution.id ===
                  projectId
                    ? {
                        ...execution,
                        status:
                          "error",
                        progress: 0,
                        message,
                      }
                    : execution,
              ),
          );
        }

        const nextProject =
          selectedIds[index + 1];

        if (
          nextProject !==
          undefined
        ) {
          setExecutions(
            (current) =>
              current.map(
                (execution) =>
                  execution.id ===
                  nextProject
                    ? {
                        ...execution,
                        status:
                          "pending",
                        progress: 0,
                        message:
                          "Aguardando execução",
                      }
                    : execution,
              ),
          );
        }
      }

      if (!allGenerationsSucceeded) {
        if (publicationMode === "network") {
          setPublicationStatus("error");
          setPublicationMessage(
            "A geração não foi concluída com sucesso para todos os projetos. Nenhuma cópia para a rede foi iniciada.",
          );
        } else {
          setToastMessage(
            "A geração não foi concluída com sucesso para todos os projetos.",
          );
        }

        return;
      }

      if (publicationMode !== "network") {
        setToastMessage(
          `${selectedIds.length} Setup${
            selectedIds.length === 1 ? "" : "s"
          } gerado${
            selectedIds.length === 1 ? "" : "s"
          } com sucesso.`,
        );
        return;
      }

      setPublicationStatus("publishing");
      setPublicationMessage(
        `Publicando ${selectedIds.length} Setup${
          selectedIds.length === 1 ? "" : "s"
        } na rede...`,
      );
      setPublicationCompleted(0);

      try {
        const publication =
          await publishSetups({
            execution_ids: executionIds,
            version: trimmedVersion,
            revision: parsedRevision,
          });

        if (!publication.success) {
          setPublicationStatus("error");
          setPublicationMessage(
            publication.message,
          );
          return;
        }

        setPublicationMessage(
          publication.message,
        );

        const finalPublication =
          await pollSetupPublication(
            publication.batch_id,
          );

        if (
          finalPublication.status === "completed" &&
          finalPublication.success === true &&
          finalPublication.failed === 0
        ) {
          setPublicationStatus("success");
          setPublicationMessage(
            finalPublication.message ??
              "Todos os Setups foram publicados com sucesso.",
          );
        } else {
          setPublicationStatus("error");
          setPublicationMessage(
            finalPublication.message ??
              "A publicação não foi concluída para todos os projetos.",
          );
        }
      } catch (error) {
        setPublicationStatus("error");
        setPublicationMessage(
          error instanceof Error
            ? error.message
            : "Não foi possível publicar os Setups na rede.",
        );
      }
    } finally {
      setIsGenerating(false);
    }
  }


  return (
    <section>
      {toastMessage && (
        <div
          role="alert"
          style={{
            position: "fixed",
            top: "24px",
            right: "24px",
            zIndex: 9999,
            maxWidth: "420px",
            padding: "14px 18px",
            borderRadius: "10px",
            background: "#dc2626",
            color: "#ffffff",
            boxShadow:
              "0 8px 24px rgba(0, 0, 0, 0.18)",
            fontSize: "14px",
            fontWeight: 600,
          }}
        >
          {toastMessage}
        </div>
      )}

      <div className="page-heading">
        <div>
          <span className="page-eyebrow">
            AUTOMAÇÃO
          </span>

          <h1>
            Geração de Setup
          </h1>

          <p>
            Selecione um ou vários
            projetos para executar a
            geração.
          </p>
        </div>

        <div className="selection-badge">
          {selectedCount === 0
            ? "Nenhum projeto selecionado"
            : `${selectedCount} ${
                selectedCount === 1
                  ? "projeto"
                  : "projetos"
              } selecionado${
                selectedCount === 1
                  ? ""
                  : "s"
              }`}
        </div>
      </div>


      <div
        className="setup-layout setup-layout-horizontal"
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "20px",
          width: "100%",
        }}
      >
        <div
          className="content-card setup-options-card"
          style={{
            width: "100%",
            boxSizing: "border-box",
          }}
        >
          <div className="card-header">
            <div>
              <h2>1. Configuração</h2>
              <p>
                Defina os parâmetros que serão utilizados na geração dos Setups.
              </p>
            </div>
          </div>

          <div
            className="form-grid setup-config-horizontal"
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(5, minmax(0, 1fr))",
              gap: "14px",
            }}
          >
            <label className="form-field">
              <span>Ambiente</span>
              <select
                value={environment}
                onChange={(event) => {
                  const nextEnvironment = event.target.value;
                  setEnvironment(nextEnvironment);

                  if (nextEnvironment === "production") {
                    setRevision("0");
                    return;
                  }

                  if (
                    nextEnvironment === "versioned" &&
                    revision.trim() === "0"
                  ) {
                    setRevision("1");
                  }
                }}
                disabled={
                  isLoading ||
                  isGenerating ||
                  environments.length === 0
                }
              >
                {environments.map((item) => (
                  <option key={item.id} value={item.id}>
                    {getEnvironmentLabel(item.id)}
                  </option>
                ))}
              </select>
            </label>

            <label className="form-field">
              <span>Configuração</span>
              <select
                value={configuration}
                onChange={(event) => setConfiguration(event.target.value)}
                disabled={isGenerating}
              >
                <option value="Release">Release</option>
                <option value="Debug">Debug</option>
              </select>
            </label>

            <label className="form-field">
              <span>Destino do Setup</span>
              <select
                value={publicationMode}
                onChange={(event) =>
                  setPublicationMode(
                    event.target.value as SetupPublicationMode,
                  )
                }
                disabled={isGenerating}
              >
                <option value="local">Somente nesta máquina</option>
                <option value="network">Copiar para rede</option>
              </select>
            </label>

            <label className="form-field">
              <span>Versão</span>
              <input
                value={version}
                onChange={(event) => setVersion(event.target.value)}
                placeholder="Ex.: 1.1.1"
                disabled={isGenerating}
              />
            </label>

            <label className="form-field">
              <span>Revisão</span>
              <input
                value={revision}
                onChange={(event) => setRevision(event.target.value)}
                placeholder="Ex.: 1"
                disabled={isGenerating}
              />
            </label>
          </div>

          <div className="setup-summary">
            <div>
              <span>Projetos</span>
              <strong>{selectedCount}</strong>
            </div>
            <div>
              <span>Ambiente</span>
              <strong>
                {environment
                  ? getEnvironmentLabel(environment)
                  : "—"}
              </strong>
            </div>
            <div>
              <span>Versão</span>
              <strong>{version || "—"}</strong>
            </div>
          </div>
        </div>

        <div
          className="content-card setup-project-card"
          style={{
            width: "100%",
            boxSizing: "border-box",
          }}
        >
          <div className="card-header">
            <div>
              <h2>2. Projetos</h2>
              <p>
                Selecione os projetos que participarão desta geração.
              </p>
            </div>

            <button
              className="secondary-button"
              type="button"
              onClick={toggleAll}
              disabled={isLoading || projects.length === 0}
            >
              {allSelected ? "Desmarcar todos" : "Selecionar todos"}
            </button>
          </div>

          {loadError && <div className="error-message">{loadError}</div>}

          {isLoading ? (
            <div className="empty-state">
              <Loader2 size={24} className="spin" />
              <strong>Carregando projetos...</strong>
            </div>
          ) : (
            <>
              <div
                className="setup-project-toolbar"
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                  marginBottom: "16px",
                  flexWrap: "wrap",
                }}
              >
                <div
                  style={{
                    position: "relative",
                    flex: "1 1 280px",
                    minWidth: "240px",
                  }}
                >
                  <Search
                    size={17}
                    style={{
                      position: "absolute",
                      left: "13px",
                      top: "50%",
                      transform: "translateY(-50%)",
                      color: "#64748b",
                    }}
                  />
                  <input
                    value={projectSearch}
                    onChange={(event) => setProjectSearch(event.target.value)}
                    placeholder="Pesquisar projetos..."
                    aria-label="Pesquisar projetos"
                    style={{
                      width: "100%",
                      boxSizing: "border-box",
                      padding: "11px 14px 11px 40px",
                      border: "1px solid #e2e8f0",
                      borderRadius: "10px",
                      outline: "none",
                      background: "#f8fafc",
                    }}
                  />
                </div>

                <div
                  style={{
                    display: "flex",
                    gap: "8px",
                    flexWrap: "wrap",
                  }}
                >
                  {(
                    [
                      ["all", `Todos (${projects.length})`],
                      ["client", `Cliente (${projects.filter((item) => item.type === "client").length})`],
                      ["server", `Servidor (${projects.filter((item) => item.type !== "client").length})`],
                    ] as const
                  ).map(([value, label]) => (
                    <button
                      key={value}
                      type="button"
                      onClick={() => setProjectFilter(value)}
                      style={{
                        border: "1px solid #e2e8f0",
                        borderRadius: "999px",
                        padding: "9px 13px",
                        background:
                          projectFilter === value ? "#eff6ff" : "#ffffff",
                        color:
                          projectFilter === value ? "#1d4ed8" : "#475569",
                        borderColor:
                          projectFilter === value ? "#bfdbfe" : "#e2e8f0",
                        fontWeight: 600,
                        cursor: "pointer",
                      }}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              {projects.length === 0 ? (
                <div className="empty-state compact">
                  <Rocket size={28} />
                  <strong>Nenhum projeto disponível</strong>
                  <span>Nenhum projeto ativo foi encontrado no cadastro.</span>
                </div>
              ) : filteredProjects.length === 0 ? (
                <div className="empty-state compact">
                  <Search size={28} />
                  <strong>Nenhum projeto encontrado</strong>
                  <span>Ajuste a pesquisa ou o filtro selecionado.</span>
                </div>
              ) : (
                <div
                  className="project-card-grid"
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
                    gap: "12px",
                  }}
                >
                  {filteredProjects.map((project) => {
                    const selected = selectedProjects.includes(project.id);
                    const isClient = project.type === "client";

                    return (
                      <button
                        key={project.id}
                        type="button"
                        onClick={() => toggleProject(project.id)}
                        aria-pressed={selected}
                        style={{
                          minWidth: 0,
                          minHeight: "118px",
                          padding: "15px",
                          textAlign: "left",
                          borderRadius: "12px",
                          border: selected
                            ? "1px solid #93c5fd"
                            : "1px solid #e2e8f0",
                          background: selected ? "#eff6ff" : "#ffffff",
                          boxShadow: selected
                            ? "0 2px 8px rgba(37, 99, 235, 0.10)"
                            : "none",
                          cursor: "pointer",
                          transition: "all 0.15s ease",
                        }}
                      >
                        <div
                          style={{
                            display: "flex",
                            alignItems: "flex-start",
                            justifyContent: "space-between",
                            gap: "10px",
                          }}
                        >
                          <span
                            style={{
                              width: "20px",
                              height: "20px",
                              flex: "0 0 20px",
                              display: "inline-flex",
                              alignItems: "center",
                              justifyContent: "center",
                              borderRadius: "6px",
                              border: selected
                                ? "1px solid #2563eb"
                                : "1px solid #cbd5e1",
                              background: selected ? "#2563eb" : "#ffffff",
                              color: "#ffffff",
                            }}
                          >
                            {selected && <Check size={14} />}
                          </span>

                          {isClient ? (
                            <Users size={17} color={selected ? "#2563eb" : "#64748b"} />
                          ) : (
                            <Server size={17} color={selected ? "#2563eb" : "#64748b"} />
                          )}
                        </div>

                        <strong
                          style={{
                            display: "block",
                            marginTop: "12px",
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                            whiteSpace: "nowrap",
                            color: "#0f172a",
                          }}
                          title={project.name}
                        >
                          {project.name}
                        </strong>

                        <span
                          style={{
                            display: "block",
                            marginTop: "5px",
                            color: "#64748b",
                            fontSize: "12px",
                            lineHeight: 1.35,
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                            whiteSpace: "nowrap",
                          }}
                          title={project.description}
                        >
                          {project.description}
                        </span>

                        <span
                          style={{
                            display: "inline-block",
                            marginTop: "9px",
                            fontSize: "10px",
                            fontWeight: 700,
                            letterSpacing: "0.04em",
                            color: selected ? "#1d4ed8" : "#64748b",
                          }}
                        >
                          {isClient ? "CLIENTE" : "SERVIDOR"}
                        </span>
                      </button>
                    );
                  })}
                </div>
              )}
            </>
          )}
        </div>

        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            padding: "2px 0",
          }}
        >
          <button
            className="primary-button setup-generate-button"
            type="button"
            disabled={isLoading || isGenerating}
            onClick={generateSetups}
            style={{
              minWidth: "240px",
              justifyContent: "center",
            }}
          >
            {isGenerating ? (
              <Loader2 size={18} className="spin" />
            ) : selectedCount === 0 ? (
              <AlertTriangle size={18} />
            ) : (
              <Rocket size={18} />
            )}
            {isGenerating
              ? "Gerando Setups..."
              : selectedCount === 0
                ? "Selecione os projetos"
                : `Gerar ${selectedCount} Setup${selectedCount === 1 ? "" : "s"}`}
          </button>
        </div>
      </div>

      <div
        className="content-card execution-card"
        style={{
          width: "100%",
          maxWidth: "none",
          boxSizing: "border-box",
        }}
      >
        <div className="card-header">
          <div>
            <h2>
              Acompanhamento da geração
            </h2>

            <p>
              Cada projeto possui seu
              próprio status de execução.
            </p>
          </div>
        </div>


        <div className="execution-list">
          {executions
            .filter((execution) =>
              selectedProjects.includes(
                execution.id,
              ),
            )
            .map((execution) => (
              <div
                className="execution-row"
                key={execution.id}
                style={{
                  display: "grid",
                  gridTemplateColumns: "48px minmax(260px, 1.15fr) minmax(320px, 2.8fr) auto",
                  alignItems: "center",
                  columnGap: "18px",
                  rowGap: "10px",
                  width: "100%",
                  boxSizing: "border-box",
                }}
              >
                <div className="execution-status-icon">
                  {execution.status ===
                    "success" && (
                    <CheckCircle />
                  )}

                  {execution.status ===
                    "running" && (
                    <Loader2 className="spin" />
                  )}

                  {execution.status ===
                    "error" && (
                    <X />
                  )}

                  {(execution.status ===
                    "waiting" ||
                    execution.status ===
                      "pending") && (
                    <Circle />
                  )}
                </div>


                <div
                  className="execution-project"
                  style={{
                    minWidth: 0,
                  }}
                >
                  <strong>
                    {execution.name}
                  </strong>

                  <span>
                    {execution.status ===
                      "waiting" &&
                      "Aguardando execução"}

                    {execution.status ===
                      "pending" &&
                      "Aguardando início..."}

                    {execution.status ===
                      "running" &&
                      (execution.currentStep ||
                        execution.message ||
                        "Executando...")}

                    {execution.status ===
                      "success" &&
                      (execution.message ||
                        "Setup gerado com sucesso")}

                    {execution.status ===
                      "error" &&
                      (execution.message ||
                        "Erro durante a geração")}
                  </span>
                </div>


                <div
                  className="progress-area"
                  style={{
                    minWidth: 0,
                    width: "100%",
                    display: "flex",
                    alignItems: "center",
                    gap: "14px",
                  }}
                >
                  <div
                    className="progress-track"
                    style={{
                      flex: 1,
                      minWidth: 0,
                    }}
                  >
                    <div
                      className="progress-value"
                      style={{
                        width: `${execution.progress}%`,
                      }}
                    />
                  </div>

                  <span>
                    {execution.progress}%
                  </span>
                </div>


                {(execution.status ===
                    "running" ||
                  execution.status ===
                    "pending" ||
                  execution.status ===
                    "error") && (
                  <div
                    className="execution-details"
                    style={{
                      gridColumn: "2 / -1",
                      minWidth: 0,
                      marginTop: "-4px",
                    }}
                  >
                    {execution.totalSteps >
                      0 && (
                      <span>
                        Etapa{" "}
                        {
                          execution.currentStepIndex
                        }{" "}
                        de{" "}
                        {
                          execution.totalSteps
                        }
                      </span>
                    )}

                    {execution.phase && (
                      <span>
                        Fase:{" "}
                        {execution.phase ===
                        "pipeline"
                          ? "Pipeline"
                          : "Setup"}
                      </span>
                    )}

                    {execution.failedStep && (
                      <span>
                        Falha:{" "}
                        {
                          execution.failedStep
                        }
                      </span>
                    )}
                  </div>
                )}
              </div>
            ))}


          {selectedCount === 0 && (
            <div className="empty-state compact">
              <Rocket size={28} />

              <strong>
                Nenhum projeto selecionado
              </strong>

              <span>
                Selecione um ou mais
                projetos acima para
                acompanhar a geração.
              </span>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}


function CheckCircle() {
  return <Check size={19} />;
}


export default SetupPage;