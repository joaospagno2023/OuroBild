"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : msbuild_command_factory.py
Descrição : Factory responsável por criar comandos MSBuild.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.abstractions.compilation_command_factory import (
    CompilationCommandFactory,
)
from app.models.build.build_context import BuildContext
from app.models.process.command import Command


class MSBuildCommandFactory(
    CompilationCommandFactory,
):
    """
    Cria comandos utilizando o MSBuild.
    """

    def create(
        self,
        context: BuildContext,
    ) -> Command:

        raise NotImplementedError