"""Interface (porta) do provedor de LLM.

Definir uma interface abstrata desacopla o restante da aplicação de qualquer
provider específico (Ollama, OpenAI, etc.). Trocar de modelo = nova implementação,
sem tocar na camada de serviço. Padrão "Ports & Adapters" (hexagonal).
"""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Contrato mínimo que todo provedor de LLM deve cumprir."""

    @abstractmethod
    def complete(self, prompt: str, *, system: str | None = None) -> str:
        """Gera uma completude de texto para o prompt informado.

        Args:
            prompt: Texto de entrada (instrução do usuário/aplicação).
            system: Mensagem de sistema opcional (define papel/regras do modelo).

        Returns:
            O texto gerado pelo modelo, já sem metadados.

        Raises:
            LLMError: em caso de falha de comunicação ou resposta inválida.
        """
        raise NotImplementedError
