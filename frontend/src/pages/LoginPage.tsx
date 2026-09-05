import {
  type FormEvent,
  useState,
} from "react";

import {
  Navigate,
  useNavigate,
} from "react-router-dom";

import {
  Eye,
  EyeOff,
} from "lucide-react";

import { useAuth } from "../auth/AuthContext";
import {
  login,
} from "../services/authApi";

function LoginPage() {
  const {
    isAuthenticated,
    setAuthenticated,
  } = useAuth();

  const navigate =
    useNavigate();

  const [
    username,
    setUsername,
  ] = useState("");

  const [
    password,
    setPassword,
  ] = useState("");

  const [
    showPassword,
    setShowPassword,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<string | null>(
    null,
  );

  const [
    isSubmitting,
    setIsSubmitting,
  ] = useState(false);

  if (isAuthenticated) {
    return (
      <Navigate
        to="/dashboard"
        replace
      />
    );
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ): Promise<void> {
    event.preventDefault();

    setError(null);

    const normalizedUsername =
      username.trim();

    if (!normalizedUsername) {
      setError(
        "Informe o usuário.",
      );

      return;
    }

    if (!password) {
      setError(
        "Informe a senha.",
      );

      return;
    }

    if (isSubmitting) {
      return;
    }

    setIsSubmitting(true);

    try {
      const response =
        await login({
          username: normalizedUsername,
          password,
        });

      setAuthenticated(
        response.access_token,
      );

      if (response.must_change_password) {
        navigate(
          "/change-password",
          {
            replace: true,
          },
        );

        return;
      }

      navigate(
        "/dashboard",
        {
          replace: true,
        },
      );
    } catch {
      setError(
        "Usuário ou senha inválidos.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="login-page">
      <section
        className="login-card"
        aria-label="Login do OuroBuild"
      >
        <div className="login-header">
          <h1>
            OuroBuild
          </h1>

          <p>
            Automação de Builds e Setups
          </p>
        </div>

        <form
          className="login-form"
          onSubmit={handleSubmit}
          noValidate
        >
          <div className="form-field">
            <label htmlFor="username">
              Usuário
            </label>

            <input
              id="username"
              name="username"
              type="text"
              autoComplete="username"
              autoFocus
              value={username}
              onChange={(event) => {
                setUsername(
                  event.target.value,
                );

                if (error) {
                  setError(null);
                }
              }}
              disabled={isSubmitting}
              required
            />
          </div>

          <div className="form-field">
            <label htmlFor="password">
              Senha
            </label>

            <div
              style={{
                position:
                  "relative",
              }}
            >
              <input
                id="password"
                name="password"
                type={
                  showPassword
                    ? "text"
                    : "password"
                }
                autoComplete="current-password"
                value={password}
                onChange={(event) => {
                  setPassword(
                    event.target.value,
                  );

                  if (error) {
                    setError(null);
                  }
                }}
                disabled={isSubmitting}
                required
                style={{
                  paddingRight:
                    "44px",
                }}
              />

              <button
                type="button"
                aria-label={
                  showPassword
                    ? "Ocultar senha"
                    : "Mostrar senha"
                }
                title={
                  showPassword
                    ? "Ocultar senha"
                    : "Mostrar senha"
                }
                onClick={() =>
                  setShowPassword(
                    (current) =>
                      !current,
                  )
                }
                disabled={isSubmitting}
                style={{
                  position:
                    "absolute",
                  top: "50%",
                  right: "8px",
                  transform:
                    "translateY(-50%)",
                  width: "32px",
                  height: "32px",
                  display: "flex",
                  alignItems:
                    "center",
                  justifyContent:
                    "center",
                  padding: 0,
                  border: 0,
                  borderRadius:
                    "6px",
                  background:
                    "transparent",
                  color: "#64748b",
                  cursor:
                    isSubmitting
                      ? "not-allowed"
                      : "pointer",
                }}
              >
                {showPassword ? (
                  <EyeOff
                    size={17}
                  />
                ) : (
                  <Eye
                    size={17}
                  />
                )}
              </button>
            </div>
          </div>

          {error && (
            <div
              className="login-error"
              role="alert"
              aria-live="polite"
            >
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={
              isSubmitting
            }
          >
            {isSubmitting
              ? "Entrando..."
              : "Entrar"}
          </button>
        </form>
      </section>
    </main>
  );
}

export default LoginPage;