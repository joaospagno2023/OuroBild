import {
  ArrowLeft,
  Check,
  Edit3,
  FolderCog,
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
import {
  useNavigate,
  useParams,
} from "react-router-dom";

import {
  createProjectCleanupRule,
  deleteProjectCleanupRule,
  getProject,
  getProjectCleanupRules,
  updateProjectCleanupRule,
  type CleanupRule,
  type CleanupRuleAction,
  type CleanupRuleTarget,
  type Project,
} from "../services/projectsApi";

type RuleFormData = {
  target: CleanupRuleTarget;
  pattern: string;
  action: CleanupRuleAction;
  recursive: boolean;
  description: string;
  enabled: boolean;
};

const emptyForm: RuleFormData = {
  target: "file",
  pattern: "",
  action: "preserve",
  recursive: true,
  description: "",
  enabled: true,
};

function CleanupRulesPage() {
  const navigate = useNavigate();
  const { projectId } = useParams<{ projectId: string }>();

  const [project, setProject] = useState<Project | null>(null);
  const [rules, setRules] = useState<CleanupRule[]>([]);
  const [form, setForm] = useState<RuleFormData>({ ...emptyForm });
  const [editingRuleId, setEditingRuleId] = useState<number | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingRules, setIsLoadingRules] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [processingRuleId, setProcessingRuleId] = useState<number | null>(null);

  const [isFormVisible, setIsFormVisible] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    if (!projectId) {
      setErrorMessage("Projeto não informado.");
      setIsLoading(false);
      return;
    }

    void loadData(projectId);
  }, [projectId]);

  async function loadData(id: string) {
    try {
      setIsLoading(true);
      setErrorMessage("");

      const projectResult = await getProject(id);
      setProject(projectResult);

      await loadRules(id);
    } catch (error) {
      setProject(null);
      setRules([]);
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Não foi possível carregar o projeto.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  async function loadRules(id: string) {
    try {
      setIsLoadingRules(true);
      const result = await getProjectCleanupRules(id);
      setRules(result);
    } catch (error) {
      setRules([]);
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Não foi possível carregar as exceções de limpeza.",
      );
    } finally {
      setIsLoadingRules(false);
    }
  }

  function clearMessages() {
    setErrorMessage("");
    setSuccessMessage("");
  }

  function openCreate() {
    clearMessages();
    setEditingRuleId(null);
    setForm({ ...emptyForm });
    setIsFormVisible(true);
  }

  function openEdit(rule: CleanupRule) {
    clearMessages();
    setEditingRuleId(rule.id);
    setForm({
      target: rule.target,
      pattern: rule.pattern,
      action: rule.action,
      recursive: rule.recursive,
      description: rule.description ?? "",
      enabled: rule.enabled,
    });
    setIsFormVisible(true);
  }

  function closeForm() {
    if (isSaving) {
      return;
    }

    setEditingRuleId(null);
    setForm({ ...emptyForm });
    setIsFormVisible(false);
  }

  async function saveRule() {
    if (!projectId) {
      return;
    }

    const pattern = form.pattern.trim();

    if (!pattern) {
      setErrorMessage("Informe o padrão da exceção.");
      return;
    }

    try {
      setIsSaving(true);
      clearMessages();

      const request = {
        target: form.target,
        pattern,
        action: form.action,
        recursive: form.recursive,
        description: form.description.trim() || null,
        enabled: form.enabled,
      };

      if (editingRuleId === null) {
        await createProjectCleanupRule(projectId, request);
        setSuccessMessage("Exceção criada com sucesso.");
      } else {
        await updateProjectCleanupRule(
          projectId,
          editingRuleId,
          request,
        );
        setSuccessMessage("Exceção atualizada com sucesso.");
      }

      closeForm();
      await loadRules(projectId);
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Não foi possível salvar a exceção.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function deleteRule(rule: CleanupRule) {
    if (!projectId) {
      return;
    }

    const confirmed = window.confirm(
      `Excluir a exceção "${rule.pattern}"?`,
    );

    if (!confirmed) {
      return;
    }

    try {
      setProcessingRuleId(rule.id);
      clearMessages();
      await deleteProjectCleanupRule(projectId, rule.id);
      setSuccessMessage("Exceção excluída com sucesso.");
      await loadRules(projectId);
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Não foi possível excluir a exceção.",
      );
    } finally {
      setProcessingRuleId(null);
    }
  }

  return (
    <section>
      <div className="page-heading">
        <div>
          <span className="page-eyebrow">
            ADMINISTRAÇÃO
          </span>

          <h1>Exceções de limpeza</h1>

          <p>
            Configure as regras específicas utilizadas na limpeza do resultado
            de Build deste projeto.
          </p>
        </div>

        <div
          style={{
            display: "flex",
            gap: "8px",
            alignItems: "center",
          }}
        >
          <button
            className="secondary-button"
            type="button"
            onClick={() => {
              if (projectId) {
                void loadData(projectId);
              }
            }}
            disabled={isLoading || isLoadingRules}
          >
            <RefreshCw size={14} />
            Atualizar
          </button>

          <button
            className="secondary-button"
            type="button"
            onClick={() => navigate("/projects")}
          >
            <ArrowLeft size={14} />
            Voltar aos projetos
          </button>
        </div>
      </div>

      {errorMessage && (
        <div className="error-message">
          {errorMessage}
        </div>
      )}

      {successMessage && (
        <div className="success-message">
          {successMessage}
        </div>
      )}

      {isLoading ? (
        <div className="empty-state">
          <Loader2 size={24} className="spin" />
          <strong>Carregando projeto...</strong>
        </div>
      ) : project === null ? (
        <div className="empty-state">
          <FolderCog size={28} />
          <strong>Projeto não encontrado.</strong>
          <span>Volte para a tela de projetos e selecione um projeto válido.</span>
        </div>
      ) : (
        <>
          <div
            className="content-card"
            style={{ marginBottom: "18px" }}
          >
            <div className="card-header">
              <div>
                <h2>{project.name}</h2>
                <p>
                  Projeto {project.id} · {project.type === "client" ? "Cliente" : "Servidor"}
                </p>
              </div>

              <FolderCog size={21} />
            </div>

            <div
              style={{
                padding: "13px 14px",
                border: "1px solid #dbeafe",
                borderRadius: "9px",
                background: "#eff6ff",
                color: "#1e40af",
                fontSize: "11px",
                lineHeight: 1.5,
              }}
            >
              <strong>Como funciona</strong>
              <div style={{ marginTop: "4px" }}>
                As regras específicas deste projeto complementam as regras
                globais de limpeza. Quando houver conflito, a regra específica
                do projeto tem prioridade.
              </div>
            </div>
          </div>

          <div className="dashboard-grid">
            <div className="content-card">
              <div className="card-header">
                <div>
                  <h2>
                    {editingRuleId === null
                      ? "Nova exceção"
                      : "Editar exceção"}
                  </h2>

                  <p>
                    Defina o arquivo ou diretório e a ação que deverá ser aplicada.
                  </p>
                </div>

                {isFormVisible && (
                  <button
                    className="table-action-button"
                    type="button"
                    onClick={closeForm}
                    disabled={isSaving}
                    title="Fechar"
                  >
                    <X size={14} />
                  </button>
                )}
              </div>

              {!isFormVisible ? (
                <div className="empty-state compact">
                  <Plus size={26} />
                  <strong>Nenhuma edição em andamento</strong>
                  <span>
                    Clique em "Nova exceção" para cadastrar uma regra para este projeto.
                  </span>
                  <button
                    className="primary-button"
                    type="button"
                    onClick={openCreate}
                  >
                    <Plus size={14} />
                    Nova exceção
                  </button>
                </div>
              ) : (
                <form
                  onSubmit={(event) => {
                    event.preventDefault();
                    void saveRule();
                  }}
                >
                  <div className="form-grid">
                    <div className="form-field">
                      <label htmlFor="cleanup-target">
                        Tipo
                      </label>

                      <select
                        id="cleanup-target"
                        value={form.target}
                        onChange={(event) =>
                          setForm((current) => ({
                            ...current,
                            target: event.target.value as CleanupRuleTarget,
                          }))
                        }
                        disabled={isSaving}
                      >
                        <option value="file">Arquivo</option>
                        <option value="directory">Diretório</option>
                      </select>
                    </div>

                    <div className="form-field">
                      <label htmlFor="cleanup-action">
                        Ação
                      </label>

                      <select
                        id="cleanup-action"
                        value={form.action}
                        onChange={(event) =>
                          setForm((current) => ({
                            ...current,
                            action: event.target.value as CleanupRuleAction,
                          }))
                        }
                        disabled={isSaving}
                      >
                        <option value="preserve">Preservar</option>
                        <option value="remove">Remover</option>
                      </select>
                    </div>

                    <div className="form-field form-field-full">
                      <label htmlFor="cleanup-pattern">
                        Padrão
                      </label>

                      <input
                        id="cleanup-pattern"
                        value={form.pattern}
                        onChange={(event) =>
                          setForm((current) => ({
                            ...current,
                            pattern: event.target.value,
                          }))
                        }
                        placeholder={
                          form.target === "file"
                            ? "Ex.: Web.config ou *.json"
                            : "Ex.: Xml ou x64"
                        }
                        disabled={isSaving}
                      />
                    </div>

                    <div className="form-field form-field-full">
                      <label htmlFor="cleanup-description">
                        Descrição
                      </label>

                      <textarea
                        id="cleanup-description"
                        value={form.description}
                        onChange={(event) =>
                          setForm((current) => ({
                            ...current,
                            description: event.target.value,
                          }))
                        }
                        placeholder="Explique por que esta exceção é necessária."
                        disabled={isSaving}
                      />
                    </div>
                  </div>

                  <div
                    style={{
                      display: "flex",
                      flexWrap: "wrap",
                      gap: "18px",
                      marginTop: "14px",
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
                        checked={form.recursive}
                        onChange={(event) =>
                          setForm((current) => ({
                            ...current,
                            recursive: event.target.checked,
                          }))
                        }
                        disabled={isSaving}
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
                        checked={form.enabled}
                        onChange={(event) =>
                          setForm((current) => ({
                            ...current,
                            enabled: event.target.checked,
                          }))
                        }
                        disabled={isSaving}
                      />
                      Regra ativa
                    </label>
                  </div>

                  <div className="form-actions">
                    <button
                      className="secondary-button"
                      type="button"
                      onClick={closeForm}
                      disabled={isSaving}
                    >
                      <X size={14} />
                      Cancelar
                    </button>

                    <button
                      className="primary-button"
                      type="submit"
                      disabled={isSaving}
                    >
                      {isSaving ? (
                        <Loader2 size={14} className="spin" />
                      ) : (
                        <Check size={14} />
                      )}
                      {editingRuleId === null
                        ? "Adicionar exceção"
                        : "Salvar alteração"}
                    </button>
                  </div>
                </form>
              )}
            </div>

            <div className="content-card">
              <div className="card-header">
                <div>
                  <h2>Regras específicas do projeto</h2>
                  <p>
                    Exceções cadastradas para {project.name}.
                  </p>
                </div>

                <span className="status-badge status-badge-active">
                  {rules.length} {rules.length === 1 ? "regra" : "regras"}
                </span>
              </div>

              {isLoadingRules ? (
                <div className="empty-state compact">
                  <Loader2 size={22} className="spin" />
                  <span>Carregando regras...</span>
                </div>
              ) : rules.length === 0 ? (
                <div className="empty-state compact">
                  <FolderCog size={24} />
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
                  {rules.map((rule) => (
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
                          {rule.action === "preserve" ? "Preservar" : "Remover"}
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
                      </div>

                      <div className="project-admin-actions">
                        <button
                          className="table-action-button"
                          type="button"
                          onClick={() => openEdit(rule)}
                          disabled={processingRuleId !== null}
                        >
                          <Edit3 size={14} />
                          Editar
                        </button>

                        <button
                          className="table-action-button"
                          type="button"
                          onClick={() => void deleteRule(rule)}
                          disabled={processingRuleId !== null}
                          title="Excluir"
                        >
                          {processingRuleId === rule.id ? (
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
        </>
      )}
    </section>
  );
}

export default CleanupRulesPage;
