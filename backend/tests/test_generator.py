"""Testes do SQLGenerator usando o provider fake (sem Ollama)."""

from app.services.llm.fake import FakeLLMProvider
from app.services.sql.generator import SQLGenerator

SCHEMA = {
    "clientes": ["id", "nome", "email"],
    "pedidos": ["id", "cliente_id", "valor_total", "status", "data_pedido"],
}


def test_gera_select_para_top_clientes():
    gen = SQLGenerator(FakeLLMProvider(), max_rows=200)
    sql = gen.generate("Quais os 10 clientes que mais compraram?", SCHEMA)
    assert sql.lower().startswith("select")
    assert "clientes" in sql.lower()


def test_gera_sql_com_limit_garantido():
    gen = SQLGenerator(FakeLLMProvider(), max_rows=200)
    sql = gen.generate("Quantos pedidos estão atrasados?", SCHEMA)
    assert "limit" in sql.lower()
