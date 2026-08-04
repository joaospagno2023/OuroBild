"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_command_factory.py
Descrição : Responsável por montar o comando de Build.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.models.pipeline.pipeline_context import (
    PipelineContext,
)
from app.models.process.command import Command
from app.models.process.command_argument import (
    CommandArgument,
)
from app.services.msbuild_locator import (
    MSBuildLocator,
)


class BuildCommandFactory:
    """
    Responsável por montar o comando de Build.
    """

    def __init__(
        self,
        msbuild_locator: MSBuildLocator,
    ) -> None:

        self.__msbuild_locator = (
            msbuild_locator
        )

    def create(
        self,
        context: PipelineContext,
    ) -> Command:

        build_context = (
            context.variables["build_context"]
        )

        project = build_context.project

        #
        # MSBuild
        #

        if (
            project.compilation_engine
            == "msbuild"
        ):

            executable = (
                self.__msbuild_locator.get_msbuild_path()
            )

            arguments = [

                CommandArgument(
                    value=build_context.paths.project_file.name,
                ),

                CommandArgument(
                    value=f"/p:Configuration={project.configuration}",
                ),

                CommandArgument(
                    value=f"/p:Platform={project.platform}",
                ),

                CommandArgument(
                    value="/restore",
                ),
            ]

        #
        # DotNet CLI
        #

        else:

            executable = Path(
                "dotnet",
            )

            arguments = [

                CommandArgument(
                    value="build",
                ),

                CommandArgument(
                    value=build_context.paths.project_file.name,
                ),

                CommandArgument(
                    value="--configuration",
                ),

                CommandArgument(
                    value=project.configuration,
                ),

                CommandArgument(
                    value="--no-restore",
                ),
            ]

        return Command(

            executable=executable,

            working_directory=(
                build_context.paths.project_file.parent
            ),

            arguments=arguments,
        )