"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : process_service.py
Descrição : Contrato para execução de processos externos.
--------------------------------------------------------------------
"""

from abc import ABC, abstractmethod

from app.models.process.command import (
    Command,
)
from app.models.process.process_result import (
    ProcessResult,
)


class ProcessService(ABC):
    """Define o contrato para execução de comandos externos."""

    @abstractmethod
    def execute(
        self,
        command: Command,
    ) -> ProcessResult:
        """Executa um comando e retorna seu resultado."""

        raise NotImplementedError
