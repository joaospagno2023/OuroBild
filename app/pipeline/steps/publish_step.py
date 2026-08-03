"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_step.py
Descrição : Etapa responsável pela execução do dotnet publish.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.abstractions.process_service import ProcessService
from app.models.pipeline.pipeline_context import PipelineContext
from app.models.process.command_argument import CommandArgument
from app.pipeline.steps.process_step import ProcessStep


class PublishStep(ProcessStep):
    """
    Executa o comando dotnet publish.
    """

    @property
    def name(
        self,
    ) -> str:
        return "Publish"

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
                value="publish",
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
                value="--output",
            ),

            CommandArgument(
                value=str(
                    build_context.paths.publish_root
                ),
            ),

            CommandArgument(
                value="--no-build",
            ),
        ]