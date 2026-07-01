"""DTOs (Pydantic) do Dashboard — métricas agregadas do tenant para os gráficos.

Todos os números já vêm calculados e escopados por empresa (tenant). O frontend
apenas renderiza; nenhuma lógica de agregação vive no cliente.
"""

from pydantic import BaseModel, Field


class Kpis(BaseModel):
    """Indicadores-chave exibidos como cartões no topo do dashboard."""

    faturamento_total: float = Field(0.0, description="Soma de valor_total dos pedidos pagos.")
    total_pedidos: int = Field(0, description="Quantidade de pedidos.")
    ticket_medio: float = Field(0.0, description="Faturamento pago / nº de pedidos pagos.")
    pedidos_atrasados: int = Field(0, description="Pedidos com status 'atrasado'.")
    total_clientes: int = Field(0, description="Clientes distintos da empresa.")


class RevenuePoint(BaseModel):
    """Um ponto da série temporal de faturamento (agrupado por mês)."""

    mes: str = Field(..., description="Mês no formato YYYY-MM.", examples=["2026-05"])
    valor: float = Field(0.0, description="Faturamento pago no mês.")


class StatusSlice(BaseModel):
    """Distribuição de pedidos por status (para gráfico de pizza)."""

    status: str
    quantidade: int = 0
    valor: float = 0.0


class TopCliente(BaseModel):
    """Cliente no ranking de faturamento (para gráfico de barras)."""

    nome: str
    valor_total: float = 0.0
    pedidos: int = 0


class DashboardData(BaseModel):
    """Payload completo consumido pela página de Dashboard."""

    kpis: Kpis = Field(default_factory=Kpis)
    faturamento_mensal: list[RevenuePoint] = Field(default_factory=list)
    pedidos_por_status: list[StatusSlice] = Field(default_factory=list)
    top_clientes: list[TopCliente] = Field(default_factory=list)
