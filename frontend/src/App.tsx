import {
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import ProtectedRoute from "./auth/ProtectedRoute";
import AppLayout from "./layouts/AppLayout";
import AdministrationPage from "./pages/AdministrationPage";
import DashboardPage from "./pages/DashboardPage";
import HistoryPage from "./pages/HistoryPage";
import LoginPage from "./pages/LoginPage";
import LogsPage from "./pages/LogsPage";
import SetupPage from "./pages/SetupPage";
import UsersPage from "./pages/UsersPage";

function App() {
  return (
    <Routes>
      <Route
        path="/login"
        element={<LoginPage />}
      />

      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route
            path="/"
            element={
              <Navigate
                to="/dashboard"
                replace
              />
            }
          />

          <Route
            path="/dashboard"
            element={<DashboardPage />}
          />

          <Route
            path="/setups"
            element={<SetupPage />}
          />

          <Route
            path="/history"
            element={<HistoryPage />}
          />

          <Route
            path="/logs"
            element={<LogsPage />}
          />

          <Route
            path="/users"
            element={<UsersPage />}
          />

          <Route
            path="/administration"
            element={
              <AdministrationPage />
            }
          />
        </Route>
      </Route>

      <Route
        path="*"
        element={
          <Navigate
            to="/dashboard"
            replace
          />
        }
      />
    </Routes>
  );
}

export default App;