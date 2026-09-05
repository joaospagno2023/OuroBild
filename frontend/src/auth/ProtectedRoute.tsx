import {
  Navigate,
  Outlet,
  useLocation,
} from "react-router-dom";

import { useAuth } from "./AuthContext";

function ProtectedRoute() {
  const {
    isAuthenticated,
    isLoading,
  } = useAuth();

  const location =
    useLocation();

  if (isLoading) {
    return (
      <div className="auth-loading">
        <span>Carregando...</span>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
        state={{
          from: location.pathname,
        }}
      />
    );
  }

  return <Outlet />;
}

export default ProtectedRoute;