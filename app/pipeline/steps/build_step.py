"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_step.py
Descrição : Etapa responsável pela execução do dotnet build.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.abstractions.process_service import ProcessService
from app.models.pipeline.pipeline_context import PipelineContext
from app.models.process.command_argument import CommandArgument
from app.parsers.msbuild.msbuild_parser import MsBuildParser
from app.pipeline.steps.process_step import ProcessStep


class BuildStep(ProcessStep):
    """
    Executa o comando dotnet build.
    """

    @property
    def name(
        self,
    ) -> str:
        return "Build"

    def __init__(
        self,
        process_service: ProcessService,
    ) -> None:

        super().__init__(
            process_service=process_service,
        )

    def get_executable(
        self,
        context: PipelineContext,
    ) -> Path:

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

        project = build_context.project

        return [

            CommandArgument(
                value="build",
            ),

            CommandArgument(
                value=(
                    build_context.paths.project_file.name
                ),
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

    def get_output_parser(
        self,
    ):
        """
        Retorna o parser responsável por interpretar
        a saída do processo de Build.
        """

        return MsBuildParser()