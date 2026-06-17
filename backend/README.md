# Corporate AI Copilot — Backend

API FastAPI que traduz perguntas em linguagem natural em SQL seguro, executa no
PostgreSQL e responde em linguagem natural.

## Arquitetura (camadas)

```
app/
├── api/              # Camada de apresentação (rotas FastAPI, DI)
│   ├── routes/       #   chat.py, auth.py, health.py
│   └── deps.py       #   injeção de dependência (inclui get_current_user)
├── schemas/          # DTOs Pydantic (contrato da API)
├── services/         # Casos de uso / regra de negócio
│   ├── chat_service.py   # orquestrador do fluxo
│   ├── auth_service.py   # registro/login
│   ├── analyzer.py       # resultado -> linguagem natural
│   ├── llm/              # abstração de LLM (base, ollama, fake, factory)
│   └── sql/              # generator, validator, executor
├── repositories/     # Acesso a dados (padrão Repository)
├── models/           # ORM SQLAlchemy (business + chat_history + user)
├── db/               # session, schema_inspector, seed, bootstrap
└── core/             # config, logging, exceptions, security (JWT/bcrypt)
```

## Autenticação (JWT)

- `POST /auth/register` — cria conta (senha hasheada com bcrypt).
- `POST /auth/login` — OAuth2 password flow; retorna `access_token` (JWT).
- `GET /auth/me` — perfil do usuário autenticado.
- `/chat` e `/chat/history` exigem `Authorization: Bearer <token>`.

Cada usuário só enxerga o **próprio histórico**. A tabela `users` fica oculta do
LLM (não é exposta no schema enviado ao modelo). No Swagger (`/docs`), use o botão
**Authorize**. Usuário demo (seed): `admin@copilot.com` / `admin123`.

O fluxo segue **Ports & Adapters**: a camada de serviço depende de interfaces
(`LLMProvider`), não de implementações. Trocar o LLM = novo adapter.

## Segurança de SQL (defesa em profundidade)

1. **String**: `services/sql/validator.py` — allowlist de SELECT, bloqueia DDL/DML,
   remove comentários, proíbe múltiplas instruções, força `LIMIT`.
2. **Papel de banco**: o SQL do LLM roda com `copilot_ro` — somente-leitura, com
   `SELECT` apenas nas tabelas de negócio (não acessa `users`).
3. **Sessão**: `services/sql/executor.py` — transação `READ ONLY` + `statement_timeout`
   + `rollback` (nada é persistido).
4. **Tenant (RLS)**: o Postgres filtra as linhas por empresa (ver abaixo).

## Multi-tenant (Row-Level Security)

Cada empresa (`tenants`) só enxerga seus próprios dados — e isso **não depende do
LLM**, que poderia gerar `SELECT * FROM clientes`:

- `clientes`/`pedidos` têm `tenant_id` e uma **policy RLS**:
  `tenant_id = current_setting('app.current_tenant')`.
- O executor conecta com o papel `copilot_ro` (não-owner → sujeito ao RLS) e, a cada
  request, faz `set_config('app.current_tenant', <tenant do usuário>, true)`.
- O `tenant_id` vem **sempre do usuário autenticado** (nunca do payload). A coluna
  `tenant_id` é ocultada do schema enviado ao LLM.

Setup: em dev, `db/rls.py` cria o papel e as policies no startup. Em produção, ver a
migração `0003_multitenant_rls`. Demo: `alpha@copilot.com` / `beta@copilot.com`
(senha `admin123`) — cada um vê um conjunto de clientes diferente.

## Como rodar

```bash
poetry install
cp .env.example .env

# Sem Ollama? Use o provider determinístico:
#   LLM_PROVIDER=fake

# Suba um Postgres (ou use o docker-compose da raiz)
poetry run uvicorn app.main:app --reload

# Popular dados de exemplo manualmente (opcional; o startup já faz em dev):
poetry run seed
```

API em http://localhost:8000 · Docs em http://localhost:8000/docs · Métricas em `/metrics`.

## Testes

```bash
poetry run pytest          # validador + gerador (não exigem Postgres/Ollama)
```

## Migrações (produção)

Em produção, desabilite o `create_all` automático (`ENVIRONMENT=production`) e use:

```bash
poetry run alembic upgrade head
```
