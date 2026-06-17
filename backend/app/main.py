"""Ponto de entrada da aplicação FastAPI (app factory)."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import CopilotError
from app.core.logging import configure_logging, get_logger
from app.db.bootstrap import init_database

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Em desenvolvimento, cria as tabelas e popula dados de exemplo.
    # Em produção, prefira migrações Alembic (ver alembic/).
    if not settings.is_production:
        init_database()
    logger.info("Aplicação iniciada", extra={"environment": settings.environment})
    yield
    logger.info("Aplicação finalizada")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Consulte dados corporativos em linguagem natural.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Handler único para os erros de domínio -> resposta JSON consistente.
    @app.exception_handler(CopilotError)
    async def copilot_error_handler(_: Request, exc: CopilotError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    app.include_router(api_router)

    # Observabilidade: expõe métricas em /metrics (Prometheus).
    Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

    return app


app = create_app()
