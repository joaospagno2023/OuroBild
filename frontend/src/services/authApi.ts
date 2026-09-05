import { apiPostForm } from "./api";

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export async function login(
  request: LoginRequest,
): Promise<TokenResponse> {
  return apiPostForm<TokenResponse>(
    "/auth/token",
    {
      username: request.username,
      password: request.password,
    },
  );
}

export function saveToken(
  token: string,
): void {
  localStorage.setItem(
    "ourobuild_access_token",
    token,
  );
}

export function getToken(): string | null {
  return localStorage.getItem(
    "ourobuild_access_token",
  );
}

export function removeToken(): void {
  localStorage.removeItem(
    "ourobuild_access_token",
  );
}

export function isAuthenticated(): boolean {
  return getToken() !== null;
}