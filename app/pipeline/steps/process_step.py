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

        self._log(
            f"Executável : {command.executable}"
        )

        self._log(
            f"Diretório  : {command.working_directory}"
        )

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

        Path(
            r"C:\Logs"
        ).mkdir(
            parents=True,
            exist_ok=True,
        )

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

        is_build_step = (
            self.name.lower() == "build"
        )

        analysis_errors = list(
            getattr(
                analysis,
                "errors",
                [],
            )
            or []
        )

        has_analysis_errors = bool(
            analysis_errors
        )

        step_failed = (
            result.status.value != "success"
            or (
                is_build_step
                and has_analysis_errors
            )
        )

        if step_failed:

            #
            # Não coloca stdout/stderr completos no
            # StepResult. O conteúdo completo já está
            # disponível em C:\Logs\msbuild_output.txt.
            #

            warnings_count = self.__get_warnings_count(
                analysis,
            )

            errors_count = len(
                analysis_errors
            )

            if is_build_step:

                step_message = (
                    "Build falhou. "
                    f"{errors_count} erro(s) e "
                    f"{warnings_count} aviso(s) "
                    "de compilação."
                )

            else:

                step_message = (
                    "Etapa não concluída "
                    "com sucesso."
                )

            #
            # Mantém somente os erros estruturados
            # no resultado da API.
            #

            step_errors = [
                self.__format_build_error(
                    error
                )
                for error in analysis_errors
            ]

            #
            # Se não houver parser/erro estruturado,
            # usa o stderr como erro resumido.
            #

            if (
                not step_errors
                and result.stderr
            ):

                step_errors = [
                    result.stderr.strip()
                ]

        else:

            step_message = (
                self.__success_step_message(
                    analysis=analysis,
                )
            )

            step_errors = []

            #
            # Warnings detalhados podem ser muito grandes.
            # Mantemos somente o total no resultado público
            # quando a etapa terminou com sucesso.
            #

            if (
                analysis is not None
                and hasattr(
                    analysis,
                    "warnings",
                )
            ):

                analysis.warnings.clear()

        step_result = StepResult(
            name=self.name,
            status=(
                StepStatus.FAILED
                if step_failed
                else StepStatus.SUCCESS
            ),
            message=step_message,
            elapsed_seconds=result.duration,
            errors=step_errors,
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
                    "Warnings : "
                    f"{len(step_result.analysis.warnings)}"
                )

            if hasattr(
                step_result.analysis,
                "errors",
            ):

                self._log(
                    "Errors   : "
                    f"{len(step_result.analysis.errors)}"
                )

        self._log("=" * 80)

        return step_result

    def __get_warnings_count(
        self,
        analysis,
    ) -> int:
        """
        Retorna a quantidade total de warnings
        encontrada pelo parser.
        """

        if analysis is None:
            return 0

        summary = getattr(
            analysis,
            "summary",
            None,
        )

        if summary is None:
            return 0

        return int(
            getattr(
                summary,
                "total_warnings",
                0,
            )
            or 0
        )

    def __success_step_message(
        self,
        analysis,
    ) -> str:
        """
        Monta uma mensagem curta para uma Step
        bem-sucedida.
        """

        if self.name.lower() == "build":

            warnings_count = (
                self.__get_warnings_count(
                    analysis,
                )
            )

            if warnings_count > 0:

                return (
                    "Etapa concluída com sucesso. "
                    f"{warnings_count} aviso(s) "
                    "de compilação."
                )

        return (
            "Etapa concluída com sucesso."
        )

    @staticmethod
    def __format_build_error(
        error,
    ) -> str:
        """
        Formata um erro de Build sem transportar
        toda a saída do MSBuild.
        """

        code = getattr(
            error,
            "code",
            "",
        ) or ""

        file = getattr(
            error,
            "file",
            "",
        ) or ""

        line = getattr(
            error,
            "line",
            None,
        )

        column = getattr(
            error,
            "column",
            None,
        )

        message = getattr(
            error,
            "message",
            "",
        ) or str(error)

        location = file

        if line is not None:

            location += (
                f"({line}"
            )

            if column is not None:

                location += (
                    f",{column}"
                )

            location += ")"

        prefix = (
            f"{code}: "
            if code
            else ""
        )

        if location:

            return (
                f"{prefix}"
                f"{message} "
                f"[{location}]"
            )

        return (
            f"{prefix}"
            f"{message}"
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
        Retorna os argumentos da Step.
        """

        raise NotImplementedError
