# Corporate AI Copilot

## Visão Geral

O Corporate AI Copilot é uma plataforma que permite que usuários de negócio consultem dados corporativos utilizando linguagem natural.

Ao invés de escrever consultas SQL manualmente, o usuário pode fazer perguntas como:

- Quais foram os clientes que mais compraram este mês?
- Qual foi o faturamento dos últimos 6 meses?
- Quantos pedidos estão atrasados?

A aplicação utiliza um LLM para interpretar a intenção do usuário, gerar consultas SQL seguras, executar as consultas em um banco PostgreSQL e retornar respostas em linguagem natural.

O objetivo é simular uma solução corporativa real utilizada por empresas para democratizar o acesso aos dados internos.

---

## Objetivos do Projeto

- Backend Python (FastAPI)
- Arquitetura de software
- Integração com LLMs
- PostgreSQL
- Docker
- Kubernetes
- Observabilidade
- Segurança em geração de SQL
- Aplicações corporativas baseadas em IA

---

## Problema que o Projeto Resolve

Em muitas empresas, usuários de negócio dependem de desenvolvedores ou analistas para obter informações do banco de dados.

Exemplo:

> Qual cliente mais comprou este mês?

Normalmente alguém precisa:
1. Entender a solicitação.
2. Escrever SQL.
3. Executar a consulta.
4. Interpretar os resultados.
5. Enviar a resposta.

O Corporate AI Copilot reduz esse processo para uma simples conversa.

---

## Arquitetura Geral

Frontend (React/Next.js)
↓
FastAPI
↓
LLM (Ollama + Llama)
↓
SQL Generator
↓
PostgreSQL
↓
Result Analyzer
↓
Natural Language Response

---

## Fluxo Completo

### 1. Usuário faz uma pergunta

Exemplo:

"Quais foram os 10 clientes que mais compraram este mês?"

### 2. Backend recebe a solicitação

Endpoint:

POST /chat

Payload:

{
  "question": "Quais foram os 10 clientes que mais compraram este mês?"
}

### 3. Sistema obtém o esquema do banco

Exemplo:

{
  "clientes": ["id", "nome", "email"],
  "pedidos": ["id", "cliente_id", "valor_total", "data_pedido"]
}

### 4. LLM gera SQL

O modelo recebe:
- Pergunta do usuário
- Esquema do banco
- Regras de segurança

Retorna apenas SQL válido.

### 5. SQL é validado

Regras:
- Permitir apenas SELECT
- Bloquear DROP
- Bloquear DELETE
- Bloquear UPDATE
- Bloquear ALTER
- Bloquear TRUNCATE

### 6. SQL é executado

O backend executa a consulta utilizando SQLAlchemy.

### 7. Resultados são analisados

Exemplo:

[
  {
    "nome": "Empresa A",
    "total": 35000
  }
]

### 8. LLM gera resposta amigável

Exemplo:

"A Empresa A foi a cliente que mais comprou neste mês, totalizando R$ 35.000."

---

## Funcionalidades MVP

- Chat com banco de dados
- Geração automática de SQL
- Validação de SQL
- PostgreSQL
- Histórico de perguntas
- Respostas em linguagem natural

---

## Funcionalidades Futuras

### Dashboard Inteligente

Pergunta:

"Mostre o faturamento dos últimos 12 meses"

Resposta:

- SQL
- Dados
- Gráfico

### Multiempresa (Multi-Tenant)

Cada empresa acessa apenas seus próprios dados.

### Observabilidade

- Prometheus
- Grafana
- Logs estruturados

### Kubernetes

Deploy completo utilizando:
- Deployment
- Service
- ConfigMap
- Secrets
- Ingress

### RAG Corporativo

Permitir consulta de:
- PDFs
- Contratos
- Procedimentos internos
- Documentação empresarial

---

## Stack Tecnológica

Backend:
- Python
- FastAPI
- SQLAlchemy
- Alembic

Banco:
- PostgreSQL

IA:
- Ollama
- Llama 3

Infraestrutura:
- Docker
- Docker Compose
- Kubernetes

Observabilidade:
- Prometheus
- Grafana

---

## Diferencial do Projeto

Este projeto não é apenas um chatbot.

O sistema:

- Interpreta linguagem natural
- Converte perguntas em SQL
- Valida consultas
- Executa consultas reais
- Analisa resultados
- Gera insights para usuários de negócio

O objetivo é simular um produto corporativo real que poderia ser utilizado dentro de empresas para democratizar o acesso aos dados.
