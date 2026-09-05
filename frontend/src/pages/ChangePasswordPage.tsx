import {
  type FormEvent,
  useState,
} from "react";

import {
  Eye,
  EyeOff,
} from "lucide-react";

import {
  useNavigate,
} from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { changePassword } from "../services/authApi";

function ChangePasswordPage() {
  const {
    user,
    updateUser,
  } = useAuth();

  const navigate = useNavigate();

  const [currentPassword, setCurrentPassword] =
    useState("");

  const [newPassword, setNewPassword] =
    useState("");

  const [confirmPassword, setConfirmPassword] =
    useState("");

  const [showCurrentPassword, setShowCurrentPassword] =
    useState(false);

  const [showNewPassword, setShowNewPassword] =
    useState(false);

  const [showConfirmPassword, setShowConfirmPassword] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const [success, setSuccess] =
    useState<string | null>(null);

  const [isSubmitting, setIsSubmitting] =
    useState(false);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ): Promise<void> {
    event.preventDefault();

    setError(null);
    setSuccess(null);

    if (!currentPassword) {
      setError("Informe a senha atual.");
      return;
    }

    if (!newPassword) {
      setError("Informe a nova senha.");
      return;
    }

    if (!confirmPassword) {
      setError("Confirme a nova senha.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setError(
        "A confirmação da nova senha não confere.",
      );
      return;
    }

    if (currentPassword === newPassword) {
      setError(
        "A nova senha deve ser diferente da senha atual.",
      );
      return;
    }

    if (isSubmitting) {
      return;
    }

    setIsSubmitting(true);

    try {
      const updatedUser = await changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });

      updateUser(updatedUser);

      setSuccess(
        "Senha alterada com sucesso. Redirecionando...",
      );

      window.setTimeout(() => {
        navigate("/dashboard", {
          replace: true,
        });
      }, 800);
    } catch {
      setError(
        "Não foi possível alterar a senha. Verifique a senha atual e tente novamente.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="login-page">
      <section
        className="login-card"
        aria-label="Alteração de senha"
      >
        <div className="login-header">
          <h1>OuroBuild</h1>

          <p>
            Primeiro acesso
          </p>
        </div>

        <div className="login-header">
          <h2>
            Troque sua senha
          </h2>

          <p>
            Por segurança, você precisa definir uma nova
            senha antes de continuar.
          </p>

          {user?.display_name && (
            <p>
              Usuário: <strong>{user.display_name}</strong>
            </p>
          )}
        </div>

        <form
          className="login-form"
          onSubmit={handleSubmit}
          noValidate
        >
          <div className="form-field">
            <label htmlFor="current-password">
              Senha atual
            </label>

            <div
              style={{
                position: "relative",
              }}
            >
              <input
                id="current-password"
                name="current-password"
                type={
                  showCurrentPassword
                    ? "text"
                    : "password"
                }
                autoComplete="current-password"
                value={currentPassword}
                onChange={(event) => {
                  setCurrentPassword(
                    event.target.value,
                  );

                  if (error) {
                    setError(null);
                  }
                }}
                disabled={isSubmitting}
                required
                autoFocus
                style={{
                  paddingRight: "44px",
                }}
              />

              <button
                type="button"
                aria-label={
                  showCurrentPassword
                    ? "Ocultar senha atual"
                    : "Mostrar senha atual"
                }
                title={
                  showCurrentPassword
                    ? "Ocultar senha atual"
                    : "Mostrar senha atual"
                }
                onClick={() =>
                  setShowCurrentPassword(
                    (current) => !current,
                  )
                }
                disabled={isSubmitting}
                style={{
                  position: "absolute",
                  top: "50%",
                  right: "8px",
                  transform:
                    "translateY(-50%)",
                  width: "32px",
                  height: "32px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  padding: 0,
                  border: 0,
                  borderRadius: "6px",
                  background: "transparent",
                  color: "#64748b",
                  cursor: isSubmitting
                    ? "not-allowed"
                    : "pointer",
                }}
              >
                {showCurrentPassword ? (
                  <EyeOff size={17} />
                ) : (
                  <Eye size={17} />
                )}
              </button>
            </div>
          </div>

          <div className="form-field">
            <label htmlFor="new-password">
              Nova senha
            </label>

            <div
              style={{
                position: "relative",
              }}
            >
              <input
                id="new-password"
                name="new-password"
                type={
                  showNewPassword
                    ? "text"
                    : "password"
                }
                autoComplete="new-password"
                value={newPassword}
                onChange={(event) => {
                  setNewPassword(
                    event.target.value,
                  );

                  if (error) {
                    setError(null);
                  }
                }}
                disabled={isSubmitting}
                required
                style={{
                  paddingRight: "44px",
                }}
              />

              <button
                type="button"
                aria-label={
                  showNewPassword
                    ? "Ocultar nova senha"
                    : "Mostrar nova senha"
                }
                title={
                  showNewPassword
                    ? "Ocultar nova senha"
                    : "Mostrar nova senha"
                }
                onClick={() =>
                  setShowNewPassword(
                    (current) => !current,
                  )
                }
                disabled={isSubmitting}
                style={{
                  position: "absolute",
                  top: "50%",
                  right: "8px",
                  transform:
                    "translateY(-50%)",
                  width: "32px",
                  height: "32px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  padding: 0,
                  border: 0,
                  borderRadius: "6px",
                  background: "transparent",
                  color: "#64748b",
                  cursor: isSubmitting
                    ? "not-allowed"
                    : "pointer",
                }}
              >
                {showNewPassword ? (
                  <EyeOff size={17} />
                ) : (
                  <Eye size={17} />
                )}
              </button>
            </div>
          </div>

          <div className="form-field">
            <label htmlFor="confirm-password">
              Confirmar nova senha
            </label>

            <div
              style={{
                position: "relative",
              }}
            >
              <input
                id="confirm-password"
                name="confirm-password"
                type={
                  showConfirmPassword
                    ? "text"
                    : "password"
                }
                autoComplete="new-password"
                value={confirmPassword}
                onChange={(event) => {
                  setConfirmPassword(
                    event.target.value,
                  );

                  if (error) {
                    setError(null);
                  }
                }}
                disabled={isSubmitting}
                required
                style={{
                  paddingRight: "44px",
                }}
              />

              <button
                type="button"
                aria-label={
                  showConfirmPassword
                    ? "Ocultar confirmação"
                    : "Mostrar confirmação"
                }
                title={
                  showConfirmPassword
                    ? "Ocultar confirmação"
                    : "Mostrar confirmação"
                }
                onClick={() =>
                  setShowConfirmPassword(
                    (current) => !current,
                  )
                }
                disabled={isSubmitting}
                style={{
                  position: "absolute",
                  top: "50%",
                  right: "8px",
                  transform:
                    "translateY(-50%)",
                  width: "32px",
                  height: "32px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  padding: 0,
                  border: 0,
                  borderRadius: "6px",
                  background: "transparent",
                  color: "#64748b",
                  cursor: isSubmitting
                    ? "not-allowed"
                    : "pointer",
                }}
              >
                {showConfirmPassword ? (
                  <EyeOff size={17} />
                ) : (
                  <Eye size={17} />
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

          {success && (
            <div
              className="login-success"
              role="status"
              aria-live="polite"
            >
              {success}
            </div>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting
              ? "Alterando..."
              : "Alterar senha"}
          </button>
        </form>
      </section>
    </main>
  );
}

export default ChangePasswordPage;