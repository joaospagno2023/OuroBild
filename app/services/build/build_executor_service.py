"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_executor_service.py
Descrição : Contrato para execução de Build.
--------------------------------------------------------------------
"""

from abc import ABC
from abc import abstractmethod

from app.models.build.build_context import (
    BuildContext,
)
from app.models.process.process_result import (
    ProcessResult,
)


class BuildExecutorService(
    ABC,
):
    """
    Contrato para execução
    de uma Build.
    """

    @abstractmethod
    def execute(
        self,
        context: BuildContext,
    ) -> ProcessResult:
        """
        Executa uma Build.

        Returns:
            Resultado da execução do processo.
        """

        raise NotImplementedError()