"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : process_executor_service.py
Descrição : Contrato para execução de processos.
--------------------------------------------------------------------
"""

from abc import ABC
from abc import abstractmethod
from pathlib import Path

from app.models.process.process_result import (
    ProcessResult,
)


class ProcessExecutorService(
    ABC,
):
    """
    Contrato para execução
    de processos externos.
    """

    @abstractmethod
    def execute(
        self,
        executable: str,
        arguments: list[str],
        working_directory: Path,
    ) -> ProcessResult:
        """
        Executa um processo externo.
        """

        raise NotImplementedError()