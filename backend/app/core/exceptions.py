"""Exceções de domínio da aplicação.

Cada erro de regra de negócio tem um tipo próprio, mapeado para um HTTP status
no handler global (ver app/main.py). Isso mantém a camada de serviço livre de
detalhes de HTTP.
"""


class CopilotError(Exception):
    """Erro base da aplicação."""

    status_code = 500
    message = "Erro interno."

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.message)
        self.message = message or self.message


class UnsafeSQLError(CopilotError):
    """SQL gerado pelo LLM violou as regras de segurança."""

    status_code = 422
    message = "A consulta gerada não passou na validação de segurança."


class SQLExecutionError(CopilotError):
    """Falha ao executar a consulta no banco."""

    status_code = 400
    message = "Não foi possível executar a consulta."


class LLMError(CopilotError):
    """Falha na comunicação com o provedor de LLM."""

    status_code = 502
    message = "O serviço de IA está indisponível no momento."


class AuthError(CopilotError):
    """Credenciais inválidas ou usuário não autorizado."""

    status_code = 401
    message = "Não autorizado."


class EmailAlreadyExistsError(CopilotError):
    """Tentativa de registrar um e-mail já existente."""

    status_code = 409
    message = "Este e-mail já está cadastrado."


class NotFoundError(CopilotError):
    """Recurso não encontrado (ou fora do escopo do tenant)."""

    status_code = 404
    message = "Recurso não encontrado."


class BadRequestError(CopilotError):
    """Requisição inválida (entrada malformada ou fora dos limites)."""

    status_code = 400
    message = "Requisição inválida."
