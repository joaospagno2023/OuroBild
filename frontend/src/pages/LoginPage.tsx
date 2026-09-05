import {
  type FormEvent,
  useState,
} from "react";
import {
  Navigate,
  useNavigate,
} from "react-router-dom";

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
    setIsSubmitting(true);

    try {
      const response =
        await login({
          username: username.trim(),
          password,
        });

      setAuthenticated(
        response.access_token,
      );

      navigate(
        "/dashboard",
        {
          replace: true,
        },
      );
    } catch (error) {
      if (
        error instanceof Error &&
        error.message
      ) {
        setError(
          "Usuário ou senha inválidos.",
        );
      } else {
        setError(
          "Não foi possível realizar o login.",
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="login-page">
      <section className="login-card">
        <div className="login-header">
          <h1>OuroBuild</h1>

          <p>
            Automação de Builds e Setups
          </p>
        </div>

        <form
          className="login-form"
          onSubmit={handleSubmit}
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
              value={username}
              onChange={(event) =>
                setUsername(
                  event.target.value,
                )
              }
              disabled={isSubmitting}
              required
            />
          </div>

          <div className="form-field">
            <label htmlFor="password">
              Senha
            </label>

            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) =>
                setPassword(
                  event.target.value,
                )
              }
              disabled={isSubmitting}
              required
            />
          </div>

          {error && (
            <div
              className="login-error"
              role="alert"
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