"""Rotas de autenticação: registro, login e perfil do usuário atual."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import AuthServiceDep, CurrentUser
from app.schemas.auth import Token, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=201, summary="Criar conta")
def register(payload: UserCreate, service: AuthServiceDep) -> UserRead:
    user = service.register(payload)
    return UserRead.model_validate(user)


@router.post("/login", response_model=Token, summary="Login (OAuth2 password flow)")
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: AuthServiceDep,
) -> Token:
    # OAuth2PasswordRequestForm usa o campo 'username' — aqui ele carrega o e-mail.
    token = service.login(form.username, form.password)
    return Token(access_token=token)


@router.get("/me", response_model=UserRead, summary="Perfil do usuário autenticado")
def me(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)
