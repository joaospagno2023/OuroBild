import {
  ArrowLeft,
  CheckCircle2,
  Clock3,
  Download,
  FileText,
  Layers3,
  Loader2,
  RefreshCw,
  XCircle,
} from "lucide-react";
import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import {
  useNavigate,
  useSearchParams,
} from "react-router-dom";

import {
  getHistory,
  getHistoryDetail,
  getHistoryLogs,
  type PipelineHistoryDetail,
  type PipelineHistoryItem,
  type PipelineHistoryLogs,
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

function LogsPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const executionId = searchParams.get("execution_id");

  const [selectedExecutionId, setSelectedExecutionId] =
    useState<string | null>(executionId);
  const [detail, setDetail] =
    useState<PipelineHistoryDetail | null>(null);
  const [logs, setLogs] =
    useState<PipelineHistoryLogs | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [autoScroll, setAutoScroll] = useState(true);

  const logContainerRef = useRef<HTMLPreElement | null>(null);

  const loadExecutionLogs = useCallback(
    async (refreshing = false): Promise<void> => {
      if (!selectedExecutionId) {
        return;
      }

      try {
        setErrorMessage("");

        if (refreshing) {
          setIsRefreshing(true);
        } else {
          setIsLoading(true);
        }

        const [detailResult, logsResult] = await Promise.all([
          getHistoryDetail(selectedExecutionId),
          getHistoryLogs(selectedExecutionId),
        ]);

        setDetail(detailResult);
        setLogs(logsResult);
      } catch (error) {
        setErrorMessage(
          error instanceof Error
            ? error.message
            : "Não foi possível carregar os logs da execução.",
        );
      } finally {
        setIsLoading(false);
        setIsRefreshing(false);
      }
    },
    [selectedExecutionId],
  );

  useEffect(() => {
    setSelectedExecutionId(executionId);
  }, [executionId]);

  useEffect(() => {
    let cancelled = false;

    async function loadLatestExecution(): Promise<void> {
      if (executionId) {
        return;
      }

      try {
        setErrorMessage("");
        setIsLoading(true);

        const history: PipelineHistoryItem[] = await getHistory();
        if (cancelled) {
          return;
        }

        const latestExecution = history[0] ?? null;
        setSelectedExecutionId(latestExecution?.execution_id ?? null);
      } catch (error) {
        if (cancelled) {
          return;
        }

        setErrorMessage(
          error instanceof Error
            ? error.message
            : "Não foi possível carregar a execução mais recente.",
        );
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    setDetail(null);
    setLogs(null);
    setErrorMessage("");
    void loadLatestExecution();

    return () => {
      cancelled = true;
    };
  }, [executionId]);

  useEffect(() => {
    if (selectedExecutionId) {
      void loadExecutionLogs();
    }
  }, [selectedExecutionId, loadExecutionLogs]);

  useEffect(() => {
    if (!autoScroll || !logContainerRef.current) {
      return;
    }

    const container = logContainerRef.current;
    container.scrollTop = container.scrollHeight;
  }, [logs?.content, autoScroll]);

  function handleDownload(): void {
    if (!logs) {
      return;
    }

    const blob = new Blob([logs.content], {
      type: "text/plain;charset=utf-8",
    });

    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");

    anchor.href = url;
    anchor.download = `pipeline-${logs.execution_id}.log`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  }

  function renderStatus() {
    if (!detail) {
      return null;
    }

    if (detail.success) {
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

  function renderEmptyPage() {
    return (
      <section>
        <div className="page-heading">
          <div>
            <span className="page-eyebrow">MONITORAMENTO</span>
            <h1>Logs</h1>
            <p>
              Consulte os registros da aplicação e das gerações.
            </p>
          </div>
        </div>

        <div className="dashboard-grid">
          <div className="content-card">
            <div className="card-header">
              <div>
                <h2>Logs da aplicação</h2>
                <p>Eventos gerais do OuroBuild.</p>
              </div>
              <FileText size={21} />
            </div>

            <div className="empty-state compact">
              <FileText size={28} />
              <strong>Nenhum log selecionado</strong>
              <span>
                Selecione uma execução no Histórico para consultar
                seus registros.
              </span>
            </div>
          </div>

          <div className="content-card">
            <div className="card-header">
              <div>
                <h2>Logs de geração</h2>
                <p>Execução de Builds e Setups.</p>
              </div>
              <Layers3 size={21} />
            </div>

            <div className="empty-state compact">
              <Layers3 size={28} />
              <strong>Nenhuma geração selecionada</strong>
              <span>
                Abra os detalhes de uma execução no Histórico e
                clique em Logs.
              </span>
            </div>
          </div>
        </div>
      </section>
    );
  }

  if (!selectedExecutionId) {
    return renderEmptyPage();
  }

  return (
    <section>
      <div className="page-heading">
        <div>
          <span className="page-eyebrow">MONITORAMENTO</span>
          <h1>Logs</h1>
          <p>
            Consulte os registros da aplicação e das gerações.
          </p>
        </div>
      </div>

      {errorMessage && (
        <div className="error-message">{errorMessage}</div>
      )}

      <div className="content-card">
        <div className="card-header">
          <div>
            <h2>Logs da execução</h2>
            <p>
              Registros detalhados da execução da Pipeline.
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
              onClick={() => navigate(-1)}
            >
              <ArrowLeft size={14} />
              Voltar
            </button>

            <button
              className="secondary-button"
              type="button"
              onClick={() => void loadExecutionLogs(true)}
              disabled={isRefreshing || isLoading}
            >
              <RefreshCw
                size={14}
                className={
                  isRefreshing ? "spin" : undefined
                }
              />
              Atualizar
            </button>

            <button
              className="secondary-button"
              type="button"
              onClick={handleDownload}
              disabled={!logs}
            >
              <Download size={14} />
              Baixar
            </button>
          </div>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "1.25fr 1fr 1fr 0.8fr 1.1fr 0.8fr",
            gap: "0",
            marginBottom: "16px",
            padding: "16px 20px",
            border: "1px solid #dce6f5",
            borderRadius: "10px",
            background: "#f3f7ff",
          }}
        >
          <div>
            <strong>Execução</strong>
            <div>{selectedExecutionId}</div>
          </div>

          <div>
            <strong>Projeto</strong>
            <div>{detail?.project_name ?? "-"}</div>
          </div>

          <div>
            <strong>Versão</strong>
            <div>{detail?.version ?? "Não informada"}</div>
          </div>

          <div>
            <strong>Status</strong>
            <div>{renderStatus() ?? "-"}</div>
          </div>

          <div>
            <strong>Início</strong>
            <div>{formatDateTime(detail?.started_at ?? null)}</div>
          </div>

          <div>
            <strong>Duração</strong>
            <div>
              {formatDuration(detail?.elapsed_seconds ?? 0)}
            </div>
          </div>
        </div>

        {isLoading && !logs ? (
          <div className="empty-state compact">
            <Loader2 size={28} className="spin" />
            <strong>Carregando logs...</strong>
            <span>Aguarde enquanto os registros são consultados.</span>
          </div>
        ) : logs ? (
          <div
            style={{
              overflow: "hidden",
              borderRadius: "10px",
              background: "#161d28",
              border: "1px solid #283445",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "flex-end",
                alignItems: "center",
                padding: "8px 14px",
                color: "#ffffff",
                fontSize: "13px",
                borderBottom: "1px solid #283445",
              }}
            >
              <label
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  cursor: "pointer",
                }}
              >
                Auto scroll
                <input
                  type="checkbox"
                  checked={autoScroll}
                  onChange={(event) =>
                    setAutoScroll(event.target.checked)
                  }
                />
              </label>
            </div>

            <pre
              ref={logContainerRef}
              style={{
                margin: 0,
                height: "460px",
                overflow: "auto",
                padding: "14px",
                color: "#edf3ff",
                fontFamily:
                  "Consolas, 'Courier New', monospace",
                fontSize: "13px",
                lineHeight: 1.55,
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
              }}
            >
              {logs.content || "Nenhum registro foi gravado para esta execução."}
            </pre>
          </div>
        ) : (
          <div className="empty-state compact">
            <Clock3 size={28} />
            <strong>Logs não disponíveis</strong>
            <span>
              Esta execução ainda não possui um arquivo de log
              individual.
            </span>
          </div>
        )}
      </div>
    </section>
  );
}

export default LogsPage;
