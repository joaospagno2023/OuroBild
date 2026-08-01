"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_environment_builder.py
Descrição : Contrato responsável por preparar o contexto de Build.
--------------------------------------------------------------------
"""

from abc import ABC
from abc import abstractmethod

from app.models.build.build_context import BuildContext


class BuildEnvironmentBuilder(ABC):
    """
    Responsável por preparar o ambiente de execução.
    """

    @abstractmethod
    def build(
        self,
        context: BuildContext,
    ) -> None:
        """
        Constrói o contexto de Build.
        """
        raise NotImplementedError