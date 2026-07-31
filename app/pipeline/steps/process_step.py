"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : process_step.py
Descrição : Classe base para Steps que executam processos externos.
--------------------------------------------------------------------
"""

from abc import ABC
from abc import abstractmethod
from pathlib import Path

from app.abstractions.process_service import ProcessService
from app.models.pipeline.pipeline_context import PipelineContext
from app.models.pipeline.step_result import StepResult
from app.models.pipeline.step_status import StepStatus
from app.models.process.command import Command
from app.models.process.command_argument import CommandArgument
from app.pipeline.abstractions.pipeline_step import PipelineStep


class ProcessStep(
    PipelineStep,
    ABC,
):
    """
    Classe base para execução de processos externos.
    """

    def __init__(
        self,
        process_service: ProcessService,
    ) -> None:
        self._process_service = process_service

    def execute(
        self,
        context: PipelineContext,
    ) -> StepResult:
        """
        Executa a Step.
        """

        command = Command(
            executable=self.get_executable(context),
            working_directory=self.get_working_directory(context),
            arguments=self.get_arguments(context),
        )

        result = self._process_service.execute(command)

        return StepResult(
            name=self.name,
            status=(
                StepStatus.SUCCESS
                if result.status.value == "success"
                else StepStatus.FAILED
            ),
            message=result.stdout or result.stderr,
            elapsed_seconds=result.duration,
        )

    @property
    @abstractmethod
    def name(
        self,
    ) -> str:
        """
        Nome amigável da Step.
        """
        raise NotImplementedError

    @abstractmethod
    def get_executable(
        self,
        context: PipelineContext,
    ) -> Path:
        raise NotImplementedError

    @abstractmethod
    def get_working_directory(
        self,
        context: PipelineContext,
    ) -> Path:
        raise NotImplementedError

    @abstractmethod
    def get_arguments(
        self,
        context: PipelineContext,
    ) -> list[CommandArgument]:
        raise NotImplementedError