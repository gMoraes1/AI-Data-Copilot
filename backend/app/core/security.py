"""Primitivas de segurança: hashing de senha (bcrypt) e tokens JWT.

Isolado da camada web e de banco para ser testável e reutilizável.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import get_settings

settings = get_settings()


# --- Senhas ---------------------------------------------------------------

def hash_password(plain: str) -> str:
    """Gera o hash bcrypt de uma senha (inclui salt aleatório)."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Compara a senha em texto puro com o hash armazenado (timing-safe)."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        # hash malformado -> trata como não confere.
        return False


# --- Tokens JWT -----------------------------------------------------------

def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    """Cria um JWT assinado cujo 'sub' identifica o usuário (e-mail)."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.access_token_expire_minutes
    )
    payload = {"sub": subject, "exp": expire, "iat": datetime.now(timezone.utc)}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str | None:
    """Valida o token e retorna o 'sub' (e-mail), ou None se inválido/expirado."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        return None
    subject = payload.get("sub")
    return subject if isinstance(subject, str) else None
