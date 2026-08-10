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

    def _log(
        self,
        message: str,
    ) -> None:
        """
        Grava informações de depuração.
        """

        Path(
            r"C:\Logs"
        ).mkdir(
            parents=True,
            exist_ok=True,
        )

        

    def execute(
        self,
        context: PipelineContext,
    ) -> StepResult:
        """
        Executa a Step.
        """

        self._log("")
        self._log("=" * 80)
        self._log(f"STEP : {self.name}")
        self._log("=" * 80)

        #
        # Command
        #

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

        self._log(f"Executável : {command.executable}")
        self._log(f"Diretório  : {command.working_directory}")

        #
        # Processo
        #

        result = self._process_service.execute(
            command,
        )

        self._log("")
        self._log("PROCESS RESULT")

        self._log(
            f"Status      : {result.status}"
        )

        self._log(
            f"Stdout Size : {len(result.stdout)}"
        )

        self._log(
            f"Stderr Size : {len(result.stderr)}"
        )

        #
        # Guarda saída completa do MSBuild
        #

        with open(
            r"C:\Logs\msbuild_output.txt",
            "w",
            encoding="utf-8",
        ) as file:

            file.write(
                result.stdout,
            )

        #
        # Parser
        #

        parser = self.get_output_parser()

        analysis = None

        if parser is None:

            self._log(
                "Parser : None"
            )

        else:

            self._log(
                f"Parser : {parser.__class__.__name__}"
            )

            analysis = parser.parse(
                output=result.stdout,
                context=context,
            )

        self._log("")
        self._log("PARSER RESULT")

        self._log(
            f"Analysis Type : {type(analysis)}"
        )

        if analysis is not None:

            if hasattr(
                analysis,
                "warnings",
            ):

                self._log(
                    f"Warnings : {len(analysis.warnings)}"
                )

            if hasattr(
                analysis,
                "errors",
            ):

                self._log(
                    f"Errors   : {len(analysis.errors)}"
                )

            if hasattr(
                analysis,
                "summary",
            ):

                self._log(
                    f"Summary  : {analysis.summary}"
                )

        else:

            self._log(
                "Analysis : None"
            )

        #
        # StepResult
        #

        step_result = StepResult(
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

        self._log("")
        self._log("STEP RESULT")

        self._log(
            f"Status : {step_result.status}"
        )

        self._log(
            f"Analysis : {type(step_result.analysis)}"
        )

        if step_result.analysis is not None:

            if hasattr(
                step_result.analysis,
                "warnings",
            ):

                self._log(
                    f"Warnings : {len(step_result.analysis.warnings)}"
                )

            if hasattr(
                step_result.analysis,
                "errors",
            ):

                self._log(
                    f"Errors   : {len(step_result.analysis.errors)}"
                )

        self._log("=" * 80)

        return step_result

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