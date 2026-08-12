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

from app.models.build.build_context import (
    BuildContext,
)

from app.models.process.command import (
    Command,
)

from app.models.process.command_argument import (
    CommandArgument,
)

from app.services.msbuild_locator import (
    MSBuildLocator,
)


class MSBuildCommandFactory(
    CompilationCommandFactory,
):
    """
    Cria comandos utilizando o MSBuild.
    """

    def __init__(
        self,
        msbuild_locator: MSBuildLocator,
    ) -> None:
        """
        Inicializa a Factory.
        """

        self.__msbuild_locator = (
            msbuild_locator
        )

    def create(
        self,
        context: BuildContext,
    ) -> Command:
        """
        Cria o comando MSBuild correspondente
        ao contexto de Build.
        """

        executable = (
            self.__msbuild_locator.get_msbuild_path()
        )

        arguments = [
            CommandArgument(
                value=(
                    context.paths.project_file.name
                ),
            ),

            CommandArgument(
                value=(
                    f"/p:Configuration="
                    f"{context.project.configuration}"
                ),
            ),

            CommandArgument(
                value=(
                    f"/p:Platform="
                    f"{context.project.platform}"
                ),
            ),

            CommandArgument(
                value="/restore",
            ),
        ]

        return Command(
            executable=Path(
                executable,
            ),
            working_directory=(
                context.paths.project_file.parent
            ),
            arguments=arguments,
        )