"""Repositório de empresas (tenants)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tenant import Tenant


class TenantRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_slug(self, slug: str) -> Tenant | None:
        return self._session.scalar(select(Tenant).where(Tenant.slug == slug))

    def add(self, tenant: Tenant) -> Tenant:
        self._session.add(tenant)
        self._session.commit()
        self._session.refresh(tenant)
        return tenant
