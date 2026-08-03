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

    def get_output_parser(
        self,
    ):
        """
        Retorna o parser responsável por interpretar
        a saída desta Step.

        Por padrão não existe parser.
        """

        return None

    def parse_output(
        self,
        output: str,
        context: PipelineContext,
    ):
        """
        Interpreta a saída produzida pelo processo.

        Caso a Step não possua um parser associado,
        retorna None.
        """

        parser = self.get_output_parser()

        if parser is None:
            return None

        return parser.parse(
            output=output,
            context=context,
        )

    def execute(
        self,
        context: PipelineContext,
    ) -> StepResult:
        """
        Executa a Step.
        """

        command = Command(
            executable=self.get_executable(
                context,
            ),
            working_directory=self.get_working_directory(
                context,
            ),
            arguments=self.get_arguments(
                context,
            ),
        )

        result = self._process_service.execute(
            command,
        )

        #
        # Interpreta a saída do processo.
        #

        analysis = self.parse_output(
            output=result.stdout,
            context=context,
        )

        return StepResult(
            name=self.name,
            status=(
                StepStatus.SUCCESS
                if result.status.value == "success"
                else StepStatus.FAILED
            ),
            message=result.stdout or result.stderr,
            elapsed_seconds=result.duration,
            analysis=analysis,
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
        """
        Retorna o executável da Step.
        """
        raise NotImplementedError

    @abstractmethod
    def get_working_directory(
        self,
        context: PipelineContext,
    ) -> Path:
        """
        Retorna o diretório de trabalho da Step.
        """
        raise NotImplementedError

    @abstractmethod
    def get_arguments(
        self,
        context: PipelineContext,
    ) -> list[CommandArgument]:
        """
        Retorna os argumentos da linha de comando.
        """
        raise NotImplementedError