import {
  FolderCog,
  Settings,
  SlidersHorizontal,
} from "lucide-react";

function AdministrationPage() {
  return (
    <section>
      <div className="page-heading">
        <div>
          <span className="page-eyebrow">
            CONFIGURAÇÃO
          </span>

          <h1>Administração</h1>

          <p>
            Configurações gerais do ambiente OuroBuild.
          </p>
        </div>
      </div>

      <div className="admin-grid">
        <div className="admin-card">
          <div className="admin-card-icon">
            <FolderCog size={21} />
          </div>

          <h2>Projetos</h2>

          <p>
            Configuração e gerenciamento dos projetos
            disponíveis para build e setup.
          </p>

          <button
            className="secondary-button"
            type="button"
          >
            Configurar
          </button>
        </div>

        <div className="admin-card">
          <div className="admin-card-icon">
            <SlidersHorizontal size={21} />
          </div>

          <h2>Ambientes</h2>

          <p>
            Gerencie ambientes, caminhos e parâmetros
            utilizados pelas execuções.
          </p>

          <button
            className="secondary-button"
            type="button"
          >
            Configurar
          </button>
        </div>

        <div className="admin-card">
          <div className="admin-card-icon">
            <Settings size={21} />
          </div>

          <h2>Configurações</h2>

          <p>
            Parâmetros gerais e configurações do
            sistema de automação.
          </p>

          <button
            className="secondary-button"
            type="button"
          >
            Configurar
          </button>
        </div>
      </div>
    </section>
  );
}

export default AdministrationPage;
