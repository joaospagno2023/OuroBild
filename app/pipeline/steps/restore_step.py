"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : restore_step.py
Descrição : Etapa responsável pela execução do dotnet restore.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.abstractions.process_service import ProcessService
from app.models.pipeline.pipeline_context import PipelineContext
from app.models.process.command_argument import CommandArgument
from app.pipeline.steps.process_step import ProcessStep


class RestoreStep(ProcessStep):
    """
    Executa o comando dotnet restore.
    """

    @property
    def name(
        self,
    ) -> str:
        return "Restore"

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
        project = context.variables["project"]

        return Path(project.project_path).parent

    def get_arguments(
        self,
        context: PipelineContext,
    ) -> list[CommandArgument]:
        project = context.variables["project"]

        return [
            CommandArgument(
                value="restore",
            ),
            CommandArgument(
                value=Path(project.project_path).name,
            ),
        ]