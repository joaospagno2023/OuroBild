"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_executor_factory.py
Descrição : Factory responsável por fornecer o executor de Build.
--------------------------------------------------------------------
"""

from abc import ABC
from abc import abstractmethod

from app.models.build.compilation_engine import (
    CompilationEngine,
)
from app.services.build.build_executor_service import (
    BuildExecutorService,
)


class BuildExecutorFactory(
    ABC,
):
    """
    Responsável por fornecer
    o executor adequado.
    """

    @abstractmethod
    def create(
        self,
        engine: CompilationEngine,
    ) -> BuildExecutorService:
        """
        Retorna o executor correspondente.
        """

        raise NotImplementedError()