"""ChatService — orquestra o fluxo completo do Copilot.

Pergunta -> schema -> SQL (LLM) -> validação -> execução -> resposta (LLM) -> histórico.

É o "caso de uso" (application service): coordena as peças, mas não contém
lógica de baixo nível (que vive em generator/executor/analyzer).
"""

import time

from sqlalchemy.engine import Engine

from app.core.config import Settings
from app.core.exceptions import CopilotError
from app.core.logging import get_logger
from app.db.schema_inspector import get_schema_map
from app.models.chat_history import ChatMessage
from app.repositories.chat_repository import ChatRepository
from app.schemas.chat import ChatResponse
from app.services.analyzer import ResultAnalyzer
from app.services.llm.base import LLMProvider
from app.services.sql.executor import SQLExecutor
from app.services.sql.generator import SQLGenerator

logger = get_logger(__name__)


class ChatService:
    def __init__(
        self,
        *,
        engine: Engine,
        readonly_engine: Engine,
        llm: LLMProvider,
        repository: ChatRepository,
        settings: Settings,
    ) -> None:
        self._engine = engine
        self._repository = repository
        self._generator = SQLGenerator(llm, settings.sql_max_rows)
        # O executor usa o engine SOMENTE-LEITURA (papel sujeito ao RLS).
        self._executor = SQLExecutor(
            readonly_engine, settings.sql_statement_timeout_ms, settings.sql_max_rows
        )
        self._analyzer = ResultAnalyzer(llm)

    def ask(
        self, question: str, *, user_id: int | None = None, tenant_id: int
    ) -> ChatResponse:
        start = time.perf_counter()
        sql: str | None = None
        try:
            schema = get_schema_map(self._engine)
            sql = self._generator.generate(question, schema)
            rows = self._executor.execute(sql, tenant_id=tenant_id)
            answer = self._analyzer.analyze(question, sql, rows)

            latency_ms = int((time.perf_counter() - start) * 1000)
            self._save(question, sql, answer, "success", None, len(rows), latency_ms, user_id)

            logger.info(
                "Pergunta respondida",
                extra={"row_count": len(rows), "latency_ms": latency_ms},
            )
            return ChatResponse(
                answer=answer,
                sql=sql,
                rows=rows,
                row_count=len(rows),
                latency_ms=latency_ms,
            )
        except CopilotError as exc:
            latency_ms = int((time.perf_counter() - start) * 1000)
            status = "rejected" if exc.status_code == 422 else "error"
            self._save(question, sql, None, status, exc.message, 0, latency_ms, user_id)
            raise

    def _save(
        self,
        question: str,
        sql: str | None,
        answer: str | None,
        status: str,
        error: str | None,
        row_count: int,
        latency_ms: int,
        user_id: int | None,
    ) -> None:
        try:
            self._repository.add(
                ChatMessage(
                    user_id=user_id,
                    question=question,
                    generated_sql=sql,
                    answer=answer,
                    status=status,
                    error=error,
                    row_count=row_count,
                    latency_ms=latency_ms,
                )
            )
        except Exception:  # noqa: BLE001 — histórico não deve derrubar a request.
            logger.exception("Falha ao gravar histórico de chat")
