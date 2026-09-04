import {
  FileText,
  Layers3,
} from "lucide-react";

function LogsPage() {
  return (
    <section>
      <div className="page-heading">
        <div>
          <span className="page-eyebrow">
            MONITORAMENTO
          </span>

          <h1>Logs</h1>

          <p>
            Consulte os registros da aplicação e das
            gerações.
          </p>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="content-card">
          <div className="card-header">
            <div>
              <h2>Logs da aplicação</h2>
              <p>
                Eventos gerais do OuroBuild.
              </p>
            </div>

            <FileText size={21} />
          </div>

          <div className="empty-state compact">
            <FileText size={28} />

            <strong>
              Nenhum log disponível
            </strong>

            <span>
              Os logs da aplicação serão
              disponibilizados aqui.
            </span>
          </div>
        </div>

        <div className="content-card">
          <div className="card-header">
            <div>
              <h2>Logs de geração</h2>
              <p>
                Execução de Builds e Setups.
              </p>
            </div>

            <Layers3 size={21} />
          </div>

          <div className="empty-state compact">
            <Layers3 size={28} />

            <strong>
              Nenhuma geração registrada
            </strong>

            <span>
              Os detalhes das gerações aparecerão
              aqui.
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}

export default LogsPage;
