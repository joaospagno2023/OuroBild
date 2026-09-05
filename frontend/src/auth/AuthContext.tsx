import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import {
  getToken,
  removeToken,
  saveToken,
} from "../services/authApi";
import { apiGet } from "../services/api";

export interface AuthUser {
  id: number;
  username: string;
  display_name?: string | null;
  email?: string | null;
  is_active: boolean;
}

interface AuthContextValue {
  token: string | null;
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setAuthenticated: (token: string) => void;
  logout: () => void;
}

const AuthContext =
  createContext<AuthContextValue | undefined>(
    undefined,
  );

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({
  children,
}: AuthProviderProps) {
  const [token, setToken] =
    useState<string | null>(
      () => getToken(),
    );

  const [user, setUser] =
    useState<AuthUser | null>(null);

  const [isLoading, setIsLoading] =
    useState<boolean>(true);

  function setAuthenticated(
    accessToken: string,
  ): void {
    saveToken(accessToken);
    setToken(accessToken);
  }

  function logout(): void {
    removeToken();
    setToken(null);
    setUser(null);
  }

  useEffect(() => {
    function handleAuthenticationFailure(): void {
      logout();
    }

    window.addEventListener(
      "ourobuild:auth-failure",
      handleAuthenticationFailure,
    );

    return () => {
      window.removeEventListener(
        "ourobuild:auth-failure",
        handleAuthenticationFailure,
      );
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function validateSession(): Promise<void> {
      if (!token) {
        if (!cancelled) {
          setUser(null);
          setIsLoading(false);
        }

        return;
      }

      try {
        const authenticatedUser =
          await apiGet<AuthUser>(
            "/auth/me",
          );

        if (cancelled) {
          return;
        }

        setUser(authenticatedUser);
      } catch {
        if (cancelled) {
          return;
        }

        removeToken();
        setToken(null);
        setUser(null);
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    setIsLoading(true);

    void validateSession();

    return () => {
      cancelled = true;
    };
  }, [token]);

  const value =
    useMemo<AuthContextValue>(
      () => ({
        token,
        user,
        isAuthenticated:
          token !== null &&
          user !== null,
        isLoading,
        setAuthenticated,
        logout,
      }),
      [
        token,
        user,
        isLoading,
      ],
    );

  return (
    <AuthContext.Provider
      value={value}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context =
    useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth deve ser utilizado dentro de AuthProvider.",
    );
  }

  return context;
}