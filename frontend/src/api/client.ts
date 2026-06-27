// Cliente HTTP tipado para a API do backend.
// A base "/api" é redirecionada pelo proxy do Vite (dev) ou pelo servidor web (prod).

import type { ChatResponse, User } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";
const TOKEN_KEY = "copilot.token";

// --- Gestão do token (persistido no localStorage) ---
export const tokenStore = {
  get: (): string | null => localStorage.getItem(TOKEN_KEY),
  set: (token: string) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = tokenStore.get();
  const headers = new Headers(init.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_BASE}${path}`, { ...init, headers });

  if (response.status === 401) {
    // Token inválido/expirado: limpa para forçar novo login.
    tokenStore.clear();
  }
  if (!response.ok) {
    throw new ApiError(response.status, await extractDetail(response));
  }
  return (await response.json()) as T;
}

async function extractDetail(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as { detail?: string };
    return data.detail ?? `Erro ${response.status}`;
  } catch {
    return `Erro ${response.status}`;
  }
}

// --- Autenticação ---

export async function login(email: string, password: string): Promise<string> {
  // O endpoint /auth/login usa OAuth2 password flow (form-urlencoded).
  const body = new URLSearchParams({ username: email, password });
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!response.ok) {
    throw new ApiError(response.status, await extractDetail(response));
  }
  const data = (await response.json()) as { access_token: string };
  tokenStore.set(data.access_token);
  return data.access_token;
}

export async function register(
  email: string,
  password: string,
  fullName?: string,
): Promise<User> {
  return request<User>("/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, full_name: fullName || null }),
  });
}

export async function getMe(): Promise<User> {
  return request<User>("/auth/me");
}

export function logout(): void {
  tokenStore.clear();
}

// --- Chat ---

export async function askCopilot(question: string): Promise<ChatResponse> {
  return request<ChatResponse>("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
}
