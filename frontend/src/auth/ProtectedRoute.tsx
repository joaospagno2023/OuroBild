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
    user,
  } = useAuth();

  const location = useLocation();

  if (isLoading) {
    return (
      <main className="login-page">
        <section className="login-card">
          <div className="login-header">
            <h1>OuroBuild</h1>
            <p>Validando sessão...</p>
          </div>
        </section>
      </main>
    );
  }

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: location.pathname }}
      />
    );
  }

  const isChangingPassword =
    location.pathname === "/change-password";

  if (
    user?.must_change_password &&
    !isChangingPassword
  ) {
    return (
      <Navigate
        to="/change-password"
        replace
      />
    );
  }

  return <Outlet />;
}

export default ProtectedRoute;