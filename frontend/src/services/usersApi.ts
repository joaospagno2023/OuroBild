import {
  apiGet,
  apiPatch,
  apiPost,
  apiPut,
} from "./api";

export interface User {
  id: number;
  username: string;
  display_name: string;
  email?: string | null;
  is_active: boolean;
  must_change_password: boolean;
  created_at: string;
  last_login_at?: string | null;
}

export interface CreateUserRequest {
  username: string;
  display_name: string;
  email?: string | null;
  password: string;
  is_active: boolean;
  must_change_password: boolean;
}

export interface UpdateUserRequest {
  display_name: string;
  email?: string | null;
  is_active: boolean;
  must_change_password: boolean;
}

export interface UpdateUserStatusRequest {
  is_active: boolean;
}

export interface ResetPasswordResponse {
  user: User;
  temporary_password: string;
}

export async function getUsers(): Promise<User[]> {
  return apiGet<User[]>("/users");
}

export async function createUser(
  request: CreateUserRequest,
): Promise<User> {
  return apiPost<CreateUserRequest, User>(
    "/users",
    request,
  );
}

export async function updateUser(
  userId: number,
  request: UpdateUserRequest,
): Promise<User> {
  return apiPut<UpdateUserRequest, User>(
    `/users/${userId}`,
    request,
  );
}

export async function updateUserStatus(
  userId: number,
  request: UpdateUserStatusRequest,
): Promise<User> {
  return apiPatch<
    UpdateUserStatusRequest,
    User
  >(
    `/users/${userId}/status`,
    request,
  );
}

export async function resetUserPassword(
  userId: number,
): Promise<ResetPasswordResponse> {
  return apiPost<
    Record<string, never>,
    ResetPasswordResponse
  >(
    `/users/${userId}/reset-password`,
    {},
  );
}