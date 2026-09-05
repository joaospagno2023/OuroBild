import {
  Bell,
  ChevronDown,
  Menu,
  LogOut,
} from "lucide-react";

import { useAuth } from "../auth/AuthContext";

type AppHeaderProps = {
  onMenuClick: () => void;
};

function AppHeader({
  onMenuClick,
}: AppHeaderProps) {
  const {
    user,
    logout,
  } = useAuth();

  function handleLogout(): void {
    logout();
  }

  const displayName =
    user?.display_name ||
    user?.username ||
    "Usuário";

  return (
    <header className="app-header">
      <button
        className="mobile-menu-button"
        type="button"
        onClick={onMenuClick}
        aria-label="Abrir menu"
      >
        <Menu size={21} />
      </button>

      <div className="header-title">
        <span>OuroBuild</span>

        <strong>
          Automação de Builds e Setups
        </strong>
      </div>

      <div className="header-actions">
        <button
          className="icon-button"
          type="button"
          aria-label="Notificações"
        >
          <Bell size={19} />

          <span className="notification-dot" />
        </button>

        <div className="user-menu">
          <div className="user-avatar">
            {displayName
              .substring(0, 2)
              .toUpperCase()}
          </div>

          <div className="user-info">
            <strong>
              {displayName}
            </strong>

            <span>
              {user?.username}
            </span>
          </div>

          <button
            className="icon-button"
            type="button"
            onClick={handleLogout}
            aria-label="Sair"
            title="Sair"
          >
            <LogOut size={17} />
          </button>

          <ChevronDown size={17} />
        </div>
      </div>
    </header>
  );
}

export default AppHeader;