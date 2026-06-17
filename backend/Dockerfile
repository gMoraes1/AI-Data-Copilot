# --- build stage: instala dependências com Poetry ---
FROM python:3.11-slim AS builder

ENV POETRY_VERSION=1.8.5 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PIP_NO_CACHE_DIR=1

RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /app
COPY pyproject.toml poetry.lock* ./
# Sem instalar o pacote da própria app (apenas dependências) -> melhor cache.
RUN poetry install --only main --no-root

# --- runtime stage ---
FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Usuário não-root (boa prática de segurança em containers).
RUN useradd --create-home --uid 1000 appuser

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . .

USER appuser
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
