"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : process_service.py
Descrição : Contrato para execução de processos externos.
--------------------------------------------------------------------
"""

from abc import ABC
from abc import abstractmethod

from app.models.process.command import Command
from app.models.process.process_result import ProcessResult


class ProcessService(ABC):
    """
    Contrato responsável pela execução de processos externos.
    """

    @abstractmethod
    def execute(
        self,
        command: Command,
    ) -> ProcessResult:
        """
        Executa um comando e retorna o resultado da execução.
        """
        pass