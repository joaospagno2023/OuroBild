import {
  Plus,
  Users,
} from "lucide-react";

function UsersPage() {
  return (
    <section>
      <div className="page-heading">
        <div>
          <span className="page-eyebrow">
            ADMINISTRAÇÃO
          </span>

          <h1>Usuários</h1>

          <p>
            Gerencie os usuários e permissões do
            OuroBuild.
          </p>
        </div>

        <button
          className="primary-button"
          type="button"
        >
          <Plus size={18} />
          Novo usuário
        </button>
      </div>

      <div className="content-card">
        <div className="empty-state">
          <Users size={32} />

          <strong>
            Nenhum usuário cadastrado
          </strong>

          <span>
            O gerenciamento de usuários será
            conectado ao módulo de autenticação.
          </span>
        </div>
      </div>
    </section>
  );
}

export default UsersPage;
