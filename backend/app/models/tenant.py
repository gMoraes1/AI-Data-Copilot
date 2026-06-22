"""Modelo de empresa (tenant). Base do isolamento multi-tenant."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    # 'slug' legível para identificar a empresa (ex.: usado em logs/URLs futuras).
    slug: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
