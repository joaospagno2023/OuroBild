import {
  type FormEvent,
  useState,
} from "react";

import {
  CheckCircle2,
  Eye,
  EyeOff,
  KeyRound,
  Save,
  UserRound,
} from "lucide-react";

import {
  useAuth,
} from "../auth/AuthContext";

import {
  changePassword,
  updateProfile,
} from "../services/authApi";


function ProfilePage() {
  const {
    user,
    updateUser,
  } = useAuth();

  const [displayName, setDisplayName] =
    useState(
      user?.display_name ??
        user?.username ??
        "",
    );

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

  const [isSavingProfile, setIsSavingProfile] =
    useState(false);

  const [isChangingPassword, setIsChangingPassword] =
    useState(false);

  const [profileMessage, setProfileMessage] =
    useState<string | null>(null);

  const [profileError, setProfileError] =
    useState<string | null>(null);

  const [passwordMessage, setPasswordMessage] =
    useState<string | null>(null);

  const [passwordError, setPasswordError] =
    useState<string | null>(null);

  if (!user) {
    return null;
  }

  async function handleProfileSubmit(
    event: FormEvent<HTMLFormElement>,
  ): Promise<void> {
    event.preventDefault();

    setProfileMessage(null);
    setProfileError(null);

    const normalizedDisplayName =
      displayName.trim();

    if (!normalizedDisplayName) {
      setProfileError(
        "Informe o nome de exibição.",
      );
      return;
    }

    if (isSavingProfile) {
      return;
    }

    setIsSavingProfile(true);

    try {
      const updatedUser =
        await updateProfile({
          display_name:
            normalizedDisplayName,
        });

      updateUser(updatedUser);

      setDisplayName(
        updatedUser.display_name ??
          updatedUser.username,
      );

      setProfileMessage(
        "Nome atualizado com sucesso.",
      );
    } catch {
      setProfileError(
        "Não foi possível atualizar o nome.",
      );
    } finally {
      setIsSavingProfile(false);
    }
  }

  async function handlePasswordSubmit(
    event: FormEvent<HTMLFormElement>,
  ): Promise<void> {
    event.preventDefault();

    setPasswordMessage(null);
    setPasswordError(null);

    if (!currentPassword) {
      setPasswordError(
        "Informe a senha atual.",
      );
      return;
    }

    if (!newPassword) {
      setPasswordError(
        "Informe a nova senha.",
      );
      return;
    }

    if (newPassword.length < 6) {
      setPasswordError(
        "A nova senha deve possuir pelo menos 6 caracteres.",
      );
      return;
    }

    if (!confirmPassword) {
      setPasswordError(
        "Confirme a nova senha.",
      );
      return;
    }

    if (newPassword !== confirmPassword) {
      setPasswordError(
        "A confirmação da nova senha não confere.",
      );
      return;
    }

    if (currentPassword === newPassword) {
      setPasswordError(
        "A nova senha deve ser diferente da senha atual.",
      );
      return;
    }

    if (isChangingPassword) {
      return;
    }

    setIsChangingPassword(true);

    try {
      const updatedUser =
        await changePassword({
          current_password:
            currentPassword,
          new_password:
            newPassword,
        });

      updateUser(updatedUser);

      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");

      setPasswordMessage(
        "Senha alterada com sucesso.",
      );
    } catch {
      setPasswordError(
        "Não foi possível alterar a senha. Verifique a senha atual e tente novamente.",
      );
    } finally {
      setIsChangingPassword(false);
    }
  }

  return (
    <section>
      <div className="page-heading">
        <div>
          <span className="page-eyebrow">
            MINHA CONTA
          </span>

          <h1>
            Meu perfil
          </h1>

          <p>
            Gerencie seus dados de acesso ao OuroBuild.
          </p>
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "minmax(0, 1fr) minmax(0, 1fr)",
          gap: "18px",
          alignItems: "start",
        }}
      >
        <section className="content-card">
          <div className="card-header">
            <div>
              <h2>
                Dados do perfil
              </h2>

              <p>
                Altere o nome apresentado no sistema.
              </p>
            </div>

            <UserRound size={20} />
          </div>

          <form
            onSubmit={handleProfileSubmit}
          >
            <div className="form-grid">
              <div
                className="form-field"
                style={{
                  gridColumn:
                    "1 / -1",
                }}
              >
                <label htmlFor="display-name">
                  Nome
                </label>

                <input
                  id="display-name"
                  name="display-name"
                  type="text"
                  autoComplete="name"
                  value={displayName}
                  onChange={(
                    event,
                  ) => {
                    setDisplayName(
                      event.target.value,
                    );
                    setProfileMessage(
                      null,
                    );
                    setProfileError(
                      null,
                    );
                  }}
                  disabled={
                    isSavingProfile
                  }
                  maxLength={200}
                  required
                />
              </div>

              <div className="form-field">
                <label htmlFor="username">
                  Usuário
                </label>

                <input
                  id="username"
                  type="text"
                  value={
                    user.username
                  }
                  disabled
                  readOnly
                />
              </div>

              <div className="form-field">
                <label htmlFor="email">
                  E-mail
                </label>

                <input
                  id="email"
                  type="email"
                  value={
                    user.email ??
                    ""
                  }
                  disabled
                  readOnly
                />
              </div>
            </div>

            {profileError && (
              <div
                className="error-message"
                role="alert"
                aria-live="polite"
                style={{
                  marginTop: "16px",
                }}
              >
                {profileError}
              </div>
            )}

            {profileMessage && (
              <div
                role="status"
                aria-live="polite"
                style={{
                  display:
                    "flex",
                  alignItems:
                    "center",
                  gap: "8px",
                  marginTop:
                    "16px",
                  padding:
                    "10px 12px",
                  border:
                    "1px solid #bbf7d0",
                  borderRadius:
                    "8px",
                  background:
                    "#f0fdf4",
                  color:
                    "#166534",
                  fontSize:
                    "12px",
                }}
              >
                <CheckCircle2
                  size={16}
                />

                {profileMessage}
              </div>
            )}

            <div
              style={{
                display:
                  "flex",
                justifyContent:
                  "flex-end",
                marginTop:
                  "20px",
              }}
            >
              <button
                type="submit"
                className="primary-button"
                disabled={
                  isSavingProfile
                }
              >
                <Save size={15} />

                {isSavingProfile
                  ? "Salvando..."
                  : "Salvar alterações"}
              </button>
            </div>
          </form>
        </section>

        <section className="content-card">
          <div className="card-header">
            <div>
              <h2>
                Alterar senha
              </h2>

              <p>
                Defina uma nova senha para sua conta.
              </p>
            </div>

            <KeyRound size={20} />
          </div>

          <form
            onSubmit={
              handlePasswordSubmit
            }
          >
            <div
              className="form-field"
            >
              <label htmlFor="current-password">
                Senha atual
              </label>

              <div
                style={{
                  position:
                    "relative",
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
                  value={
                    currentPassword
                  }
                  onChange={(
                    event,
                  ) => {
                    setCurrentPassword(
                      event.target.value,
                    );

                    setPasswordError(
                      null,
                    );
                    setPasswordMessage(
                      null,
                    );
                  }}
                  disabled={
                    isChangingPassword
                  }
                  required
                  style={{
                    paddingRight:
                      "44px",
                  }}
                />

                <button
                  type="button"
                  onClick={() =>
                    setShowCurrentPassword(
                      (
                        value,
                      ) =>
                        !value,
                    )
                  }
                  disabled={
                    isChangingPassword
                  }
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
                  style={{
                    position:
                      "absolute",
                    top:
                      "50%",
                    right:
                      "8px",
                    transform:
                      "translateY(-50%)",
                    width:
                      "32px",
                    height:
                      "32px",
                    display:
                      "flex",
                    alignItems:
                      "center",
                    justifyContent:
                      "center",
                    padding:
                      0,
                    border:
                      0,
                    borderRadius:
                      "6px",
                    background:
                      "transparent",
                    color:
                      "#64748b",
                    cursor:
                      isChangingPassword
                        ? "not-allowed"
                        : "pointer",
                  }}
                >
                  {showCurrentPassword ? (
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

            <div
              className="form-field"
              style={{
                marginTop:
                  "16px",
              }}
            >
              <label htmlFor="new-password">
                Nova senha
              </label>

              <div
                style={{
                  position:
                    "relative",
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
                  value={
                    newPassword
                  }
                  onChange={(
                    event,
                  ) => {
                    setNewPassword(
                      event.target.value,
                    );

                    setPasswordError(
                      null,
                    );
                    setPasswordMessage(
                      null,
                    );
                  }}
                  disabled={
                    isChangingPassword
                  }
                  required
                  style={{
                    paddingRight:
                      "44px",
                  }}
                />

                <button
                  type="button"
                  onClick={() =>
                    setShowNewPassword(
                      (
                        value,
                      ) =>
                        !value,
                    )
                  }
                  disabled={
                    isChangingPassword
                  }
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
                  style={{
                    position:
                      "absolute",
                    top:
                      "50%",
                    right:
                      "8px",
                    transform:
                      "translateY(-50%)",
                    width:
                      "32px",
                    height:
                      "32px",
                    display:
                      "flex",
                    alignItems:
                      "center",
                    justifyContent:
                      "center",
                    padding:
                      0,
                    border:
                      0,
                    borderRadius:
                      "6px",
                    background:
                      "transparent",
                    color:
                      "#64748b",
                    cursor:
                      isChangingPassword
                        ? "not-allowed"
                        : "pointer",
                  }}
                >
                  {showNewPassword ? (
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

            <div
              className="form-field"
              style={{
                marginTop:
                  "16px",
              }}
            >
              <label htmlFor="confirm-password">
                Confirmar nova senha
              </label>

              <div
                style={{
                  position:
                    "relative",
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
                  value={
                    confirmPassword
                  }
                  onChange={(
                    event,
                  ) => {
                    setConfirmPassword(
                      event.target.value,
                    );

                    setPasswordError(
                      null,
                    );
                    setPasswordMessage(
                      null,
                    );
                  }}
                  disabled={
                    isChangingPassword
                  }
                  required
                  style={{
                    paddingRight:
                      "44px",
                  }}
                />

                <button
                  type="button"
                  onClick={() =>
                    setShowConfirmPassword(
                      (
                        value,
                      ) =>
                        !value,
                    )
                  }
                  disabled={
                    isChangingPassword
                  }
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
                  style={{
                    position:
                      "absolute",
                    top:
                      "50%",
                    right:
                      "8px",
                    transform:
                      "translateY(-50%)",
                    width:
                      "32px",
                    height:
                      "32px",
                    display:
                      "flex",
                    alignItems:
                      "center",
                    justifyContent:
                      "center",
                    padding:
                      0,
                    border:
                      0,
                    borderRadius:
                      "6px",
                    background:
                      "transparent",
                    color:
                      "#64748b",
                    cursor:
                      isChangingPassword
                        ? "not-allowed"
                        : "pointer",
                  }}
                >
                  {showConfirmPassword ? (
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

            {passwordError && (
              <div
                className="error-message"
                role="alert"
                aria-live="polite"
                style={{
                  marginTop:
                    "16px",
                }}
              >
                {passwordError}
              </div>
            )}

            {passwordMessage && (
              <div
                role="status"
                aria-live="polite"
                style={{
                  display:
                    "flex",
                  alignItems:
                    "center",
                  gap: "8px",
                  marginTop:
                    "16px",
                  padding:
                    "10px 12px",
                  border:
                    "1px solid #bbf7d0",
                  borderRadius:
                    "8px",
                  background:
                    "#f0fdf4",
                  color:
                    "#166534",
                  fontSize:
                    "12px",
                }}
              >
                <CheckCircle2
                  size={16}
                />

                {passwordMessage}
              </div>
            )}

            <div
              style={{
                display:
                  "flex",
                justifyContent:
                  "flex-end",
                marginTop:
                  "20px",
              }}
            >
              <button
                type="submit"
                className="primary-button"
                disabled={
                  isChangingPassword
                }
              >
                <KeyRound size={15} />

                {isChangingPassword
                  ? "Alterando..."
                  : "Alterar senha"}
              </button>
            </div>
          </form>
        </section>
      </div>
    </section>
  );
}

export default ProfilePage;