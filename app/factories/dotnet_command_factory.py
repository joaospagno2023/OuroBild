"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : dotnet_command_factory.py
Descrição : Factory responsável por criar comandos dotnet.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.abstractions.compilation_command_factory import (
    CompilationCommandFactory,
)
from app.models.build.build_context import BuildContext
from app.models.process.command import Command


class DotnetCommandFactory(
    CompilationCommandFactory,
):
    """
    Cria comandos utilizando o dotnet CLI.
    """

    def create(
        self,
        context: BuildContext,
    ) -> Command:

        raise NotImplementedError