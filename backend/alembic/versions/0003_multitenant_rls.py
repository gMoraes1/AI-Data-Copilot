"""Multi-tenant: tabela tenants, tenant_id nas tabelas e Row-Level Security.

Revision ID: 0003_multitenant_rls
Revises: 0002_users_auth
Create Date: 2026-06-16

Observação: a criação do papel somente-leitura (copilot_ro) costuma ser
provisionada pela infraestrutura. Incluímos aqui de forma idempotente para
facilitar ambientes de demonstração; ajuste a senha conforme seu secret manager.
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_multitenant_rls"
down_revision: str | None = "0002_users_auth"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_RO_ROLE = "copilot_ro"
_RO_PASSWORD = "copilot_ro"
_TABLES = ("clientes", "pedidos")


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False, unique=True),
        sa.Column("slug", sa.String(length=60), nullable=False, unique=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # tenant_id nas tabelas (tabelas vazias em uma migração limpa -> NOT NULL ok).
    for table in ("users", "clientes", "pedidos"):
        op.add_column(table, sa.Column("tenant_id", sa.Integer(), nullable=False))
        op.create_index(f"ix_{table}_tenant_id", table, ["tenant_id"])
        op.create_foreign_key(
            f"fk_{table}_tenant_id", table, "tenants", ["tenant_id"], ["id"]
        )

    # E-mail de cliente deixa de ser único global (pode repetir entre empresas).
    op.drop_constraint("clientes_email_key", "clientes", type_="unique")

    # --- Papel somente-leitura + RLS ---
    op.execute(
        sa.text(
            f"""
            DO $$ BEGIN
              IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{_RO_ROLE}') THEN
                CREATE ROLE {_RO_ROLE} LOGIN PASSWORD '{_RO_PASSWORD}';
              END IF;
            END $$;
            """
        )
    )
    op.execute(sa.text(f"GRANT USAGE ON SCHEMA public TO {_RO_ROLE}"))
    for table in _TABLES:
        op.execute(sa.text(f"GRANT SELECT ON {table} TO {_RO_ROLE}"))
        op.execute(sa.text(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY"))
        op.execute(sa.text(f"DROP POLICY IF EXISTS tenant_isolation ON {table}"))
        op.execute(
            sa.text(
                f"CREATE POLICY tenant_isolation ON {table} FOR SELECT "
                "USING (tenant_id = current_setting('app.current_tenant', true)::int)"
            )
        )


def downgrade() -> None:
    for table in _TABLES:
        op.execute(sa.text(f"DROP POLICY IF EXISTS tenant_isolation ON {table}"))
        op.execute(sa.text(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY"))
        op.execute(sa.text(f"REVOKE SELECT ON {table} FROM {_RO_ROLE}"))

    op.create_unique_constraint("clientes_email_key", "clientes", ["email"])
    for table in ("pedidos", "clientes", "users"):
        op.drop_constraint(f"fk_{table}_tenant_id", table, type_="foreignkey")
        op.drop_index(f"ix_{table}_tenant_id", table_name=table)
        op.drop_column(table, "tenant_id")

    op.drop_table("tenants")
