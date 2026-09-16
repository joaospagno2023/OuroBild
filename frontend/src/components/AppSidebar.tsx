import {
  BarChart3,
  Boxes,
  ClipboardList,
  Settings,
  Rocket,
} from "lucide-react";
import {
  useCallback,
  useEffect,
  useState,
} from "react";
import { NavLink } from "react-router-dom";

type MenuItem = {
  label: string;
  path: string;
  icon: React.ReactNode;
};

type OuroDeploySqlStatus = {
  configured: boolean;
  online: boolean;
  url: string;
  message: string;
};

type OuroDeploySqlState =
  | "checking"
  | "online"
  | "offline"
  | "not-configured";

const menuItems: MenuItem[] = [
  {
    label: "Dashboard",
    path: "/dashboard",
    icon: <BarChart3 size={19} />,
  },
  {
    label: "Geração de Setup",
    path: "/setups",
    icon: <Rocket size={19} />,
  },
  {
    label: "Histórico",
    path: "/history",
    icon: <ClipboardList size={19} />,
  },
  {
    label: "Administração",
    path: "/administration",
    icon: <Settings size={19} />,
  },
];

function AppSidebar() {
  const [
    ouroDeploySqlState,
    setOuroDeploySqlState,
  ] = useState<OuroDeploySqlState>("checking");

  const checkOuroDeploySqlStatus =
    useCallback(async () => {
      try {
        setOuroDeploySqlState("checking");

        const response = await fetch(
          "/api/configuration/ourodeploy-sql/status",
          {
            method: "GET",
            credentials: "include",
          },
        );

        if (!response.ok) {
          setOuroDeploySqlState("offline");
          return;
        }

        const data =
          (await response.json()) as OuroDeploySqlStatus;

        if (!data.configured) {
          setOuroDeploySqlState(
            "not-configured",
          );
          return;
        }

        if (data.online) {
          setOuroDeploySqlState("online");
          return;
        }

        setOuroDeploySqlState("offline");
      } catch {
        setOuroDeploySqlState("offline");
      }
    }, []);

  useEffect(() => {
    void checkOuroDeploySqlStatus();

    const intervalId = window.setInterval(
      () => {
        void checkOuroDeploySqlStatus();
      },
      30_000,
    );

    return () => {
      window.clearInterval(intervalId);
    };
  }, [checkOuroDeploySqlStatus]);

  function getOuroDeploySqlStatusTitle(): string {
    switch (ouroDeploySqlState) {
      case "online":
        return "Online";

      case "offline":
        return "Offline";

      case "not-configured":
        return "Não configurada";

      case "checking":
      default:
        return "Verificando...";
    }
  }

  function getOuroDeploySqlStatusClass(): string {
    switch (ouroDeploySqlState) {
      case "online":
        return "status-dot status-dot-online";

      case "offline":
        return "status-dot status-dot-offline";

      case "not-configured":
        return "status-dot status-dot-not-configured";

      case "checking":
      default:
        return "status-dot status-dot-checking";
    }
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">
          <Boxes size={22} />
        </div>

        <div>
          <strong>OuroBuild</strong>
          <span>Build & Setup Manager</span>
        </div>
      </div>

      <div className="sidebar-section-title">
        PRINCIPAL
      </div>

      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `sidebar-link ${
                isActive
                  ? "sidebar-link-active"
                  : ""
              }`
            }
          >
            {item.icon}
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="system-status">
          <span className="status-dot" />
          <div>
            <strong>Sistema online</strong>
            <span>OuroBuild API</span>
          </div>
        </div>

        <div className="system-status">
          <span
            className={getOuroDeploySqlStatusClass()}
          />

          <div>
            <strong>OuroDeploy SQL</strong>
            <span>
              {getOuroDeploySqlStatusTitle()}
            </span>
          </div>
        </div>

        <div className="sidebar-version">
          Versão 1.0.0
        </div>
      </div>
    </aside>
  );
}

export default AppSidebar;