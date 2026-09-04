import { Clock3 } from "lucide-react";

function HistoryPage() {
  return (
    <section>
      <div className="page-heading">
        <div>
          <span className="page-eyebrow">
            AUDITORIA
          </span>

          <h1>Histórico</h1>

          <p>
            Consulte as gerações e execuções
            realizadas no OuroBuild.
          </p>
        </div>
      </div>

      <div className="content-card">
        <div className="card-header">
          <div>
            <h2>Execuções</h2>
            <p>
              Histórico das gerações de Setup.
            </p>
          </div>
        </div>

        <div className="empty-state">
          <Clock3 size={32} />

          <strong>
            Nenhum histórico disponível
          </strong>

          <span>
            As execuções realizadas aparecerão
            nesta tela.
          </span>
        </div>
      </div>
    </section>
  );
}

export default HistoryPage;
