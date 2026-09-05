import {
  FolderCog,
  Settings,
  SlidersHorizontal,
  Users,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

function AdministrationPage() {
  const navigate = useNavigate();

  return (
    <section>
      <div className="page-heading">
        <div>
          <span className="page-eyebrow">
            CONFIGURAÇÃO
          </span>

          <h1>Administração</h1>

          <p>
            Gerencie as configurações e recursos
            administrativos do OuroBuild.
          </p>
        </div>
      </div>

      <div className="admin-grid">
        <div className="admin-card">
          <div className="admin-card-icon">
            <Users size={21} />
          </div>

          <h2>Usuários</h2>

          <p>
            Cadastre, altere e gerencie os usuários
            do OuroBuild.
          </p>

          <button
            className="secondary-button"
            type="button"
            onClick={() => navigate("/users")}
          >
            Configurar
          </button>
        </div>

        <div className="admin-card">
          <div className="admin-card-icon">
            <FolderCog size={21} />
          </div>

          <h2>Projetos</h2>

          <p>
            Cadastre, altere e gerencie os projetos
            disponíveis para build e setup.
          </p>

          <button
            className="secondary-button"
            type="button"
            onClick={() => navigate("/projects")}
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
            Gerencie os ambientes, caminhos e
            parâmetros utilizados pelas execuções.
          </p>

          <button
            className="secondary-button"
            type="button"
            onClick={() => navigate("/environments")}
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
            Gerencie os parâmetros gerais e as
            configurações do sistema de automação.
          </p>

          <button
            className="secondary-button"
            type="button"
            onClick={() => navigate("/settings")}
          >
            Configurar
          </button>
        </div>
      </div>
    </section>
  );
}

export default AdministrationPage;