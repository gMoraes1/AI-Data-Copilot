// Hook que encapsula o estado da conversa e a comunicação com a API.
// Mantém os componentes de UI "burros" (apenas apresentação).

import { useCallback, useState } from "react";
import { ApiError, askCopilot } from "../api/client";
import type { ChatTurn } from "../types";

let counter = 0;
const nextId = () => `${Date.now()}-${counter++}`;

export function useChat() {
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [loading, setLoading] = useState(false);

  const send = useCallback(async (question: string) => {
    const trimmed = question.trim();
    if (!trimmed || loading) return;

    const userTurn: ChatTurn = { id: nextId(), role: "user", question: trimmed };
    const pendingId = nextId();
    const pendingTurn: ChatTurn = { id: pendingId, role: "assistant", pending: true };
    setTurns((prev) => [...prev, userTurn, pendingTurn]);
    setLoading(true);

    try {
      const res = await askCopilot(trimmed);
      setTurns((prev) =>
        prev.map((t) =>
          t.id === pendingId
            ? {
                ...t,
                pending: false,
                answer: res.answer,
                sql: res.sql,
                rows: res.rows,
                latencyMs: res.latency_ms,
              }
            : t,
        ),
      );
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Falha de conexão com o servidor.";
      setTurns((prev) =>
        prev.map((t) => (t.id === pendingId ? { ...t, pending: false, error: message } : t)),
      );
    } finally {
      setLoading(false);
    }
  }, [loading]);

  return { turns, loading, send };
}
