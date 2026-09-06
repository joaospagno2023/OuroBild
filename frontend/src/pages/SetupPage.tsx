import {
  Check,
  ChevronDown,
  Circle,
  Loader2,
  Rocket,
  X,
} from "lucide-react";

import {
  useMemo,
  useState,
} from "react";

import {
  executeProject,
  getExecution,
  type PipelineExecutionResponse,
} from "../services/projectsApi";


type Project = {
  id: string;
  name: string;
  description: string;
  type: "client" | "server";
};


type ExecutionStatus =
  | "waiting"
  | "pending"
  | "running"
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


const projects: Project[] = [
  {
    id: "linkpagamento",
    name: "WinService LinkPagamento",
    description:
      "Serviço responsável pelo LinkPagamento",
    type: "client",
  },
  {
    id: "ourocce",
    name: "Ouro Service CCe",
    description:
      "Serviço responsável pelo CCe",
    type: "client",
  },
  {
    id: "wcfcadastro",
    name: "Ouro Net Server Cadastro",
    description:
      "Serviço responsável pelo Server de Cadastro",
    type: "server",
  },
  {
    id: "ouroCustomwebhook",
    name: "Ouro Net Server Custom Web Hook",
    description:
      "Serviço responsável pelo Server de Cadastro",
    type: "server",
  },
  {
    id: "wcfmovimento",
    name: "Ouro Net Server Movimento",
    description:
      "Serviço responsável pelo Server de Movimento",
    type: "server",
  },
];


const initialExecutions: ProjectExecution[] =
  projects.map((project) => ({
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


function SetupPage() {
  const [
    selectedProjects,
    setSelectedProjects,
  ] = useState<string[]>([]);


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
  ] = useState("1");


  const [
    configuration,
    setConfiguration,
  ] = useState("Release");


  const [
    executions,
    setExecutions,
  ] = useState<ProjectExecution[]>(
    initialExecutions,
  );


  const [
    isGenerating,
    setIsGenerating,
  ] = useState(false);


  const allSelected =
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
      [selectedProjects],
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
  ): Promise<void> {
    const pollIntervalMs = 1000;

    while (true) {
      const execution = await getExecution(executionId);

      updateExecution(projectId, execution);

      if (
        execution.status === "completed" ||
        execution.status === "failed"
      ) {
        return;
      }

      await new Promise((resolve) =>
        window.setTimeout(resolve, pollIntervalMs),
      );
    }
  }

  function updateExecution(
    projectId: string,
    execution: PipelineExecutionResponse,
  ) {
    setExecutions((current) =>
      current.map((item) =>
        item.id === projectId
          ? {
              ...item,
              status:
                execution.status === "pending"
                  ? "pending"
                  : execution.status === "running"
                    ? "running"
                    : execution.status === "completed"
                      ? "success"
                      : "error",
              progress: Math.round(
                execution.progress_percent,
              ),
              executionId: execution.execution_id,
              phase: execution.phase,
              currentStep: execution.current_step,
              currentStepIndex:
                execution.current_step_index,
              totalSteps: execution.total_steps,
              message: execution.message,
              failedStep: execution.failed_step,
            }
          : item,
      ),
    );
  }

  async function generateSetups() {
    if (
      selectedCount === 0 ||
      isGenerating
    ) {
      return;
    }

    setIsGenerating(true);

    const selectedIds = [
      ...selectedProjects,
    ];

    setExecutions((current) =>
      current.map((execution) =>
        selectedIds.includes(execution.id)
          ? {
              ...execution,
              status: "pending",
              progress: 0,
              executionId: null,
              phase: null,
              currentStep: null,
              currentStepIndex: 0,
              totalSteps: 0,
              message: "Aguardando execução",
              failedStep: null,
            }
          : execution,
      ),
    );

    let parsedRevision: number | null = null;

    if (revision.trim() !== "") {
      const numericRevision =
        Number(revision);

      if (
        !Number.isInteger(numericRevision) ||
        numericRevision < 0
      ) {
        setExecutions((current) =>
          current.map((execution) =>
            selectedIds.includes(execution.id)
              ? {
                  ...execution,
                  status: "error",
                  progress: 0,
                  message: "Revisão inválida.",
                }
              : execution,
          ),
        );

        setIsGenerating(false);

        return;
      }

      parsedRevision = numericRevision;
    }

    try {
      for (
        let index = 0;
        index < selectedIds.length;
        index += 1
      ) {
        const projectId =
          selectedIds[index];

        setExecutions((current) =>
          current.map((execution) =>
            execution.id === projectId
              ? {
                  ...execution,
                  status: "pending",
                  progress: 0,
                  message: "Iniciando execução...",
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
              },
            );

          updateExecution(
            projectId,
            initialExecution,
          );

          await pollExecution(
            projectId,
            initialExecution.execution_id,
          );
        } catch (error) {
          const message =
            error instanceof Error
              ? error.message
              : "Erro durante a execução.";

          setExecutions((current) =>
            current.map((execution) =>
              execution.id === projectId
                ? {
                    ...execution,
                    status: "error",
                    progress: 0,
                    message,
                  }
                : execution,
            ),
          );
        }

        const nextProject =
          selectedIds[index + 1];

        if (nextProject !== undefined) {
          setExecutions((current) =>
            current.map((execution) =>
              execution.id === nextProject
                ? {
                    ...execution,
                    status: "pending",
                    progress: 0,
                    message: "Aguardando execução",
                  }
                : execution,
            ),
          );
        }
      }
    } finally {
      setIsGenerating(false);
    }
  }


  return (
    <section>
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
            >
              {allSelected
                ? "Desmarcar todos"
                : "Selecionar todos"}
            </button>
          </div>


          <div className="project-list">
            <button
              type="button"
              className={`project-row ${
                allSelected
                  ? "project-row-selected"
                  : ""
              }`}
              onClick={toggleAll}
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
          </div>
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
                onChange={(event) =>
                  setEnvironment(
                    event.target.value,
                  )
                }
              >
                <option value="production">
                  Produção
                </option>

                <option value="Homologacao">
                  Homologação
                </option>

                <option value="Desenvolvimento">
                  Desenvolvimento
                </option>
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
                {environment}
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
              selectedCount === 0 ||
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
                    execution.status === "pending") && (
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

                {(execution.status === "running" ||
                  execution.status === "pending" ||
                  execution.status === "error") && (
                  <div className="execution-details">
                    {execution.totalSteps > 0 && (
                      <span>
                        Etapa {execution.currentStepIndex} de {execution.totalSteps}
                      </span>
                    )}

                    {execution.phase && (
                      <span>
                        Fase: {execution.phase === "pipeline" ? "Pipeline" : "Setup"}
                      </span>
                    )}

                    {execution.failedStep && (
                      <span>
                        Falha: {execution.failedStep}
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