"""Popula o banco com 2 empresas (tenants), dados de negócio e usuários demo.

Idempotente. Os dois tenants permitem VER o isolamento multi-tenant:
- alpha@copilot.com (Empresa Alpha) -> enxerga só clientes/pedidos da Alpha.
- beta@copilot.com  (Empresa Beta)  -> enxerga só os da Beta.

Pode ser executado via `poetry run seed` ou automaticamente no startup (dev).
"""

from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.business import Cliente, Pedido
from app.models.tenant import Tenant
from app.models.user import User

logger = get_logger(__name__)

_PASSWORD = "admin123"

# slug -> (nome da empresa, e-mail do usuário demo)
_TENANTS = {
    "alpha": ("Empresa Alpha", "alpha@copilot.com"),
    "beta": ("Empresa Beta", "beta@copilot.com"),
}

# slug do tenant -> lista de (nome_cliente, email, [(valor, status, dias_atras), ...])
_DATA = {
    "alpha": [
        ("Empresa A", "contato@empresaa.com.br", [("35000.00", "pago", 5), ("12000.00", "pago", 20)]),
        ("Empresa B", "contato@empresab.com.br", [("18000.00", "pago", 3), ("9000.00", "atrasado", 40)]),
        ("Indústria Delta", "compras@delta.com.br", [("41000.00", "pago", 8), ("15000.00", "pago", 33)]),
    ],
    "beta": [
        ("Empresa C", "contato@empresac.com.br", [("27000.00", "pago", 12), ("5000.00", "atrasado", 65)]),
        ("Comércio Ômega", "financeiro@omega.com.br", [("8000.00", "pago", 2), ("22000.00", "atrasado", 50)]),
    ],
}


def seed(session: Session) -> None:
    if session.scalar(select(func.count()).select_from(Tenant)):
        logger.info("Seed ignorado: tenants já existem")
        return

    today = date(2026, 6, 11)
    for slug, (name, user_email) in _TENANTS.items():
        tenant = Tenant(name=name, slug=slug)
        session.add(tenant)
        session.flush()  # garante tenant.id

        session.add(
            User(
                tenant_id=tenant.id,
                email=user_email,
                full_name=f"Admin {name}",
                hashed_password=hash_password(_PASSWORD),
            )
        )

        for nome, email, pedidos in _DATA[slug]:
            cliente = Cliente(tenant_id=tenant.id, nome=nome, email=email)
            session.add(cliente)
            session.flush()
            for valor, status, dias in pedidos:
                session.add(
                    Pedido(
                        tenant_id=tenant.id,
                        cliente_id=cliente.id,
                        valor_total=Decimal(valor),
                        status=status,
                        data_pedido=today - timedelta(days=dias),
                    )
                )

    session.commit()
    logger.info("Seed concluído", extra={"tenants": len(_TENANTS)})


def main() -> None:
    """Entry point para `poetry run seed`."""
    with SessionLocal() as session:
        seed(session)


if __name__ == "__main__":
    main()
