
import {
  BarChart3,
  Boxes,
  ClipboardList,
  FileText,
  Settings,
  Users,
  Rocket,
} from "lucide-react";
import { NavLink } from "react-router-dom";

type MenuItem = {
  label: string;
  path: string;
  icon: React.ReactNode;
};

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
    label: "Logs",
    path: "/logs",
    icon: <FileText size={19} />,
  },
  {
    label: "Usuários",
    path: "/users",
    icon: <Users size={19} />,
  },
  {
    label: "Administração",
    path: "/administration",
    icon: <Settings size={19} />,
  },
];

function AppSidebar() {
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
                isActive ? "sidebar-link-active" : ""
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

        <div className="sidebar-version">
          Versão 1.0.0
        </div>
      </div>
    </aside>
  );
}

export default AppSidebar;
