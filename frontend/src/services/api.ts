const API_BASE_URL =
  "http://127.0.0.1:8000";

function getAuthorizationHeader(): Record<string, string> {
  const token = localStorage.getItem(
    "ourobuild_access_token",
  );

  if (!token) {
    return {};
  }

  return {
    Authorization: `Bearer ${token}`,
  };
}

function handleUnauthorized(): void {
  localStorage.removeItem(
    "ourobuild_access_token",
  );

  window.dispatchEvent(
    new Event("ourobuild:auth-failure"),
  );
}

export async function apiGet<T>(
  endpoint: string,
): Promise<T> {
  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      method: "GET",
      headers: {
        Accept: "application/json",
        ...getAuthorizationHeader(),
      },
    },
  );

  if (response.status === 401) {
    handleUnauthorized();

    throw new Error(
      "Sessão expirada ou não autenticada.",
    );
  }

  if (!response.ok) {
    throw new Error(
      `Erro HTTP ${response.status}: ${response.statusText}`,
    );
  }

  return response.json() as Promise<T>;
}

export async function apiPost<
  TRequest,
  TResponse,
>(
  endpoint: string,
  body: TRequest,
): Promise<TResponse> {
  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        ...getAuthorizationHeader(),
      },
      body: JSON.stringify(body),
    },
  );

  if (response.status === 401) {
    handleUnauthorized();

    throw new Error(
      "Sessão expirada ou não autenticada.",
    );
  }

  if (!response.ok) {
    const message =
      await response.text();

    throw new Error(
      message ||
        `Erro HTTP ${response.status}: ${response.statusText}`,
    );
  }

  return response.json() as Promise<TResponse>;
}

export async function apiPostForm<
  TResponse,
>(
  endpoint: string,
  data: Record<string, string>,
): Promise<TResponse> {
  const formData =
    new URLSearchParams();

  for (
    const [key, value] of Object.entries(data)
  ) {
    formData.append(
      key,
      value,
    );
  }

  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type":
          "application/x-www-form-urlencoded",
      },
      body: formData.toString(),
    },
  );

  if (!response.ok) {
    const message =
      await response.text();

    throw new Error(
      message ||
        `Erro HTTP ${response.status}: ${response.statusText}`,
    );
  }

  return response.json() as Promise<TResponse>;
}