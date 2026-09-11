import {
  AlertTriangle,
  Check,
  ChevronDown,
  Circle,
  Loader2,
  Rocket,
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


      <div className="setup-layout">
        <div className="content-card setup-project-card">
          <div className="card-header">
            <div>
              <h2>
                Projetos
              </h2>

              <p>
                Escolha os projetos que
                participarão desta geração.
              </p>
            </div>

            <button
              className="secondary-button"
              type="button"
              onClick={toggleAll}
              disabled={
                isLoading ||
                projects.length === 0
              }
            >
              {allSelected
                ? "Desmarcar todos"
                : "Selecionar todos"}
            </button>
          </div>


          {loadError && (
            <div className="error-message">
              {loadError}
            </div>
          )}


          {isLoading ? (
            <div className="empty-state">
              <Loader2
                size={24}
                className="spin"
              />

              <strong>
                Carregando projetos...
              </strong>
            </div>
          ) : (
            <div className="project-list">
              <button
                type="button"
                className={`project-row ${
                  allSelected
                    ? "project-row-selected"
                    : ""
                }`}
                onClick={toggleAll}
                disabled={
                  projects.length === 0
                }
              >
                <span
                  className={`checkbox ${
                    allSelected
                      ? "checkbox-selected"
                      : ""
                  }`}
                >
                  {allSelected && (
                    <Check size={15} />
                  )}
                </span>

                <div className="project-row-content">
                  <strong>
                    Todos os projetos
                  </strong>

                  <span>
                    Selecionar todos os
                    projetos disponíveis
                  </span>
                </div>

                <ChevronDown
                  size={18}
                  className="project-chevron"
                />
              </button>


              {projects.map(
                (project) => {
                  const selected =
                    selectedProjects.includes(
                      project.id,
                    );

                  return (
                    <button
                      key={project.id}
                      type="button"
                      className={`project-row ${
                        selected
                          ? "project-row-selected"
                          : ""
                      }`}
                      onClick={() =>
                        toggleProject(
                          project.id,
                        )
                      }
                    >
                      <span
                        className={`checkbox ${
                          selected
                            ? "checkbox-selected"
                            : ""
                        }`}
                      >
                        {selected && (
                          <Check size={15} />
                        )}
                      </span>

                      <div className="project-row-content">
                        <strong>
                          {project.name}
                        </strong>

                        <span>
                          {
                            project.description
                          }
                        </span>
                      </div>

                      <span className="project-type">
                        {project.type ===
                        "client"
                          ? "CLIENT"
                          : "SERVER"}
                      </span>
                    </button>
                  );
                },
              )}


              {!isLoading &&
                projects.length === 0 &&
                !loadError && (
                  <div className="empty-state compact">
                    <Rocket size={28} />

                    <strong>
                      Nenhum projeto disponível
                    </strong>

                    <span>
                      Nenhum projeto ativo foi
                      encontrado no cadastro.
                    </span>
                  </div>
                )}
            </div>
          )}
        </div>


        <div className="content-card setup-options-card">
          <div className="card-header">
            <div>
              <h2>
                Configuração
              </h2>

              <p>
                Parâmetros comuns para os
                projetos selecionados.
              </p>
            </div>
          </div>


          <div className="form-grid">
            <label className="form-field">
              <span>
                Ambiente
              </span>

              <select
                value={environment}
                onChange={(event) => {
                  const nextEnvironment =
                    event.target.value;

                  setEnvironment(
                    nextEnvironment,
                  );

                  if (
                    nextEnvironment ===
                    "production"
                  ) {
                    setRevision("0");
                    return;
                  }

                  if (
                    nextEnvironment ===
                      "versioned" &&
                    revision.trim() ===
                      "0"
                  ) {
                    setRevision("1");
                  }
                }}
                disabled={
                  isLoading ||
                  isGenerating ||
                  environments.length ===
                    0
                }
              >
                {environments.map(
                  (item) => (
                    <option
                      key={item.id}
                      value={item.id}
                    >
                      {getEnvironmentLabel(
                        item.id,
                      )}
                    </option>
                  ),
                )}
              </select>
            </label>


            <label className="form-field">
              <span>
                Configuração
              </span>

              <select
                value={configuration}
                onChange={(event) =>
                  setConfiguration(
                    event.target.value,
                  )
                }
                disabled={
                  isGenerating
                }
              >
                <option value="Release">
                  Release
                </option>

                <option value="Debug">
                  Debug
                </option>
              </select>
            </label>


            <label className="form-field">
              <span>
                Destino do Setup
              </span>

              <select
                value={publicationMode}
                onChange={(event) =>
                  setPublicationMode(
                    event.target.value as SetupPublicationMode,
                  )
                }
                disabled={
                  isGenerating
                }
              >
                <option value="local">
                  Somente nesta máquina
                </option>

                <option value="network">
                  Copiar para rede
                </option>
              </select>
            </label>


            <label className="form-field">
              <span>
                Versão
              </span>

              <input
                value={version}
                onChange={(event) =>
                  setVersion(
                    event.target.value,
                  )
                }
                placeholder="Ex.: 1.1.1"
                disabled={
                  isGenerating
                }
              />
            </label>


            <label className="form-field">
              <span>
                Revisão
              </span>

              <input
                value={revision}
                onChange={(event) =>
                  setRevision(
                    event.target.value,
                  )
                }
                placeholder="Ex.: 1"
                disabled={
                  isGenerating
                }
              />
            </label>
          </div>


          <div className="setup-summary">
            <div>
              <span>
                Projetos
              </span>

              <strong>
                {selectedCount}
              </strong>
            </div>

            <div>
              <span>
                Ambiente
              </span>

              <strong>
                {environment
                  ? getEnvironmentLabel(
                      environment,
                    )
                  : "—"}
              </strong>
            </div>

            <div>
              <span>
                Versão
              </span>

              <strong>
                {version}
              </strong>
            </div>
          </div>


          <button
            className="primary-button setup-generate-button"
            type="button"
            disabled={
              isLoading ||
              isGenerating
            }
            onClick={
              generateSetups
            }
          >
            {isGenerating ? (
              <Loader2
                size={18}
                className="spin"
              />
            ) : selectedCount === 0 ? (
              <AlertTriangle size={18} />
            ) : (
              <Rocket size={18} />
            )}

            {isGenerating
              ? "Gerando Setups..."
              : `Gerar ${selectedCount} Setup${
                  selectedCount === 1
                    ? ""
                    : "s"
                }`}
          </button>


          {selectedProjectData.length >
            0 && (
            <div className="selected-preview">
              <span>
                Projetos selecionados
              </span>

              <div>
                {selectedProjectData.map(
                  (project) => (
                    <span
                      className="selected-chip"
                      key={project.id}
                    >
                      {project.name}

                      <X size={13} />
                    </span>
                  ),
                )}
              </div>
            </div>
          )}
        </div>
      </div>


      {publicationStatus !== "idle" && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="setup-publication-title"
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 10000,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "24px",
            background: "rgba(15, 23, 42, 0.45)",
            backdropFilter: "blur(4px)",
          }}
        >
          <div
            style={{
              width: "min(760px, 100%)",
              maxHeight: "90vh",
              overflowY: "auto",
              borderRadius: "18px",
              background: "#ffffff",
              boxShadow: "0 24px 70px rgba(15, 23, 42, 0.24)",
              padding: "28px",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "flex-start",
                justifyContent: "space-between",
                gap: "20px",
              }}
            >
              <div>
                <h2
                  id="setup-publication-title"
                  style={{
                    margin: 0,
                    fontSize: "24px",
                    lineHeight: 1.2,
                    color: "#0f172a",
                  }}
                >
                  Publicação dos Setups
                </h2>

                <p
                  style={{
                    margin: "8px 0 0",
                    color: "#64748b",
                    fontSize: "14px",
                  }}
                >
                  {publicationStatus === "publishing"
                    ? "A geração terminou. Agora os Setups estão sendo copiados para a rede."
                    : publicationStatus === "success"
                      ? "Todos os Setups foram publicados com sucesso."
                      : "A publicação não foi concluída."}
                </p>
              </div>

              {publicationStatus !== "publishing" && (
                <button
                  type="button"
                  aria-label="Fechar publicação"
                  onClick={closePublicationModal}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    justifyContent: "center",
                    width: "36px",
                    height: "36px",
                    flexShrink: 0,
                    border: "0",
                    borderRadius: "10px",
                    background: "#f1f5f9",
                    color: "#475569",
                    cursor: "pointer",
                  }}
                >
                  <X size={18} />
                </button>
              )}
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "14px",
                marginTop: "24px",
              }}
            >
              <div
                style={{
                  borderRadius: "14px",
                  padding: "18px",
                  background: publicationStatus === "success" ? "#ecfdf5" : "#eff6ff",
                  border: publicationStatus === "success" ? "1px solid #a7f3d0" : "1px solid #bfdbfe",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                  }}
                >
                  <span
                    style={{
                      width: "30px",
                      height: "30px",
                      borderRadius: "50%",
                      display: "inline-flex",
                      alignItems: "center",
                      justifyContent: "center",
                      background: publicationStatus === "success" ? "#10b981" : "#2563eb",
                      color: "#ffffff",
                      fontWeight: 700,
                    }}
                  >
                    {publicationStatus === "success" ? <Check size={16} /> : "1"}
                  </span>

                  <strong
                    style={{
                      color: publicationStatus === "success" ? "#065f46" : "#1e3a8a",
                    }}
                  >
                    Geração dos Setups
                  </strong>
                </div>

                <div
                  style={{
                    marginTop: "12px",
                    color: "#475569",
                    fontSize: "14px",
                  }}
                >
                  {selectedCount} de {selectedCount} Setup{selectedCount === 1 ? "" : "s"} gerado{selectedCount === 1 ? "" : "s"} com sucesso.
                </div>
              </div>

              <div
                style={{
                  borderRadius: "14px",
                  padding: "18px",
                  background: publicationStatus === "error" ? "#fef2f2" : "#eff6ff",
                  border: publicationStatus === "error" ? "1px solid #fecaca" : "1px solid #bfdbfe",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                  }}
                >
                  <span
                    style={{
                      width: "30px",
                      height: "30px",
                      borderRadius: "50%",
                      display: "inline-flex",
                      alignItems: "center",
                      justifyContent: "center",
                      background: publicationStatus === "error" ? "#dc2626" : "#2563eb",
                      color: "#ffffff",
                      fontWeight: 700,
                    }}
                  >
                    2
                  </span>

                  <strong
                    style={{
                      color: publicationStatus === "error" ? "#991b1b" : "#1e3a8a",
                    }}
                  >
                    Copiando para rede
                  </strong>
                </div>

                <div
                  style={{
                    marginTop: "12px",
                    color: "#475569",
                    fontSize: "14px",
                  }}
                >
                  {publicationStatus === "publishing"
                    ? "Publicação em andamento..."
                    : `${publicationCompleted} de ${selectedCount} publicados${
                        publicationFailed > 0
                          ? `; ${publicationFailed} com falha`
                          : ""
                      }.`}
                </div>
              </div>
            </div>

            <div
              style={{
                marginTop: "22px",
                padding: "20px",
                borderRadius: "14px",
                background: "#f8fafc",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: "16px",
                }}
              >
                <strong style={{ color: "#0f172a" }}>
                  {publicationStatus === "publishing"
                    ? "Copiando os Setups..."
                    : publicationStatus === "success"
                      ? "Publicação concluída"
                      : "Publicação interrompida"}
                </strong>

                <span
                  style={{
                    fontWeight: 700,
                    color: publicationStatus === "error" ? "#dc2626" : publicationStatus === "success" ? "#059669" : "#2563eb",
                  }}
                >
                  {publicationStatus === "publishing"
                    ? `${publicationCompleted}/${selectedCount}`
                    : `${publicationCompleted}/${selectedCount}`}
                </span>
              </div>

              <div
                style={{
                  height: "10px",
                  marginTop: "14px",
                  overflow: "hidden",
                  borderRadius: "999px",
                  background: "#e2e8f0",
                }}
              >
                <div
                  style={{
                    width: `${selectedCount > 0 ? Math.min(100, Math.round((publicationCompleted / selectedCount) * 100)) : 0}%`,
                    height: "100%",
                    borderRadius: "inherit",
                    background: publicationStatus === "error" ? "#ef4444" : publicationStatus === "success" ? "#10b981" : "#2563eb",
                    transition: "width 300ms ease",
                  }}
                />
              </div>
            </div>

            <div style={{ marginTop: "18px" }}>
              <strong
                style={{
                  display: "block",
                  marginBottom: "10px",
                  color: "#0f172a",
                }}
              >
                Projetos selecionados
              </strong>

              <div
                style={{
                  display: "grid",
                  gap: "8px",
                }}
              >
                {selectedProjectData.map(
                  (project) => (
                    <div
                      key={project.id}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        gap: "12px",
                        padding: "12px 14px",
                        borderRadius: "10px",
                        background: "#ffffff",
                        border: "1px solid #e2e8f0",
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "10px",
                        }}
                      >
                        <span
                          style={{
                            width: "26px",
                            height: "26px",
                            borderRadius: "50%",
                            display: "inline-flex",
                            alignItems: "center",
                            justifyContent: "center",
                            background: publicationStatus === "success" ? "#dcfce7" : "#dbeafe",
                            color: publicationStatus === "success" ? "#166534" : "#1d4ed8",
                            fontSize: "12px",
                            fontWeight: 700,
                          }}
                        >
                          {publicationStatus === "success" ? <Check size={14} /> : selectedProjectData.indexOf(project) + 1}
                        </span>

                        <div
                          style={{
                            display: "flex",
                            flexDirection: "column",
                            gap: "2px",
                          }}
                        >
                          <strong style={{ color: "#334155" }}>
                            {project.name}
                          </strong>

                          <span
                            style={{
                              color: "#64748b",
                              fontSize: "12px",
                            }}
                          >
                            {publicationStatus === "success"
                              ? "Copiado com sucesso"
                              : publicationStatus === "error"
                                ? "Não foi possível concluir a publicação"
                                : "Aguardando conclusão da cópia..."}
                          </span>
                        </div>
                      </div>
                    </div>
                  ),
                )}
              </div>
            </div>

            <div
              style={{
                marginTop: "18px",
                display: "grid",
                gridTemplateColumns: "repeat(3, 1fr)",
                gap: "10px",
              }}
            >
              {[
                ["Total", selectedCount],
                ["Concluídos", publicationCompleted],
                ["Falhas", publicationFailed],
              ].map(([label, value]) => (
                <div
                  key={label as string}
                  style={{
                    padding: "14px",
                    borderRadius: "12px",
                    background: "#f8fafc",
                    border: "1px solid #e2e8f0",
                  }}
                >
                  <span
                    style={{
                      display: "block",
                      color: "#64748b",
                      fontSize: "12px",
                    }}
                  >
                    {label}
                  </span>

                  <strong
                    style={{
                      display: "block",
                      marginTop: "3px",
                      fontSize: "22px",
                      color: "#0f172a",
                    }}
                  >
                    {value}
                  </strong>
                </div>
              ))}
            </div>

            <div
              style={{
                marginTop: "18px",
                padding: "14px 16px",
                borderRadius: "10px",
                background: publicationStatus === "error" ? "#fef2f2" : "#eff6ff",
                color: publicationStatus === "error" ? "#991b1b" : "#1e3a8a",
                fontSize: "14px",
              }}
            >
              {publicationStatus === "publishing"
                ? "Aguarde enquanto os Setups são copiados para a rede."
                : publicationMessage}
            </div>
          </div>
        </div>
      )}

      <div className="content-card execution-card">
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


                <div className="execution-project">
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


                <div className="progress-area">
                  <div className="progress-track">
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
                  <div className="execution-details">
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