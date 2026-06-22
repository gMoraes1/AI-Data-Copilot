"""Modelos de dados de negócio (demo).

Representam o domínio corporativo que o usuário consulta em linguagem natural:
clientes e seus pedidos. Em uma instalação real, este schema seria o banco
corporativo já existente — aqui criamos um exemplo para o Copilot consultar.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Discriminador de tenant: a qual empresa este registro pertence.
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id"), nullable=False, index=True
    )
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(180), nullable=False)

    pedidos: Mapped[list["Pedido"]] = relationship(back_populates="cliente")


class Pedido(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id"), nullable=False, index=True
    )
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False, index=True)
    valor_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pago")
    data_pedido: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    cliente: Mapped["Cliente"] = relationship(back_populates="pedidos")
