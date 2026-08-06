"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_executor.py
Descrição : Contrato para execução de Build.
--------------------------------------------------------------------
"""

from abc import ABC
from abc import abstractmethod

from app.models.build.build_context import (
    BuildContext,
)
from app.models.build.build_result import (
    BuildResult,
)


class BuildExecutorServices(ABC):
    """
    Contrato para execução
    de uma Build.
    """

    @abstractmethod
    def execute(
        self,
        context: BuildContext,
    ) -> BuildResult:
        """
        Executa uma Build.
        """