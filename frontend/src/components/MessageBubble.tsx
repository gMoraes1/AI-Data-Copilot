// Apresenta um turno da conversa (usuário ou assistente).

import type { ChatTurn } from "../types";
import { ResultTable } from "./ResultTable";
import { SqlDetails } from "./SqlDetails";

interface Props {
  turn: ChatTurn;
}

export function MessageBubble({ turn }: Props) {
  if (turn.role === "user") {
    return (
      <div className="bubble bubble--user">
        <p>{turn.question}</p>
      </div>
    );
  }

  return (
    <div className="bubble bubble--assistant">
      {turn.pending && <p className="typing">Consultando os dados…</p>}

      {turn.error && <p className="error">⚠️ {turn.error}</p>}

      {turn.answer && <p>{turn.answer}</p>}

      {turn.sql && <SqlDetails sql={turn.sql} latencyMs={turn.latencyMs} />}

      {turn.rows && turn.rows.length > 0 && <ResultTable rows={turn.rows} />}
    </div>
  );
}
