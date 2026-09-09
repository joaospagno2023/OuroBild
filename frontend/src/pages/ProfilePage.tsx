import { type FormEvent, useState } from "react";
import {
  CheckCircle2,
  Eye,
  EyeOff,
  KeyRound,
  Mail,
  Save,
  UserRound,
} from "lucide-react";
import { useAuth } from "../auth/AuthContext";
import {
  changePassword,
  updateProfile,
} from "../services/authApi";

function ProfilePage() {
  const { user, updateUser } = useAuth();

  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [profileLoaded, setProfileLoaded] = useState(false);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [profileMessage, setProfileMessage] = useState<string | null>(null);
  const [profileError, setProfileError] = useState<string | null>(null);
  const [passwordMessage, setPasswordMessage] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);

  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);

  if (!user) {
    return null;
  }

  if (!profileLoaded) {
    setDisplayName(user.display_name ?? user.username);
    setEmail(user.email ?? "");
    setProfileLoaded(true);
  }

  async function handleProfileSubmit(
    event: FormEvent<HTMLFormElement>,
  ): Promise<void> {
    event.preventDefault();

    setProfileMessage(null);
    setProfileError(null);

    const normalizedDisplayName = displayName.trim();
    const normalizedEmail = email.trim();

    if (!normalizedDisplayName) {
      setProfileError("Informe o nome.");
      return;
    }

    if (
      normalizedEmail &&
      !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalizedEmail)
    ) {
      setProfileError("Informe um e-mail válido.");
      return;
    }

    setIsSavingProfile(true);

    try {
      const updatedUser = await updateProfile({
        display_name: normalizedDisplayName,
        email: normalizedEmail || null,
      });

      updateUser(updatedUser);
      setDisplayName(
        updatedUser.display_name ??
          updatedUser.username,
      );
      setEmail(updatedUser.email ?? "");
      setProfileMessage(
        "Dados do perfil atualizados com sucesso.",
      );
    } catch {
      setProfileError(
        "Não foi possível atualizar os dados do perfil.",
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
      setPasswordError("Informe a senha atual.");
      return;
    }

    if (!newPassword) {
      setPasswordError("Informe a nova senha.");
      return;
    }

    if (newPassword.length < 6) {
      setPasswordError(
        "A nova senha deve possuir pelo menos 6 caracteres.",
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

    setIsChangingPassword(true);

    try {
      const updatedUser = await changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });

      updateUser(updatedUser);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setPasswordMessage("Senha alterada com sucesso.");
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
          <span className="page-eyebrow">MINHA CONTA</span>
          <h1>Meu perfil</h1>
          <p>Gerencie seus dados de acesso ao OuroBuild.</p>
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(2, minmax(0, 1fr))",
          gap: "18px",
          alignItems: "start",
        }}
      >
        <section className="content-card">
          <div className="card-header">
            <div>
              <h2>Dados do perfil</h2>
              <p>Atualize seu nome e seu e-mail.</p>
            </div>
            <UserRound size={20} />
          </div>

          <form onSubmit={handleProfileSubmit}>
            <div className="form-grid">
              <div
                className="form-field"
                style={{ gridColumn: "1 / -1" }}
              >
                <label htmlFor="profile-display-name">
                  Nome
                </label>
                <input
                  id="profile-display-name"
                  type="text"
                  value={displayName}
                  onChange={(event) => {
                    setDisplayName(event.target.value);
                    setProfileError(null);
                    setProfileMessage(null);
                  }}
                  disabled={isSavingProfile}
                  maxLength={200}
                  required
                />
              </div>

              <div className="form-field">
                <label htmlFor="profile-username">
                  Usuário
                </label>
                <input
                  id="profile-username"
                  type="text"
                  value={user.username}
                  disabled
                  readOnly
                />
              </div>

              <div className="form-field">
                <label htmlFor="profile-email">E-mail</label>
                <div style={{ position: "relative" }}>
                  <Mail
                    size={16}
                    style={{
                      position: "absolute",
                      left: "12px",
                      top: "50%",
                      transform: "translateY(-50%)",
                      color: "#94a3b8",
                    }}
                  />
                  <input
                    id="profile-email"
                    type="email"
                    value={email}
                    onChange={(event) => {
                      setEmail(event.target.value);
                      setProfileError(null);
                      setProfileMessage(null);
                    }}
                    disabled={isSavingProfile}
                    placeholder="seu@email.com"
                    style={{ paddingLeft: "36px" }}
                  />
                </div>
              </div>
            </div>

            {profileError && (
              <div
                className="error-message"
                role="alert"
                style={{ marginTop: "16px" }}
              >
                {profileError}
              </div>
            )}

            {profileMessage && (
              <div
                role="status"
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  marginTop: "16px",
                  padding: "10px 12px",
                  border: "1px solid #bbf7d0",
                  borderRadius: "8px",
                  background: "#f0fdf4",
                  color: "#166534",
                  fontSize: "12px",
                }}
              >
                <CheckCircle2 size={16} />
                {profileMessage}
              </div>
            )}

            <div
              style={{
                display: "flex",
                justifyContent: "flex-end",
                marginTop: "20px",
              }}
            >
              <button
                type="submit"
                className="primary-button"
                disabled={isSavingProfile}
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
              <h2>Alterar senha</h2>
              <p>Troque a senha de acesso da sua conta.</p>
            </div>
            <KeyRound size={20} />
          </div>

          <form onSubmit={handlePasswordSubmit}>
            <div className="form-field">
              <label htmlFor="profile-current-password">
                Senha atual
              </label>
              <div style={{ position: "relative" }}>
                <input
                  id="profile-current-password"
                  type={showCurrentPassword ? "text" : "password"}
                  value={currentPassword}
                  onChange={(event) => {
                    setCurrentPassword(event.target.value);
                    setPasswordError(null);
                    setPasswordMessage(null);
                  }}
                  disabled={isChangingPassword}
                  autoComplete="current-password"
                  required
                  style={{ paddingRight: "44px" }}
                />
                <button
                  type="button"
                  onClick={() =>
                    setShowCurrentPassword((value) => !value)
                  }
                  disabled={isChangingPassword}
                  aria-label={
                    showCurrentPassword
                      ? "Ocultar senha atual"
                      : "Mostrar senha atual"
                  }
                  style={passwordEyeButtonStyle}
                >
                  {showCurrentPassword ? (
                    <EyeOff size={17} />
                  ) : (
                    <Eye size={17} />
                  )}
                </button>
              </div>
            </div>

            <div className="form-field" style={{ marginTop: "16px" }}>
              <label htmlFor="profile-new-password">Nova senha</label>
              <div style={{ position: "relative" }}>
                <input
                  id="profile-new-password"
                  type={showNewPassword ? "text" : "password"}
                  value={newPassword}
                  onChange={(event) => {
                    setNewPassword(event.target.value);
                    setPasswordError(null);
                    setPasswordMessage(null);
                  }}
                  disabled={isChangingPassword}
                  autoComplete="new-password"
                  required
                  style={{ paddingRight: "44px" }}
                />
                <button
                  type="button"
                  onClick={() =>
                    setShowNewPassword((value) => !value)
                  }
                  disabled={isChangingPassword}
                  aria-label={
                    showNewPassword
                      ? "Ocultar nova senha"
                      : "Mostrar nova senha"
                  }
                  style={passwordEyeButtonStyle}
                >
                  {showNewPassword ? (
                    <EyeOff size={17} />
                  ) : (
                    <Eye size={17} />
                  )}
                </button>
              </div>
            </div>

            <div className="form-field" style={{ marginTop: "16px" }}>
              <label htmlFor="profile-confirm-password">
                Confirmar nova senha
              </label>
              <div style={{ position: "relative" }}>
                <input
                  id="profile-confirm-password"
                  type={showConfirmPassword ? "text" : "password"}
                  value={confirmPassword}
                  onChange={(event) => {
                    setConfirmPassword(event.target.value);
                    setPasswordError(null);
                    setPasswordMessage(null);
                  }}
                  disabled={isChangingPassword}
                  autoComplete="new-password"
                  required
                  style={{ paddingRight: "44px" }}
                />
                <button
                  type="button"
                  onClick={() =>
                    setShowConfirmPassword((value) => !value)
                  }
                  disabled={isChangingPassword}
                  aria-label={
                    showConfirmPassword
                      ? "Ocultar confirmação"
                      : "Mostrar confirmação"
                  }
                  style={passwordEyeButtonStyle}
                >
                  {showConfirmPassword ? (
                    <EyeOff size={17} />
                  ) : (
                    <Eye size={17} />
                  )}
                </button>
              </div>
            </div>

            {passwordError && (
              <div
                className="error-message"
                role="alert"
                style={{ marginTop: "16px" }}
              >
                {passwordError}
              </div>
            )}

            {passwordMessage && (
              <div
                role="status"
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  marginTop: "16px",
                  padding: "10px 12px",
                  border: "1px solid #bbf7d0",
                  borderRadius: "8px",
                  background: "#f0fdf4",
                  color: "#166534",
                  fontSize: "12px",
                }}
              >
                <CheckCircle2 size={16} />
                {passwordMessage}
              </div>
            )}

            <div
              style={{
                display: "flex",
                justifyContent: "flex-end",
                marginTop: "20px",
              }}
            >
              <button
                type="submit"
                className="primary-button"
                disabled={isChangingPassword}
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

const passwordEyeButtonStyle = {
  position: "absolute" as const,
  top: "50%",
  right: "8px",
  transform: "translateY(-50%)",
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
  cursor: "pointer",
};

export default ProfilePage;
