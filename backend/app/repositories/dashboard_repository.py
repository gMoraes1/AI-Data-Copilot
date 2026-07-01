"""Repositório de agregações para o Dashboard (padrão Repository).

Diferente do SQL gerado pelo LLM (não confiável, isolado por RLS + papel
read-only), estas consultas são código nosso e confiável — filtram o tenant
explicitamente na sessão principal. A camada de serviço não conhece SQLAlchemy.
"""

from collections import defaultdict
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.business import Cliente, Pedido


def _f(value: object) -> float:
    """Converte Decimal/None para float serializável."""
    if isinstance(value, Decimal):
        return float(value)
    return float(value or 0)


class DashboardRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def kpis(self, tenant_id: int) -> dict:
        pagos = (Pedido.tenant_id == tenant_id, Pedido.status == "pago")

        faturamento = self._session.scalar(
            select(func.coalesce(func.sum(Pedido.valor_total), 0)).where(*pagos)
        )
        pedidos_pagos = self._session.scalar(
            select(func.count()).select_from(Pedido).where(*pagos)
        )
        total_pedidos = self._session.scalar(
            select(func.count()).select_from(Pedido).where(Pedido.tenant_id == tenant_id)
        )
        atrasados = self._session.scalar(
            select(func.count())
            .select_from(Pedido)
            .where(Pedido.tenant_id == tenant_id, Pedido.status == "atrasado")
        )
        total_clientes = self._session.scalar(
            select(func.count()).select_from(Cliente).where(Cliente.tenant_id == tenant_id)
        )

        faturamento_f = _f(faturamento)
        ticket_medio = faturamento_f / pedidos_pagos if pedidos_pagos else 0.0
        return {
            "faturamento_total": faturamento_f,
            "total_pedidos": int(total_pedidos or 0),
            "ticket_medio": round(ticket_medio, 2),
            "pedidos_atrasados": int(atrasados or 0),
            "total_clientes": int(total_clientes or 0),
        }

    def faturamento_mensal(self, tenant_id: int) -> list[dict]:
        """Faturamento pago agrupado por mês (YYYY-MM).

        Agrupa em Python para ser portável entre Postgres (produção) e SQLite
        (testes), evitando date_trunc/strftime específicos de cada dialeto.
        """
        rows = self._session.execute(
            select(Pedido.data_pedido, Pedido.valor_total).where(
                Pedido.tenant_id == tenant_id, Pedido.status == "pago"
            )
        ).all()

        por_mes: dict[str, float] = defaultdict(float)
        for data_pedido, valor in rows:
            por_mes[data_pedido.strftime("%Y-%m")] += _f(valor)

        return [{"mes": mes, "valor": round(por_mes[mes], 2)} for mes in sorted(por_mes)]

    def pedidos_por_status(self, tenant_id: int) -> list[dict]:
        rows = self._session.execute(
            select(
                Pedido.status,
                func.count().label("quantidade"),
                func.coalesce(func.sum(Pedido.valor_total), 0).label("valor"),
            )
            .where(Pedido.tenant_id == tenant_id)
            .group_by(Pedido.status)
            .order_by(func.count().desc())
        ).all()
        return [
            {"status": status, "quantidade": int(qtd), "valor": _f(valor)}
            for status, qtd, valor in rows
        ]

    def top_clientes(self, tenant_id: int, limit: int = 5) -> list[dict]:
        rows = self._session.execute(
            select(
                Cliente.nome,
                func.coalesce(func.sum(Pedido.valor_total), 0).label("valor_total"),
                func.count(Pedido.id).label("pedidos"),
            )
            .join(Pedido, Pedido.cliente_id == Cliente.id)
            .where(Cliente.tenant_id == tenant_id)
            .group_by(Cliente.id, Cliente.nome)
            .order_by(func.sum(Pedido.valor_total).desc())
            .limit(limit)
        ).all()
        return [
            {"nome": nome, "valor_total": _f(valor), "pedidos": int(pedidos)}
            for nome, valor, pedidos in rows
        ]
