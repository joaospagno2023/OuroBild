import { apiPost, apiPostForm, apiPut } from "./api";

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  must_change_password: boolean;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface AuthUser {
  id: number;
  username: string;
  display_name?: string | null;
  email?: string | null;
  is_active: boolean;
  must_change_password: boolean;
  created_at: string;
  last_login_at?: string | null;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export async function login(
  request: LoginRequest,
): Promise<TokenResponse> {
  return apiPostForm<TokenResponse>("/auth/token", {
    username: request.username,
    password: request.password,
  });
}

export async function changePassword(
  request: ChangePasswordRequest,
): Promise<AuthUser> {
  return apiPost<ChangePasswordRequest, AuthUser>(
    "/auth/change-password",
    request,
  );
}

export function saveToken(token: string): void {
  localStorage.setItem("ourobuild_access_token", token);
}

export function getToken(): string | null {
  return localStorage.getItem("ourobuild_access_token");
}

export function removeToken(): void {
  localStorage.removeItem("ourobuild_access_token");
}

export function isAuthenticated(): boolean {
  return getToken() !== null;
}

export interface UpdateProfileRequest {
  display_name: string;
  email?: string | null;
}

export async function updateProfile(
  request: UpdateProfileRequest,
): Promise<AuthUser> {
  return apiPut<UpdateProfileRequest, AuthUser>(
    "/auth/profile",
    request,
  );
}
