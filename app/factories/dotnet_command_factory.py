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

from app.models.build.build_context import (
    BuildContext,
)

from app.models.process.command import (
    Command,
)

from app.models.process.command_argument import (
    CommandArgument,
)


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
        """
        Cria o comando de Build utilizando
        a CLI do .NET.
        """

        project_file = (
            context.paths.project_file
        )

        configuration = (
            context.project.configuration
        )

        arguments = [
            CommandArgument(
                value="build",
            ),

            CommandArgument(
                value=str(
                    project_file.name,
                ),
            ),

            CommandArgument(
                value="--configuration",
            ),

            CommandArgument(
                value=configuration,
            ),

            CommandArgument(
                value="--no-restore",
            ),
        ]

        return Command(
            executable=Path(
                "dotnet",
            ),
            working_directory=(
                project_file.parent
            ),
            arguments=arguments,
        )