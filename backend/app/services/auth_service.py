"""AuthService — casos de uso de autenticação (registro e login)."""

import re

from app.core.exceptions import AuthError, EmailAlreadyExistsError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.tenant import Tenant
from app.models.user import User
from app.repositories.tenant_repository import TenantRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserCreate


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:60] or "empresa"


class AuthService:
    def __init__(self, users: UserRepository, tenants: TenantRepository) -> None:
        self._users = users
        self._tenants = tenants

    def register(self, data: UserCreate) -> User:
        if self._users.get_by_email(data.email):
            raise EmailAlreadyExistsError()

        # Cada novo cadastro cria a própria empresa (tenant). Em um produto real,
        # o usuário entraria por convite em um tenant existente.
        slug = _slugify(data.email)
        tenant = self._tenants.get_by_slug(slug)
        if tenant is None:
            company = data.full_name or data.email.split("@")[0]
            tenant = self._tenants.add(Tenant(name=f"Empresa de {company}", slug=slug))

        user = User(
            tenant_id=tenant.id,
            email=data.email,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
        )
        return self._users.add(user)

    def authenticate(self, email: str, password: str) -> User:
        """Valida credenciais; lança AuthError se inválidas (sem revelar qual parte)."""
        user = self._users.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise AuthError("E-mail ou senha inválidos.")
        if not user.is_active:
            raise AuthError("Usuário inativo.")
        return user

    def login(self, email: str, password: str) -> str:
        """Autentica e retorna um access token JWT."""
        user = self.authenticate(email, password)
        return create_access_token(subject=user.email)
