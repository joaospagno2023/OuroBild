
import {
  Bell,
  ChevronDown,
  Menu,
} from "lucide-react";

type AppHeaderProps = {
  onMenuClick: () => void;
};

function AppHeader({
  onMenuClick,
}: AppHeaderProps) {
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
        <strong>Automação de Builds e Setups</strong>
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
            JS
          </div>

          <div className="user-info">
            <strong>Administrador</strong>
            <span>Administrador</span>
          </div>

          <ChevronDown size={17} />
        </div>
      </div>
    </header>
  );
}

export default AppHeader;
