
import { useState } from "react";
import { Outlet } from "react-router-dom";

import AppHeader from "../components/AppHeader";
import AppSidebar from "../components/AppSidebar";

function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="app-shell">
      <AppSidebar />

      {sidebarOpen && (
        <button
          className="sidebar-overlay"
          type="button"
          aria-label="Fechar menu"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <main className="main-area">
        <AppHeader
          onMenuClick={() =>
            setSidebarOpen((value) => !value)
          }
        />

        <div className="page-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

export default AppLayout;
