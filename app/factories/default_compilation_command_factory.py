"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : default_compilation_command_factory.py
Descrição : Responsável por criar comandos de compilação.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.abstractions.compilation_command_factory import (
    CompilationCommandFactory,
)
from app.models.build.build_context import BuildContext
from app.models.build.compilation_engine import (
    CompilationEngine,
)
from app.models.process.command import Command
from app.models.process.command_argument import (
    CommandArgument,
)


class DefaultCompilationCommandFactory(
    CompilationCommandFactory,
):
    """
    Responsável por montar o comando de compilação.
    """

    def create(
        self,
        context: BuildContext,
    ) -> Command:

        project = context.project

        if (
            project.compilation_engine
            == CompilationEngine.MSBUILD
        ):
            return self.__create_msbuild_command(
                context,
            )

        return self.__create_dotnet_command(
            context,
        )

    def __create_msbuild_command(
        self,
        context: BuildContext,
    ) -> Command:

        project = context.project

        return Command(

            executable=Path("MSBuild.exe"),

            working_directory=Path(
                project.solution_path
            ).parent,

            arguments=[

                CommandArgument(
                    value=project.solution_path,
                ),

                CommandArgument(
                    value=f"/p:Configuration={project.configuration}",
                ),

                CommandArgument(
                    value=f"/p:Platform={project.platform}",
                ),
            ],
        )

    def __create_dotnet_command(
        self,
        context: BuildContext,
    ) -> Command:

        project = context.project

        return Command(

            executable=Path("dotnet"),

            working_directory=Path(
                project.project_path
            ).parent,

            arguments=[

                CommandArgument(
                    value="build",
                ),

                CommandArgument(
                    value=project.project_path,
                ),

                CommandArgument(
                    value="--configuration",
                ),

                CommandArgument(
                    value=project.configuration,
                ),
            ],
        )