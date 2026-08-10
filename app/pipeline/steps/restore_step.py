"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : restore_step.py
Descrição : Etapa responsável pela execução do Restore.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.abstractions.process_service import (
    ProcessService,
)
from app.models.build.compilation_engine import (
    CompilationEngine,
)
from app.models.pipeline.pipeline_context import (
    PipelineContext,
)
from app.models.process.command_argument import (
    CommandArgument,
)
from app.pipeline.steps.process_step import (
    ProcessStep,
)
from app.services.msbuild_locator import (
    MSBuildLocator,
)


class RestoreStep(ProcessStep):
    """
    Executa o Restore do projeto.
    """

    @property
    def name(
        self,
    ) -> str:
        return "Restore"

    def __init__(
        self,
        process_service: ProcessService,
        msbuild_locator: MSBuildLocator,
    ) -> None:

        super().__init__(
            process_service=process_service,
        )

        self.__msbuild_locator = (
            msbuild_locator
        )

    def get_executable(
        self,
        context: PipelineContext,
    ) -> Path:

        build_context = (
            context.variables["build_context"]
        )

        project = (
            build_context.project
        )

        if (
            project.compilation_engine
            == CompilationEngine.MSBUILD
        ):

            return (
                self.__msbuild_locator.get_msbuild_path()
            )

        return Path("dotnet")

    def get_working_directory(
        self,
        context: PipelineContext,
    ) -> Path:

        build_context = (
            context.variables["build_context"]
        )

        return (
            build_context.paths.project_file.parent
        )

    def get_arguments(
        self,
        context: PipelineContext,
    ) -> list[CommandArgument]:

        build_context = (
            context.variables["build_context"]
        )

        project = (
            build_context.project
        )

        #
        # MSBuild
        #

        if (
            project.compilation_engine
            == CompilationEngine.MSBUILD
        ):

            restore_target = (
                build_context.paths.solution_file
                or build_context.paths.project_file
            )
           

            return [

                CommandArgument(
                    value=str(
                        restore_target,
                    ),
                ),

                CommandArgument(
                    value="/t:Restore",
                ),

            ]

        #
        # DotNet
        #

        return [

            CommandArgument(
                value="restore",
            ),

            CommandArgument(
                value=str(
                    build_context.paths.project_file,
                ),
            ),

        ]