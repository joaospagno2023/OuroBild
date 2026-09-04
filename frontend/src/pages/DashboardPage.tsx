import {
  AlertCircle,
  CheckCircle2,
  Clock3,
  Rocket,
} from "lucide-react";

function DashboardPage() {
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

        <a
          className="primary-button"
          href="/setups"
        >
          <Rocket size={18} />
          Gerar Setup
        </a>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">
            <Rocket size={21} />
          </div>

          <span>Setups gerados</span>
          <strong>0</strong>
          <small>Este período</small>
        </div>

        <div className="stat-card">
          <div className="stat-icon success">
            <CheckCircle2 size={21} />
          </div>

          <span>Execuções concluídas</span>
          <strong>0</strong>
          <small>Com sucesso</small>
        </div>

        <div className="stat-card">
          <div className="stat-icon warning">
            <Clock3 size={21} />
          </div>

          <span>Em execução</span>
          <strong>0</strong>
          <small>Processamentos ativos</small>
        </div>

        <div className="stat-card">
          <div className="stat-icon danger">
            <AlertCircle size={21} />
          </div>

          <span>Falhas</span>
          <strong>0</strong>
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
