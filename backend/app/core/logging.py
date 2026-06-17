"""Configuração de logging estruturado (JSON) para observabilidade.

Logs em JSON facilitam a ingestão por ferramentas como Loki/ELK e a correlação
de eventos. Use `get_logger(__name__)` nos módulos.
"""

import logging
import sys

try:
    # python-json-logger >= 3.1
    from pythonjsonlogger.json import JsonFormatter
except ImportError:  # pragma: no cover - compat com versões antigas
    from pythonjsonlogger.jsonlogger import JsonFormatter

_configured = False


def configure_logging(level: str = "INFO") -> None:
    global _configured
    if _configured:
        return

    handler = logging.StreamHandler(sys.stdout)
    formatter = JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={"asctime": "timestamp", "levelname": "level", "name": "logger"},
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())

    # Reduz o ruído de bibliotecas verbosas.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
