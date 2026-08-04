"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : compilation_command_factory.py
Descrição : Contrato responsável por criar comandos de compilação.
--------------------------------------------------------------------
"""

from abc import ABC
from abc import abstractmethod

from app.models.build.build_context import BuildContext
from app.models.process.command import Command


class CompilationCommandFactory(
    ABC,
):
    """
    Cria o comando responsável por compilar um projeto.
    """

    @abstractmethod
    def create(
        self,
        context: BuildContext,
    ) -> Command:
        """
        Cria o comando de compilação.
        """
        raise NotImplementedError