import {
  AlertCircle,
  CheckCircle2,
  ChevronRight,
  Clock3,
  Loader2,
  RefreshCw,
  Rocket,
  XCircle,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getHistory,
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

function DashboardPage() {
  const navigate = useNavigate();

  const [items, setItems] = useState<PipelineHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    void loadDashboard();
  }, []);

  async function loadDashboard(
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
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Não foi possível carregar os dados do dashboard.",
      );
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }

  const completedCount = items.filter(
    (item) => item.success,
  ).length;

  const failedCount = items.filter(
    (item) => !item.success,
  ).length;

  /*
   * O endpoint atual de histórico retorna apenas execuções
   * já persistidas como concluídas ou com falha. Portanto,
   * o contador de processos ativos permanece em zero até
   * termos um endpoint específico para estados em execução.
   */
  const runningCount = 0;

  const setupCount = completedCount;

  const recentItems = items.slice(0, 5);

  return (
    <section>
      <div className="page-heading">
        <div>
          <span className="page-eyebrow">
            VISÃO GERAL
          </span>

          <h1>Dashboard</h1>

          <p>
            Acompanhe builds, setups e execuções do
            OuroBuild.
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
            onClick={() => void loadDashboard(true)}
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

          <a
            className="primary-button"
            href="/setups"
          >
            <Rocket size={18} />
            Gerar Setup
          </a>
        </div>
      </div>

      {errorMessage && (
        <div className="error-message">
          {errorMessage}
        </div>
      )}

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">
            <Rocket size={21} />
          </div>

          <span>Setups gerados</span>
          <strong>
            {isLoading ? "..." : setupCount}
          </strong>
          <small>Execuções concluídas</small>
        </div>

        <div className="stat-card">
          <div className="stat-icon success">
            <CheckCircle2 size={21} />
          </div>

          <span>Execuções concluídas</span>
          <strong>
            {isLoading ? "..." : completedCount}
          </strong>
          <small>Com sucesso</small>
        </div>

        <div className="stat-card">
          <div className="stat-icon warning">
            <Clock3 size={21} />
          </div>

          <span>Em execução</span>
          <strong>
            {isLoading ? "..." : runningCount}
          </strong>
          <small>Processamentos ativos</small>
        </div>

        <div className="stat-card">
          <div className="stat-icon danger">
            <AlertCircle size={21} />
          </div>

          <span>Falhas</span>
          <strong>
            {isLoading ? "..." : failedCount}
          </strong>
          <small>Necessitam atenção</small>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="content-card">
          <div className="card-header">
            <div>
              <h2>Execuções recentes</h2>
              <p>
                Últimas operações realizadas no sistema.
              </p>
            </div>
          </div>

          {isLoading ? (
            <div className="empty-state">
              <Loader2 size={32} className="spin" />
              <strong>Carregando execuções...</strong>
            </div>
          ) : recentItems.length === 0 ? (
            <div className="empty-state">
              <Rocket size={32} />

              <strong>
                Nenhuma execução registrada
              </strong>

              <span>
                As execuções aparecerão aqui quando
                começarmos a gerar os setups.
              </span>
            </div>
          ) : (
            <div className="project-admin-list">
              {recentItems.map((item) => (
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
                      {item.version
                        ? `Versão ${item.version} · `
                        : ""}
                      {formatDateTime(item.started_at)}
                    </span>
                    <span>{item.execution_id}</span>
                  </div>

                  <span
                    className={
                      item.success
                        ? "status-badge status-badge-active"
                        : "status-badge status-badge-inactive"
                    }
                  >
                    {item.success ? (
                      <CheckCircle2 size={12} />
                    ) : (
                      <XCircle size={12} />
                    )}
                    {getStatusLabel(item)}
                  </span>

                  <div className="project-admin-info">
                    <strong>
                      {formatDuration(
                        item.elapsed_seconds,
                      )}
                    </strong>
                    <span>
                      {item.steps_count} {item.steps_count === 1
                        ? "etapa"
                        : "etapas"}
                    </span>
                  </div>

                  <button
                    className="secondary-button"
                    type="button"
                    onClick={() =>
                      navigate(
                        `/history?execution_id=${encodeURIComponent(
                          item.execution_id,
                        )}`,
                      )
                    }
                    aria-label={`Abrir histórico da execução ${item.execution_id}`}
                  >
                    Detalhes
                    <ChevronRight size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="content-card">
          <div className="card-header">
            <div>
              <h2>Status do sistema</h2>
              <p>
                Componentes principais do OuroBuild.
              </p>
            </div>
          </div>

          <div className="system-list">
            <div className="system-item">
              <span className="status-dot" />
              <div>
                <strong>API</strong>
                <span>Disponível</span>
              </div>
            </div>

            <div className="system-item">
              <span className="status-dot" />
              <div>
                <strong>Pipeline</strong>
                <span>Disponível</span>
              </div>
            </div>

            <div className="system-item">
              <span className="status-dot" />
              <div>
                <strong>Advanced Installer</strong>
                <span>Configurado</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default DashboardPage;
