"""Configurações da aplicação, carregadas de variáveis de ambiente / arquivo .env.

Centraliza toda a configuração em um único objeto `Settings` (padrão 12-factor).
Nenhum outro módulo deve ler `os.environ` diretamente.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Aplicação ---
    app_name: str = "Corporate AI Copilot"
    environment: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"

    # CORS — origens permitidas para o frontend.
    cors_origins: list[str] = Field(default=["http://localhost:5173", "http://localhost:3000"])

    # --- Autenticação (JWT) ---
    # IMPORTANTE: defina SECRET_KEY via variável de ambiente em produção.
    secret_key: str = Field(
        default="dev-insecure-secret-change-me-0123456789abcdef",
        description="Chave para assinar os tokens JWT. NUNCA use o default em produção.",
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8  # 8 horas

    # --- Banco de dados ---
    database_url: str = Field(
        default="postgresql+psycopg2://copilot:copilot@localhost:5432/copilot",
        description="DSN do PostgreSQL onde ficam o histórico e os dados de negócio.",
    )

    # --- Execução de SQL (camada de segurança) ---
    sql_max_rows: int = Field(default=200, description="Limite de linhas retornadas por consulta.")
    sql_statement_timeout_ms: int = Field(
        default=5000, description="Timeout de execução da consulta no Postgres (ms)."
    )

    # --- Multi-tenant / papel somente-leitura para execução das queries do LLM ---
    # O executor conecta com ESTE papel (não-owner) para que o RLS seja aplicado.
    # Tem permissão apenas de SELECT nas tabelas de negócio (não lê 'users').
    readonly_db_user: str = "copilot_ro"
    readonly_db_password: str = "copilot_ro"
    database_readonly_url: str = Field(
        default="postgresql+psycopg2://copilot_ro:copilot_ro@localhost:5432/copilot",
        description="DSN do papel somente-leitura usado para executar o SQL gerado.",
    )
    # Em dev, o bootstrap cria o papel read-only e configura o RLS automaticamente.
    setup_rls_on_startup: bool = True

    # --- LLM ---
    llm_provider: Literal["ollama", "fake"] = "ollama"
    llm_model: str = "llama3"
    llm_temperature: float = 0.0
    ollama_base_url: str = "http://localhost:11434"
    llm_timeout_seconds: float = 60.0

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Retorna uma instância singleton de Settings (cacheada)."""
    return Settings()
