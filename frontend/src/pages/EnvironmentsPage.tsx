import {
  useEffect,
  useState,
  type FormEvent,
} from "react";

import {
  Check,
  ChevronLeft,
  Edit,
  FolderOpen,
  Loader2,
  Plus,
  RefreshCw,
  Server,
} from "lucide-react";

import {
  createEnvironment,
  getEnvironments,
  updateEnvironment,
  type BuildEnvironmentType,
  type CreateEnvironmentRequest,
  type Environment,
  type UpdateEnvironmentRequest,
} from "../services/environmentsApi";


type PageMode =
  | "list"
  | "create"
  | "edit";


interface EnvironmentFormData {
  id: string;
  name: string;
  resolver: BuildEnvironmentType;
  root_path: string;
}


const emptyForm: EnvironmentFormData = {
  id: "",
  name: "",
  resolver: "versioned",
  root_path: "",
};


function resolverLabel(
  resolver: string,
): string {
  switch (resolver) {
    case "production":
      return "Produção";

    case "versioned":
      return "Versionado";

    default:
      return resolver;
  }
}


function EnvironmentIcon({
  resolver,
}: {
  resolver: string;
}) {
  if (resolver === "production") {
    return <Server size={19} />;
  }

  return <FolderOpen size={19} />;
}


function EnvironmentsPage() {
  const [environments, setEnvironments] =
    useState<Environment[]>([]);

  const [mode, setMode] =
    useState<PageMode>("list");

  const [form, setForm] =
    useState<EnvironmentFormData>({
      ...emptyForm,
    });

  const [isLoading, setIsLoading] =
    useState(false);

  const [isRefreshing, setIsRefreshing] =
    useState(false);

  const [isSaving, setIsSaving] =
    useState(false);

  const [errorMessage, setErrorMessage] =
    useState("");

  const [successMessage, setSuccessMessage] =
    useState("");

  useEffect(() => {
    void loadEnvironments();
  }, []);

  async function loadEnvironments(
    refreshing = false,
  ) {
    try {
      setErrorMessage("");

      if (refreshing) {
        setIsRefreshing(true);
      } else {
        setIsLoading(true);
      }

      const result =
        await getEnvironments();

      setEnvironments(result);
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "";

      setErrorMessage(
        message ||
          "Não foi possível carregar os ambientes.",
      );
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }

  function clearMessages() {
    setErrorMessage("");
    setSuccessMessage("");
  }

  function openCreate() {
    clearMessages();

    setForm({
      ...emptyForm,
    });

    setMode("create");
  }

  function openEdit(
    environment: Environment,
  ) {
    clearMessages();

    setForm({
      id: environment.id,
      name: environment.name,
      resolver:
        environment.resolver as BuildEnvironmentType,
      root_path: environment.root_path,
    });

    setMode("edit");
  }

  function backToList() {
    clearMessages();
    setMode("list");
  }

  function updateField<
    K extends keyof EnvironmentFormData
  >(
    field: K,
    value: EnvironmentFormData[K],
  ) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function buildCreateRequest():
    CreateEnvironmentRequest {
    return {
      id: form.id.trim(),
      name: form.name.trim(),
      resolver: form.resolver,
      root_path: form.root_path.trim(),
    };
  }

  function buildUpdateRequest():
    UpdateEnvironmentRequest {
    return {
      name: form.name.trim(),
      resolver: form.resolver,
      root_path: form.root_path.trim(),
    };
  }

  function validateForm(): string | null {
    if (
      mode === "create" &&
      !form.id.trim()
    ) {
      return "Informe o identificador do ambiente.";
    }

    if (!form.name.trim()) {
      return "Informe o nome do ambiente.";
    }

    if (!form.root_path.trim()) {
      return "Informe o caminho raiz do ambiente.";
    }

    return null;
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    clearMessages();

    const validationError =
      validateForm();

    if (validationError) {
      setErrorMessage(
        validationError,
      );

      return;
    }

    try {
      setIsSaving(true);

      if (mode === "create") {
        await createEnvironment(
          buildCreateRequest(),
        );

        setSuccessMessage(
          "Ambiente cadastrado com sucesso.",
        );
      } else {
        await updateEnvironment(
          form.id,
          buildUpdateRequest(),
        );

        setSuccessMessage(
          "Ambiente alterado com sucesso.",
        );
      }

      await loadEnvironments(true);

      setMode("list");
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "";

      setErrorMessage(
        message ||
          "Não foi possível salvar o ambiente.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  function renderMessage() {
    if (errorMessage) {
      return (
        <div className="error-message">
          {errorMessage}
        </div>
      );
    }

    if (successMessage) {
      return (
        <div className="success-message">
          {successMessage}
        </div>
      );
    }

    return null;
  }

  function renderEnvironmentsList() {
    if (isLoading) {
      return (
        <div className="empty-state">
          <Loader2
            size={24}
            className="spin"
          />

          <strong>
            Carregando ambientes...
          </strong>
        </div>
      );
    }

    if (environments.length === 0) {
      return (
        <div className="empty-state">
          <FolderOpen size={24} />

          <strong>
            Nenhum ambiente cadastrado.
          </strong>

          <span>
            Cadastre o primeiro ambiente
            para disponibilizá-lo no OuroBuild.
          </span>
        </div>
      );
    }

    return (
      <div className="content-card">
        <div className="card-header">
          <div>
            <h2>
              Ambientes cadastrados
            </h2>

            <p>
              Gerencie os ambientes utilizados
              pelo processo de build e setup.
            </p>
          </div>

          <button
            className="secondary-button"
            type="button"
            onClick={() =>
              void loadEnvironments(true)
            }
            disabled={isRefreshing}
          >
            <RefreshCw
              size={14}
              className={
                isRefreshing
                  ? "spin"
                  : undefined
              }
            />

            Atualizar
          </button>
        </div>

        <div className="project-admin-list">
          {environments.map(
            (environment) => (
              <div
                className="project-admin-row"
                key={environment.id}
              >
                <div className="project-admin-icon">
                  <EnvironmentIcon
                    resolver={
                      environment.resolver
                    }
                  />
                </div>

                <div className="project-admin-info">
                  <strong>
                    {environment.name}
                  </strong>

                  <span>
                    {environment.id}
                  </span>
                </div>

                <span className="project-admin-type">
                  {resolverLabel(
                    environment.resolver,
                  )}
                </span>

                <div className="project-admin-info">
                  <span>
                    {environment.root_path}
                  </span>
                </div>

                <div className="project-admin-actions">
                  <button
                    className="table-action-button"
                    type="button"
                    onClick={() =>
                      openEdit(
                        environment,
                      )
                    }
                  >
                    <Edit size={14} />

                    Editar
                  </button>
                </div>
              </div>
            ),
          )}
        </div>
      </div>
    );
  }

  function renderEnvironmentForm() {
    const isEdit =
      mode === "edit";

    return (
      <form
        className="content-card"
        onSubmit={handleSubmit}
      >
        <div className="card-header">
          <div>
            <h2>
              {isEdit
                ? "Editar ambiente"
                : "Novo ambiente"}
            </h2>

            <p>
              {isEdit
                ? "Altere as configurações do ambiente."
                : "Cadastre um novo ambiente no OuroBuild."}
            </p>
          </div>
        </div>

        <div className="form-grid">
          <div className="form-field">
            <label htmlFor="environment-id">
              Identificador
            </label>

            <input
              id="environment-id"
              value={form.id}
              disabled={isEdit}
              onChange={(event) =>
                updateField(
                  "id",
                  event.target.value,
                )
              }
              placeholder="ex.: production"
            />
          </div>

          <div className="form-field">
            <label htmlFor="environment-name">
              Nome
            </label>

            <input
              id="environment-name"
              value={form.name}
              onChange={(event) =>
                updateField(
                  "name",
                  event.target.value,
                )
              }
              placeholder="Nome do ambiente"
            />
          </div>

          <div className="form-field">
            <label htmlFor="environment-resolver">
              Tipo
            </label>

            <select
              id="environment-resolver"
              value={form.resolver}
              onChange={(event) =>
                updateField(
                  "resolver",
                  event.target.value as BuildEnvironmentType,
                )
              }
            >
              <option value="versioned">
                Versionado
              </option>

              <option value="production">
                Produção
              </option>
            </select>
          </div>

          <div className="form-field form-field-full">
            <label htmlFor="environment-root-path">
              Caminho raiz
            </label>

            <input
              id="environment-root-path"
              value={form.root_path}
              onChange={(event) =>
                updateField(
                  "root_path",
                  event.target.value,
                )
              }
              placeholder={
                "C:\\DvpLocal\\WorkSpaceTFS\\OuroNet\\..."
              }
            />
          </div>
        </div>

        <div className="form-actions">
          <button
            className="secondary-button"
            type="button"
            onClick={backToList}
            disabled={isSaving}
          >
            <ChevronLeft size={14} />

            Voltar
          </button>

          <button
            className="primary-button"
            type="submit"
            disabled={isSaving}
          >
            {isSaving ? (
              <Loader2
                size={14}
                className="spin"
              />
            ) : (
              <Check size={14} />
            )}

            {isEdit
              ? "Salvar alterações"
              : "Cadastrar ambiente"}
          </button>
        </div>
      </form>
    );
  }

  return (
    <section>
      <div className="page-heading">
        <div>
          <span className="page-eyebrow">
            ADMINISTRAÇÃO
          </span>

          <h1>
            Ambientes
          </h1>

          <p>
            Gerencie os ambientes utilizados
            para build e setup.
          </p>
        </div>

        {mode === "list" && (
          <button
            className="primary-button"
            type="button"
            onClick={openCreate}
          >
            <Plus size={15} />

            Novo ambiente
          </button>
        )}
      </div>

      {renderMessage()}

      {mode === "list"
        ? renderEnvironmentsList()
        : renderEnvironmentForm()}
    </section>
  );
}

export default EnvironmentsPage;