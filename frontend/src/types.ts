// Tipos do domínio compartilhados, espelhando os DTOs do backend.

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  tenant_id: number;
  tenant_name: string | null;
  created_at: string;
}

export interface ChatResponse {
  answer: string;
  sql: string;
  rows: Record<string, unknown>[];
  row_count: number;
  latency_ms: number;
}

export type Role = "user" | "assistant";

export interface ChatTurn {
  id: string;
  role: Role;
  question?: string;
  // Preenchido apenas em mensagens do assistente:
  answer?: string;
  sql?: string;
  rows?: Record<string, unknown>[];
  latencyMs?: number;
  error?: string;
  pending?: boolean;
}
