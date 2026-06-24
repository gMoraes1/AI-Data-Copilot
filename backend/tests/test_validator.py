"""Testes da camada de validação de segurança de SQL (sem dependências externas)."""

import pytest

from app.core.exceptions import UnsafeSQLError
from app.services.sql import validator


def test_permite_select_simples():
    sql = validator.sanitize_and_validate("SELECT * FROM clientes")
    assert sql.lower().startswith("select")


def test_permite_cte_with():
    sql = "WITH t AS (SELECT 1 AS n) SELECT n FROM t"
    assert validator.sanitize_and_validate(sql)


def test_remove_code_fences():
    raw = "```sql\nSELECT 1\n```"
    assert validator.sanitize_and_validate(raw) == "SELECT 1"


def test_remove_ponto_e_virgula_final():
    assert validator.sanitize_and_validate("SELECT 1;") == "SELECT 1"


@pytest.mark.parametrize(
    "sql",
    [
        "DROP TABLE clientes",
        "DELETE FROM pedidos",
        "UPDATE pedidos SET valor_total = 0",
        "INSERT INTO clientes (nome) VALUES ('x')",
        "ALTER TABLE clientes ADD COLUMN x int",
        "TRUNCATE clientes",
    ],
)
def test_bloqueia_comandos_de_escrita(sql):
    with pytest.raises(UnsafeSQLError):
        validator.sanitize_and_validate(sql)


def test_bloqueia_multiplas_instrucoes():
    with pytest.raises(UnsafeSQLError):
        validator.sanitize_and_validate("SELECT 1; DROP TABLE clientes")


def test_bloqueia_escrita_escondida_em_comentario():
    # O comando real é um DELETE disfarçado após um comentário de linha.
    sql = "SELECT 1\n-- inocente\n; DELETE FROM clientes"
    with pytest.raises(UnsafeSQLError):
        validator.sanitize_and_validate(sql)


def test_enforce_row_limit_adiciona_limit():
    assert "LIMIT 50" in validator.enforce_row_limit("SELECT 1", 50)


def test_enforce_row_limit_respeita_existente():
    sql = "SELECT 1 LIMIT 5"
    assert validator.enforce_row_limit(sql, 50) == sql
