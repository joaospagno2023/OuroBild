import {
  CheckCircle2,
  ChevronRight,
  Clock3,
  FileText,
  Loader2,
  RefreshCw,
  XCircle,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getHistory,
  getHistoryDetail,
  type PipelineHistoryDetail,
  type PipelineHistoryItem,
} from "../services/historyApi";

function formatDateTime(value: string | null): string {
  if (!value) {
    return "-";
  }

  const parsed = new Date(value);

  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return parsed.toLocaleString("pt-BR");
}

function formatDuration(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) {
    return "-";
  }

  const totalSeconds = Math.round(seconds);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const remainingSeconds = totalSeconds % 60;

  if (hours > 0) {
    return `${hours}h ${minutes}m ${remainingSeconds}s`;
  }

  if (minutes > 0) {
    return `${minutes}m ${remainingSeconds}s`;
  }

  return `${remainingSeconds}s`;
}

function getStatusLabel(item: PipelineHistoryItem): string {
  return item.success ? "Sucesso" : "Falha";
}

function HistoryPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<PipelineHistoryItem[]>([]);
  const [selectedExecutionId, setSelectedExecutionId] =
    useState<string | null>(null);
  const [detail, setDetail] =
    useState<PipelineHistoryDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isLoadingDetail, setIsLoadingDetail] =
    useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    void loadHistory();
  }, []);

  async function loadHistory(
    refreshing = false,
  ): Promise<void> {
    try {
      setErrorMessage("");

      if (refreshing) {
        setIsRefreshing(true);
      } else {
        setIsLoading(true);
      }

      const result = await getHistory();
      setItems(result);

      if (
        selectedExecutionId &&
        !result.some(
          (item) => item.execution_id === selectedExecutionId,
        )
      ) {
        setSelectedExecutionId(null);
        setDetail(null);
      }
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Não foi possível carregar o histórico.",
      );
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }

  async function openDetail(
    executionId: string,
  ): Promise<void> {
    try {
      setErrorMessage("");
      setSelectedExecutionId(executionId);
      setIsLoadingDetail(true);
      setDetail(null);

      const result = await getHistoryDetail(
        executionId,
      );

      setDetail(result);
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Não foi possível carregar os detalhes da execução.",
      );
    } finally {
      setIsLoadingDetail(false);
    }
  }

  function renderStatus(item: PipelineHistoryItem) {
    if (item.success) {
      return (
        <span className="status-badge status-badge-active">
          <CheckCircle2 size={12} />
          Sucesso
        </span>
      );
    }

    return (
      <span className="status-badge status-badge-inactive">
        <XCircle size={12} />
        Falha
      </span>
    );
  }

  function renderHistoryList() {
    if (isLoading) {
      return (
        <div className="empty-state">
          <Loader2 size={28} className="spin" />
          <strong>Carregando histórico...</strong>
        </div>
      );
    }

    if (items.length === 0) {
      return (
        <div className="empty-state">
          <Clock3 size={32} />
          <strong>Nenhum histórico disponível</strong>
          <span>
            As execuções concluídas aparecerão nesta tela.
          </span>
        </div>
      );
    }

    return (
      <div className="project-admin-list">
        {items.map((item) => (
          <div
            className="project-admin-row"
            key={item.execution_id}
          >
            <div className="project-admin-icon">
              {item.success ? (
                <CheckCircle2 size={18} />
              ) : (
                <XCircle size={18} />
              )}
            </div>

            <div className="project-admin-info">
              <strong>{item.project_name}</strong>
              <span>
                Versão {item.version ?? "não informada"} · {formatDateTime(item.started_at)} · {item.execution_id}
              </span>
            </div>

            {renderStatus(item)}

            <div className="project-admin-info">
              <strong>
                {formatDuration(item.elapsed_seconds)}
              </strong>
              <span>
                {item.steps_count} {item.steps_count === 1 ? "etapa" : "etapas"}
              </span>
            </div>

            <div className="project-admin-actions">
              <button
                className="table-action-button"
                type="button"
                onClick={() => void openDetail(item.execution_id)}
              >
                Detalhes
                <ChevronRight size={14} />
              </button>
            </div>
          </div>
        ))}
      </div>
    );
  }

  function renderDetail() {
    if (!selectedExecutionId) {
      return null;
    }

    return (
      <div className="content-card">
        <div className="card-header">
          <div>
            <h2>Detalhes da execução</h2>
            <p>
              Informações e etapas da execução selecionada.
            </p>
          </div>

          <button
            className="secondary-button"
            type="button"
            onClick={() =>
              navigate(`/logs?execution_id=${encodeURIComponent(detail?.execution_id ?? selectedExecutionId)}`)
            }
            disabled={!detail}
          >
            <FileText size={14} />
            Logs
          </button>
        </div>

        {isLoadingDetail && (
          <div className="empty-state compact">
            <Loader2 size={24} className="spin" />
            <strong>Carregando detalhes...</strong>
          </div>
        )}

        {!isLoadingDetail && detail && (
          <div className="dashboard-grid">
            <div className="system-list">
              <div className="system-item">
                <div>
                  <strong>Projeto</strong>
                  <span>{detail.project_name}</span>
                </div>
              </div>

              <div className="system-item">
                <div>
                  <strong>Versão</strong>
                  <span>{detail.version ?? "Não informada"}</span>
                </div>
              </div>

              <div className="system-item">
                <div>
                  <strong>Status</strong>
                  <span>{getStatusLabel(detail)}</span>
                </div>
              </div>

              <div className="system-item">
                <div>
                  <strong>Início</strong>
                  <span>{formatDateTime(detail.started_at)}</span>
                </div>
              </div>

              <div className="system-item">
                <div>
                  <strong>Fim</strong>
                  <span>{formatDateTime(detail.finished_at)}</span>
                </div>
              </div>

              <div className="system-item">
                <div>
                  <strong>Duração</strong>
                  <span>{formatDuration(detail.elapsed_seconds)}</span>
                </div>
              </div>

              {detail.failed_step && (
                <div className="system-item">
                  <div>
                    <strong>Etapa com falha</strong>
                    <span>{detail.failed_step}</span>
                  </div>
                </div>
              )}

              {detail.message && (
                <div className="system-item">
                  <div>
                    <strong>Mensagem</strong>
                    <span>{detail.message}</span>
                  </div>
                </div>
              )}
            </div>

            <div className="content-card">
              <div className="card-header">
                <div>
                  <h2>Etapas</h2>
                  <p>Resultado de cada etapa executada.</p>
                </div>
              </div>

              <div className="system-list">
                {detail.steps.map((step, index) => (
                  <div
                    className="system-item"
                    key={`${detail.execution_id}-${index}`}
                  >
                    <div>
                      <strong>
                        {String(step.name ?? `Etapa ${index + 1}`)}
                      </strong>
                      <span>
                        {String(step.status ?? "-")}
                        {step.message
                          ? ` · ${String(step.message)}`
                          : ""}
                      </span>
                    </div>
                  </div>
                ))}

                {detail.steps.length === 0 && (
                  <div className="empty-state compact">
                    <strong>Nenhuma etapa registrada.</strong>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <section>
      <div className="page-heading">
        <div>
          <span className="page-eyebrow">AUDITORIA</span>
          <h1>Histórico</h1>
          <p>
            Consulte as gerações e execuções realizadas no OuroBuild.
          </p>
        </div>
      </div>

      {errorMessage && (
        <div className="error-message">{errorMessage}</div>
      )}

      <div className="content-card">
        <div className="card-header">
          <div>
            <h2>Execuções</h2>
            <p>Histórico das execuções de Build e Setup.</p>
          </div>

          <button
            className="secondary-button"
            type="button"
            onClick={() => void loadHistory(true)}
            disabled={isRefreshing}
          >
            <RefreshCw
              size={14}
              className={isRefreshing ? "spin" : undefined}
            />
            Atualizar
          </button>
        </div>

        {renderHistoryList()}
      </div>

      {renderDetail()}
    </section>
  );
}

export default HistoryPage;
