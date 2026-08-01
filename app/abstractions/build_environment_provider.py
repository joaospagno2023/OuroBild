"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_environment_provider.py
Descrição : Contrato responsável por preparar um BuildContext.
--------------------------------------------------------------------
"""

from abc import ABC
from abc import abstractmethod

from app.models.build.build_context import BuildContext


class BuildEnvironmentProvider(ABC):
    """
    Contrato para preparação do ambiente de Build.
    """

    @abstractmethod
    def prepare(
        self,
        context: BuildContext,
    ) -> None:
        """
        Prepara o BuildContext.

        Cada implementação deverá preencher
        os caminhos necessários para execução
        da Pipeline.
        """
        raise NotImplementedError