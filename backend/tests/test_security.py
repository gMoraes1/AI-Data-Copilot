"""Testes das primitivas de segurança (hashing e JWT)."""

import time

from app.core import security


def test_hash_e_verify_senha():
    hashed = security.hash_password("segredo123")
    assert hashed != "segredo123"  # nunca armazenar em texto puro.
    assert security.verify_password("segredo123", hashed)
    assert not security.verify_password("errada", hashed)


def test_hashes_diferentes_para_mesma_senha():
    # bcrypt usa salt aleatório -> hashes distintos.
    assert security.hash_password("x") != security.hash_password("x")


def test_verify_com_hash_malformado_nao_quebra():
    assert security.verify_password("x", "nao-e-um-hash") is False


def test_token_roundtrip():
    token = security.create_access_token("user@test.com")
    assert security.decode_access_token(token) == "user@test.com"


def test_token_invalido_retorna_none():
    assert security.decode_access_token("token.falso.aqui") is None


def test_token_expirado_retorna_none():
    token = security.create_access_token("user@test.com", expires_minutes=-1)
    time.sleep(0.01)
    assert security.decode_access_token(token) is None
