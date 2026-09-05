import {
  type FormEvent,
  useEffect,
  useState,
} from "react";

import {
  CircleCheck,
  CircleX,
  Clipboard,
  Eye,
  EyeOff,
  LoaderCircle,
  Plus,
  Save,
  UserPlus,
  Users,
  X,
} from "lucide-react";

import {
  createUser,
  getUsers,
  resetUserPassword,
  updateUser,
  updateUserStatus,
  type User,
} from "../services/usersApi";

type UsersPageMode =
  | "list"
  | "create"
  | "edit";

interface ResetPasswordResult {
  username: string;
  temporaryPassword: string;
}

function UsersPage() {
  const [mode, setMode] =
    useState<UsersPageMode>("list");

  const [users, setUsers] =
    useState<User[]>([]);

  const [isLoadingUsers, setIsLoadingUsers] =
    useState(true);

  const [isRefreshingUsers, setIsRefreshingUsers] =
    useState(false);

  const [updatingStatusUserId, setUpdatingStatusUserId] =
    useState<number | null>(null);

  const [resettingPasswordUserId, setResettingPasswordUserId] =
    useState<number | null>(null);

  const [resetPasswordResult, setResetPasswordResult] =
    useState<ResetPasswordResult | null>(null);

  const [editingUserId, setEditingUserId] =
    useState<number | null>(null);

  const [username, setUsername] =
    useState("");

  const [displayName, setDisplayName] =
    useState("");

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [confirmPassword, setConfirmPassword] =
    useState("");

  const [isActive, setIsActive] =
    useState(true);

  const [mustChangePassword, setMustChangePassword] =
    useState(true);

  const [showPassword, setShowPassword] =
    useState(false);

  const [showConfirmPassword, setShowConfirmPassword] =
    useState(false);

  const [isSubmitting, setIsSubmitting] =
    useState(false);

  const [successMessage, setSuccessMessage] =
    useState<string | null>(null);

  const [errorMessage, setErrorMessage] =
    useState<string | null>(null);

  function clearMessages(): void {
    setSuccessMessage(null);
    setErrorMessage(null);
  }

  function resetForm(): void {
    setEditingUserId(null);
    setUsername("");
    setDisplayName("");
    setEmail("");
    setPassword("");
    setConfirmPassword("");
    setIsActive(true);
    setMustChangePassword(true);
    setShowPassword(false);
    setShowConfirmPassword(false);
  }

  function handleNewUser(): void {
    clearMessages();
    setResetPasswordResult(null);
    resetForm();
    setMode("create");
  }

  function handleEditUser(
    user: User,
  ): void {
    clearMessages();
    setResetPasswordResult(null);

    setEditingUserId(user.id);
    setUsername(user.username);
    setDisplayName(
      user.display_name,
    );
    setEmail(
      user.email || "",
    );
    setPassword("");
    setConfirmPassword("");
    setIsActive(
      user.is_active,
    );
    setMustChangePassword(
      user.must_change_password,
    );
    setShowPassword(false);
    setShowConfirmPassword(false);
    setMode("edit");
  }

  function handleCancel(): void {
    clearMessages();
    setResetPasswordResult(null);
    resetForm();
    setMode("list");
  }

  async function loadUsers(
    showRefreshState = false,
  ): Promise<void> {
    if (showRefreshState) {
      setIsRefreshingUsers(true);
    } else {
      setIsLoadingUsers(true);
    }

    try {
      const result =
        await getUsers();

      setUsers(result);
    } catch {
      setErrorMessage(
        "Não foi possível carregar os usuários.",
      );
    } finally {
      setIsLoadingUsers(false);
      setIsRefreshingUsers(false);
    }
  }

  useEffect(() => {
    void loadUsers();
  }, []);

  async function handleToggleStatus(
    user: User,
  ): Promise<void> {
    if (
      updatingStatusUserId !== null ||
      resettingPasswordUserId !== null ||
      isSubmitting
    ) {
      return;
    }

    const nextStatus =
      !user.is_active;

    const action =
      nextStatus
        ? "ativar"
        : "desativar";

    const confirmed =
      window.confirm(
        `Deseja ${action} o usuário "${user.username}"?`,
      );

    if (!confirmed) {
      return;
    }

    clearMessages();

    setUpdatingStatusUserId(
      user.id,
    );

    try {
      const updatedUser =
        await updateUserStatus(
          user.id,
          {
            is_active:
              nextStatus,
          },
        );

      setUsers(
        (currentUsers) =>
          currentUsers.map(
            (currentUser) =>
              currentUser.id ===
              updatedUser.id
                ? updatedUser
                : currentUser,
          ),
      );

      setSuccessMessage(
        nextStatus
          ? `Usuário "${user.username}" ativado com sucesso.`
          : `Usuário "${user.username}" desativado com sucesso.`,
      );
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "";

      setErrorMessage(
        message ||
          `Não foi possível ${action} o usuário.`,
      );
    } finally {
      setUpdatingStatusUserId(
        null,
      );
    }
  }

  async function handleResetPassword(
    user: User,
  ): Promise<void> {
    if (
      resettingPasswordUserId !== null ||
      updatingStatusUserId !== null ||
      isSubmitting
    ) {
      return;
    }

    const confirmed =
      window.confirm(
        `Deseja redefinir a senha do usuário "${user.username}"?`,
      );

    if (!confirmed) {
      return;
    }

    clearMessages();
    setResetPasswordResult(null);
    setResettingPasswordUserId(
      user.id,
    );

    try {
      const result =
        await resetUserPassword(
          user.id,
        );

      setUsers(
        (currentUsers) =>
          currentUsers.map(
            (currentUser) =>
              currentUser.id ===
              result.user.id
                ? result.user
                : currentUser,
          ),
      );

      setResetPasswordResult({
        username:
          result.user.username,
        temporaryPassword:
          result.temporary_password,
      });

      setSuccessMessage(
        `Senha do usuário "${user.username}" redefinida com sucesso.`,
      );
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "";

      setErrorMessage(
        message ||
          "Não foi possível redefinir a senha.",
      );
    } finally {
      setResettingPasswordUserId(
        null,
      );
    }
  }

  async function handleCopyTemporaryPassword(): Promise<void> {
    if (
      !resetPasswordResult
    ) {
      return;
    }

    try {
      await navigator.clipboard.writeText(
        resetPasswordResult.temporaryPassword,
      );

      setSuccessMessage(
        "Senha temporária copiada para a área de transferência.",
      );
    } catch {
      setErrorMessage(
        "Não foi possível copiar a senha temporária.",
      );
    }
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ): Promise<void> {
    event.preventDefault();

    if (isSubmitting) {
      return;
    }

    clearMessages();

    const normalizedUsername =
      username.trim();

    const normalizedDisplayName =
      displayName.trim();

    const normalizedEmail =
      email.trim();

    if (!normalizedUsername) {
      setErrorMessage(
        "Informe o usuário.",
      );
      return;
    }

    if (!normalizedDisplayName) {
      setErrorMessage(
        "Informe o nome do usuário.",
      );
      return;
    }

    if (mode === "create") {
      if (!password) {
        setErrorMessage(
          "Informe a senha.",
        );
        return;
      }

      if (password.length < 6) {
        setErrorMessage(
          "A senha deve possuir pelo menos 6 caracteres.",
        );
        return;
      }

      if (!confirmPassword) {
        setErrorMessage(
          "Confirme a senha.",
        );
        return;
      }

      if (
        password !==
        confirmPassword
      ) {
        setErrorMessage(
          "As senhas não conferem.",
        );
        return;
      }
    }

    if (
      mode === "edit" &&
      editingUserId === null
    ) {
      setErrorMessage(
        "Usuário para edição não foi informado.",
      );
      return;
    }

    setIsSubmitting(true);

    try {
      if (mode === "create") {
        await createUser({
          username:
            normalizedUsername,

          display_name:
            normalizedDisplayName,

          email:
            normalizedEmail ||
            null,

          password,

          is_active:
            isActive,

          must_change_password:
            mustChangePassword,
        });

        await loadUsers();

        setSuccessMessage(
          `Usuário "${normalizedUsername}" criado com sucesso.`,
        );
      } else {
        await updateUser(
          editingUserId!,
          {
            display_name:
              normalizedDisplayName,

            email:
              normalizedEmail ||
              null,

            is_active:
              isActive,

            must_change_password:
              mustChangePassword,
          },
        );

        await loadUsers();

        setSuccessMessage(
          `Usuário "${normalizedUsername}" atualizado com sucesso.`,
        );
      }

      resetForm();
      setMode("list");
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "";

      setErrorMessage(
        message ||
          "Não foi possível salvar o usuário.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  function formatDate(
    value?: string | null,
  ): string {
    if (!value) {
      return "—";
    }

    return new Intl.DateTimeFormat(
      "pt-BR",
      {
        dateStyle:
          "short",
        timeStyle:
          "short",
      },
    ).format(
      new Date(value),
    );
  }

  function renderStatus(
    user: User,
  ) {
    if (user.is_active) {
      return (
        <span
          style={{
            display:
              "inline-flex",
            alignItems:
              "center",
            gap: "6px",
            color:
              "#166534",
            fontWeight:
              600,
            fontSize:
              "12px",
          }}
        >
          <CircleCheck
            size={16}
          />

          Ativo
        </span>
      );
    }

    return (
      <span
        style={{
          display:
            "inline-flex",
          alignItems:
            "center",
          gap: "6px",
          color:
            "#b91c1c",
          fontWeight:
            600,
          fontSize:
            "12px",
        }}
      >
        <CircleX
          size={16}
        />

        Inativo
      </span>
    );
  }

  function renderResetPasswordResult() {
    if (
      !resetPasswordResult
    ) {
      return null;
    }

    return (
      <section
        className="content-card"
        style={{
          marginBottom:
            "16px",
          border:
            "1px solid #bbf7d0",
          background:
            "#f0fdf4",
        }}
      >
        <div className="card-header">
          <div>
            <h2>
              Senha temporária
            </h2>

            <p>
              A senha foi
              redefinida para{" "}
              <strong>
                {
                  resetPasswordResult.username
                }
              </strong>
              .
            </p>
          </div>

          <CircleCheck
            size={20}
          />
        </div>

        <div
          style={{
            display:
              "flex",
            alignItems:
              "center",
            gap: "10px",
            flexWrap:
              "wrap",
          }}
        >
          <code
            style={{
              flex:
                "1 1 240px",
              minWidth:
                "220px",
              padding:
                "10px 12px",
              border:
                "1px solid #bbf7d0",
              borderRadius:
                "8px",
              background:
                "#ffffff",
              color:
                "#14532d",
              fontSize:
                "14px",
              fontWeight:
                700,
              letterSpacing:
                "0.08em",
              textAlign:
                "center",
            }}
          >
            {
              resetPasswordResult.temporaryPassword
            }
          </code>

          <button
            type="button"
            className="secondary-button"
            onClick={() =>
              void handleCopyTemporaryPassword()
            }
          >
            <Clipboard
              size={15}
            />

            Copiar senha
          </button>
        </div>

        <small
          style={{
            display:
              "block",
            marginTop:
              "10px",
            color:
              "#166534",
            fontSize:
              "11px",
          }}
        >
          Guarde esta senha temporária.
          O usuário deverá
          alterá-la no próximo
          acesso.
        </small>
      </section>
    );
  }

  function renderUsersList() {
    if (isLoadingUsers) {
      return (
        <section className="content-card">
          <div
            className="empty-state"
            style={{
              minHeight:
                "260px",
            }}
          >
            <LoaderCircle
              size={28}
              className="spin"
            />

            <strong>
              Carregando usuários...
            </strong>

            <span>
              Aguarde enquanto
              carregamos as contas
              cadastradas.
            </span>
          </div>
        </section>
      );
    }

    if (users.length === 0) {
      return (
        <section className="content-card">
          <div className="empty-state">
            <Users
              size={32}
            />

            <strong>
              Nenhum usuário cadastrado
            </strong>

            <span>
              Cadastre o primeiro
              usuário para liberar o
              acesso ao OuroBuild.
            </span>

            <button
              className="primary-button"
              type="button"
              onClick={
                handleNewUser
              }
              style={{
                marginTop:
                  "8px",
              }}
            >
              <Plus
                size={18}
              />

              Novo usuário
            </button>
          </div>
        </section>
      );
    }

    return (
      <section className="content-card">
        <div className="card-header">
          <div>
            <h2>
              Usuários cadastrados
            </h2>

            <p>
              Contas de acesso ao
              OuroBuild.
            </p>
          </div>

          <button
            type="button"
            className="secondary-button"
            onClick={() =>
              void loadUsers(
                true,
              )
            }
            disabled={
              isRefreshingUsers ||
              updatingStatusUserId !==
                null ||
              resettingPasswordUserId !==
                null
            }
          >
            {isRefreshingUsers ? (
              <LoaderCircle
                size={15}
                className="spin"
              />
            ) : (
              <Users
                size={15}
              />
            )}

            Atualizar
          </button>
        </div>

        <div
          style={{
            overflowX:
              "auto",
          }}
        >
          <table
            style={{
              width:
                "100%",
              borderCollapse:
                "collapse",
              fontSize:
                "12px",
            }}
          >
            <thead>
              <tr>
                <th
                  style={
                    headerCellStyle
                  }
                >
                  Usuário
                </th>

                <th
                  style={
                    headerCellStyle
                  }
                >
                  Nome
                </th>

                <th
                  style={
                    headerCellStyle
                  }
                >
                  E-mail
                </th>

                <th
                  style={
                    headerCellStyle
                  }
                >
                  Status
                </th>

                <th
                  style={
                    headerCellStyle
                  }
                >
                  Primeiro acesso
                </th>

                <th
                  style={
                    headerCellStyle
                  }
                >
                  Último login
                </th>

                <th
                  style={{
                    ...headerCellStyle,
                    textAlign:
                      "right",
                  }}
                >
                  Ações
                </th>
              </tr>
            </thead>

            <tbody>
              {users.map(
                (user) => {
                  const hasActiveOperation =
                    updatingStatusUserId !==
                      null ||
                    resettingPasswordUserId !==
                      null;

                  const isUpdatingStatus =
                    updatingStatusUserId ===
                    user.id;

                  const isResettingPassword =
                    resettingPasswordUserId ===
                    user.id;

                  return (
                    <tr
                      key={
                        user.id
                      }
                    >
                      <td
                        style={
                          bodyCellStyleStrong
                        }
                      >
                        {
                          user.username
                        }
                      </td>

                      <td
                        style={
                          bodyCellStyle
                        }
                      >
                        {
                          user.display_name
                        }
                      </td>

                      <td
                        style={
                          bodyCellStyle
                        }
                      >
                        {
                          user.email ||
                          "—"
                        }
                      </td>

                      <td
                        style={
                          bodyCellStyle
                        }
                      >
                        {renderStatus(
                          user,
                        )}
                      </td>

                      <td
                        style={
                          bodyCellStyle
                        }
                      >
                        {user.must_change_password
                          ? "Sim"
                          : "Não"}
                      </td>

                      <td
                        style={
                          bodyCellStyle
                        }
                      >
                        {formatDate(
                          user.last_login_at,
                        )}
                      </td>

                      <td
                        style={{
                          ...bodyCellStyle,
                          textAlign:
                            "right",
                        }}
                      >
                        <div
                          style={{
                            display:
                              "inline-flex",
                            gap: "6px",
                            flexWrap:
                              "wrap",
                            justifyContent:
                              "flex-end",
                          }}
                        >
                          <button
                            type="button"
                            className="secondary-button"
                            onClick={() =>
                              handleEditUser(
                                user,
                              )
                            }
                            disabled={
                              hasActiveOperation
                            }
                          >
                            Editar
                          </button>

                          <button
                            type="button"
                            className="secondary-button"
                            onClick={() =>
                              void handleToggleStatus(
                                user,
                              )
                            }
                            disabled={
                              hasActiveOperation
                            }
                            title={
                              user.is_active
                                ? "Desativar usuário"
                                : "Ativar usuário"
                            }
                          >
                            {isUpdatingStatus ? (
                              <LoaderCircle
                                size={
                                  15
                                }
                                className="spin"
                              />
                            ) : user.is_active ? (
                              <CircleX
                                size={
                                  15
                                }
                              />
                            ) : (
                              <CircleCheck
                                size={
                                  15
                                }
                              />
                            )}

                            {user.is_active
                              ? "Desativar"
                              : "Ativar"}
                          </button>

                          <button
                            type="button"
                            className="secondary-button"
                            onClick={() =>
                              void handleResetPassword(
                                user,
                              )
                            }
                            disabled={
                              hasActiveOperation
                            }
                            title="Redefinir senha"
                          >
                            {isResettingPassword ? (
                              <LoaderCircle
                                size={
                                  15
                                }
                                className="spin"
                              />
                            ) : (
                              <Eye
                                size={
                                  15
                                }
                              />
                            )}

                            Resetar senha
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                },
              )}
            </tbody>
          </table>
        </div>
      </section>
    );
  }

  function renderUserForm() {
    const isEdit =
      mode === "edit";

    return (
      <div>
        <div className="page-heading">
          <div>
            <span className="page-eyebrow">
              ADMINISTRAÇÃO
            </span>

            <h1>
              {isEdit
                ? "Editar usuário"
                : "Novo usuário"}
            </h1>

            <p>
              {isEdit
                ? "Atualize os dados da conta de acesso ao OuroBuild."
                : "Cadastre uma nova conta para acesso ao OuroBuild."}
            </p>
          </div>

          <button
            className="secondary-button"
            type="button"
            onClick={
              handleCancel
            }
            disabled={
              isSubmitting
            }
          >
            <X
              size={16}
            />

            Voltar
          </button>
        </div>

        <div
          style={{
            display:
              "grid",
            gridTemplateColumns:
              "minmax(0, 1.5fr) minmax(280px, 0.8fr)",
            gap: "18px",
            alignItems:
              "start",
          }}
        >
          <section className="content-card">
            <div className="card-header">
              <div>
                <h2>
                  Dados do usuário
                </h2>

                <p>
                  {isEdit
                    ? "Altere somente os dados necessários."
                    : "Informe os dados da nova conta."}
                </p>
              </div>

              <UserPlus
                size={20}
              />
            </div>

            <form
              onSubmit={
                handleSubmit
              }
            >
              <div className="form-grid">
                <div className="form-field">
                  <label htmlFor="username">
                    Usuário
                  </label>

                  <input
                    id="username"
                    name="username"
                    type="text"
                    autoComplete="username"
                    value={
                      username
                    }
                    onChange={(
                      event,
                    ) => {
                      setUsername(
                        event.target.value,
                      );

                      clearMessages();
                    }}
                    disabled={
                      isSubmitting ||
                      isEdit
                    }
                    readOnly={
                      isEdit
                    }
                    required
                  />

                  {isEdit && (
                    <small
                      style={{
                        display:
                          "block",
                        marginTop:
                          "5px",
                        color:
                          "#64748b",
                        fontSize:
                          "11px",
                      }}
                    >
                      O usuário de
                      acesso não pode
                      ser alterado
                      nesta etapa.
                    </small>
                  )}
                </div>

                <div className="form-field">
                  <label htmlFor="display-name">
                    Nome
                  </label>

                  <input
                    id="display-name"
                    name="display-name"
                    type="text"
                    autoComplete="name"
                    value={
                      displayName
                    }
                    onChange={(
                      event,
                    ) => {
                      setDisplayName(
                        event
                          .target
                          .value,
                      );

                      clearMessages();
                    }}
                    disabled={
                      isSubmitting
                    }
                    required
                  />
                </div>

                <div className="form-field">
                  <label htmlFor="email">
                    E-mail
                  </label>

                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    value={email}
                    onChange={(
                      event,
                    ) => {
                      setEmail(
                        event
                          .target
                          .value,
                      );

                      clearMessages();
                    }}
                    disabled={
                      isSubmitting
                    }
                  />
                </div>

                <div className="form-field">
                  <label htmlFor="user-status">
                    Status
                  </label>

                  <select
                    id="user-status"
                    value={
                      isActive
                        ? "active"
                        : "inactive"
                    }
                    onChange={(
                      event,
                    ) => {
                      setIsActive(
                        event
                          .target
                          .value ===
                          "active",
                      );

                      clearMessages();
                    }}
                    disabled={
                      isSubmitting
                    }
                  >
                    <option value="active">
                      Ativo
                    </option>

                    <option value="inactive">
                      Inativo
                    </option>
                  </select>
                </div>

                {!isEdit && (
                  <>
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
                          autoComplete="new-password"
                          value={
                            password
                          }
                          onChange={(
                            event,
                          ) => {
                            setPassword(
                              event
                                .target
                                .value,
                            );

                            clearMessages();
                          }}
                          disabled={
                            isSubmitting
                          }
                          required
                          style={{
                            paddingRight:
                              "42px",
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
                              (
                                current,
                              ) =>
                                !current,
                            )
                          }
                          disabled={
                            isSubmitting
                          }
                          style={
                            eyeButtonStyle
                          }
                        >
                          {showPassword ? (
                            <EyeOff
                              size={
                                16
                              }
                            />
                          ) : (
                            <Eye
                              size={
                                16
                              }
                            />
                          )}
                        </button>
                      </div>
                    </div>

                    <div className="form-field">
                      <label htmlFor="confirm-password">
                        Confirmar senha
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
                              event
                                .target
                                .value,
                            );

                            clearMessages();
                          }}
                          disabled={
                            isSubmitting
                          }
                          required
                          style={{
                            paddingRight:
                              "42px",
                          }}
                        />

                        <button
                          type="button"
                          aria-label={
                            showConfirmPassword
                              ? "Ocultar senha"
                              : "Mostrar senha"
                          }
                          title={
                            showConfirmPassword
                              ? "Ocultar senha"
                              : "Mostrar senha"
                          }
                          onClick={() =>
                            setShowConfirmPassword(
                              (
                                current,
                              ) =>
                                !current,
                            )
                          }
                          disabled={
                            isSubmitting
                          }
                          style={
                            eyeButtonStyle
                          }
                        >
                          {showConfirmPassword ? (
                            <EyeOff
                              size={
                                16
                              }
                            />
                          ) : (
                            <Eye
                              size={
                                16
                              }
                            />
                          )}
                        </button>
                      </div>
                    </div>
                  </>
                )}

                <div
                  className="form-field"
                  style={{
                    gridColumn:
                      "1 / -1",
                  }}
                >
                  <label
                    htmlFor="must-change-password"
                    style={{
                      display:
                        "flex",
                      alignItems:
                        "center",
                      gap:
                        "8px",
                      cursor:
                        isSubmitting
                          ? "not-allowed"
                          : "pointer",
                    }}
                  >
                    <input
                      id="must-change-password"
                      name="must-change-password"
                      type="checkbox"
                      checked={
                        mustChangePassword
                      }
                      onChange={(
                        event,
                      ) => {
                        setMustChangePassword(
                          event
                            .target
                            .checked,
                        );

                        clearMessages();
                      }}
                      disabled={
                        isSubmitting
                      }
                      style={{
                        width:
                          "16px",
                        height:
                          "16px",
                        margin: 0,
                      }}
                    />

                    <span>
                      Exigir troca de
                      senha no primeiro
                      acesso
                    </span>
                  </label>

                  <small
                    style={{
                      display:
                        "block",
                      marginTop:
                        "5px",
                      marginLeft:
                        "24px",
                      color:
                        "#64748b",
                      fontSize:
                        "11px",
                    }}
                  >
                    {isEdit
                      ? "Ao ativar esta opção, o usuário será direcionado para alterar a senha no próximo acesso."
                      : "O usuário será direcionado para a tela de alteração de senha no primeiro login."}
                  </small>
                </div>
              </div>

              {errorMessage && (
                <div
                  className="error-message"
                  role="alert"
                  aria-live="polite"
                  style={{
                    marginTop:
                      "15px",
                  }}
                >
                  {
                    errorMessage
                  }
                </div>
              )}

              <div
                style={{
                  display:
                    "flex",
                  justifyContent:
                    "flex-end",
                  gap:
                    "10px",
                  marginTop:
                    "20px",
                }}
              >
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => {
                    if (
                      isEdit
                    ) {
                      handleCancel();
                      return;
                    }

                    resetForm();
                    clearMessages();
                  }}
                  disabled={
                    isSubmitting
                  }
                >
                  {isEdit
                    ? "Cancelar"
                    : "Limpar"}
                </button>

                <button
                  type="submit"
                  className="primary-button"
                  disabled={
                    isSubmitting
                  }
                >
                  {isSubmitting ? (
                    <>
                      <LoaderCircle
                        size={
                          15
                        }
                        className="spin"
                      />

                      Salvando...
                    </>
                  ) : (
                    <>
                      <Save
                        size={
                          15
                        }
                      />

                      {isEdit
                        ? "Salvar alterações"
                        : "Criar usuário"}
                    </>
                  )}
                </button>
              </div>
            </form>
          </section>

          <section className="content-card">
            <div className="card-header">
              <div>
                <h2>
                  Informações
                </h2>

                <p>
                  {isEdit
                    ? "Dados disponíveis nesta edição."
                    : "Dados utilizados para criar a conta."}
                </p>
              </div>
            </div>

            <div className="system-list">
              <div className="system-item">
                <UserPlus
                  size={17}
                />

                <div>
                  <strong>
                    Usuário de acesso
                  </strong>

                  <span>
                    {isEdit
                      ? "O identificador permanece bloqueado."
                      : "Será utilizado no login do OuroBuild."}
                  </span>
                </div>
              </div>

              <div className="system-item">
                <CircleCheck
                  size={17}
                />

                <div>
                  <strong>
                    Senha
                  </strong>

                  <span>
                    {isEdit
                      ? "A alteração de senha será tratada na etapa de reset."
                      : "A senha é armazenada como hash."}
                  </span>
                </div>
              </div>

              <div className="system-item">
                <CircleCheck
                  size={17}
                />

                <div>
                  <strong>
                    Primeiro acesso
                  </strong>

                  <span>
                    A exigência de troca
                    de senha pode ser
                    definida nesta tela.
                  </span>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    );
  }

  return (
    <section>
      {mode === "list" ? (
        <>
          <div className="page-heading">
            <div>
              <span className="page-eyebrow">
                ADMINISTRAÇÃO
              </span>

              <h1>
                Usuários
              </h1>

              <p>
                Gerencie os usuários e
                permissões do OuroBuild.
              </p>
            </div>

            <button
              className="primary-button"
              type="button"
              onClick={
                handleNewUser
              }
            >
              <Plus
                size={18}
              />

              Novo usuário
            </button>
          </div>

          {successMessage && (
            <div
              style={
                successMessageStyle
              }
              role="status"
              aria-live="polite"
            >
              <CircleCheck
                size={16}
              />

              {
                successMessage
              }
            </div>
          )}

          {errorMessage && (
            <div
              className="error-message"
              role="alert"
              aria-live="polite"
              style={{
                marginBottom:
                  "16px",
              }}
            >
              {
                errorMessage
              }
            </div>
          )}

          {renderResetPasswordResult()}

          {renderUsersList()}
        </>
      ) : (
        renderUserForm()
      )}
    </section>
  );
}

const headerCellStyle = {
  textAlign:
    "left" as const,
  padding:
    "12px 10px",
  borderBottom:
    "1px solid #e2e8f0",
  color:
    "#64748b",
  fontWeight:
    600,
};

const bodyCellStyle = {
  padding:
    "14px 10px",
  borderBottom:
    "1px solid #f1f5f9",
  color:
    "#475569",
};

const bodyCellStyleStrong = {
  ...bodyCellStyle,
  fontWeight:
    600,
  color:
    "#0f172a",
};

const eyeButtonStyle = {
  position:
    "absolute" as const,
  top: "50%",
  right: "8px",
  transform:
    "translateY(-50%)",
  width: "30px",
  height: "30px",
  display:
    "flex",
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
  color:
    "#64748b",
};

const successMessageStyle = {
  display:
    "flex",
  alignItems:
    "center",
  gap:
    "8px",
  marginBottom:
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
};

export default UsersPage;