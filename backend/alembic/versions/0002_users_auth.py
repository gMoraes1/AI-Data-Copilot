"""Auth: tabela users e coluna user_id em chat_history.

Revision ID: 0002_users_auth
Revises: 0001_initial
Create Date: 2026-06-16
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_users_auth"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=180), nullable=False, unique=True),
        sa.Column("full_name", sa.String(length=120), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.add_column("chat_history", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_index("ix_chat_history_user_id", "chat_history", ["user_id"])
    op.create_foreign_key(
        "fk_chat_history_user_id", "chat_history", "users", ["user_id"], ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("fk_chat_history_user_id", "chat_history", type_="foreignkey")
    op.drop_index("ix_chat_history_user_id", table_name="chat_history")
    op.drop_column("chat_history", "user_id")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
