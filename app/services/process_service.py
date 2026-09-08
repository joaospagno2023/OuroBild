"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : process_service.py
Descrição : Implementação responsável pela execução de processos.
--------------------------------------------------------------------
"""

from datetime import datetime
import subprocess

from app.abstractions.process_service import (
    ProcessService,
)

from app.models.process.command import (
    Command,
)

from app.models.process.process_result import (
    ProcessResult,
)

from app.models.process.process_status import (
    ProcessStatus,
)

from app.services.logging.pipeline_logger import (
    PipelineLogger,
)


class DefaultProcessService(
    ProcessService,
):
    """
    Executa comandos utilizando o subprocess.
    """

    def execute(
        self,
        command: Command,
    ) -> ProcessResult:
        """
        Executa um processo externo e registra sua execução no log.
        """

        if command is None:
            raise ValueError(
                "O comando não foi informado."
            )

        started_at = datetime.now()

        executable = str(
            command.executable,
        )

        working_directory = str(
            command.working_directory,
        )

        command_line = " ".join(
            [
                executable,
                *[
                    argument.value
                    for argument
                    in command.arguments
                ],
            ],
        )

        PipelineLogger.info(
            "PROCESS EXECUTION - INICIO"
        )

        PipelineLogger.info(
            f"Executable.....: {executable}"
        )

        PipelineLogger.info(
            f"Working Dir....: {working_directory}"
        )

        PipelineLogger.info(
            f"Command........: {command_line}"
        )

        try:

            result = subprocess.run(
                args=[
                    executable,
                    *[
                        argument.value
                        for argument
                        in command.arguments
                    ],
                ],
                cwd=working_directory,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            status = (
                ProcessStatus.SUCCESS
                if result.returncode == 0
                else ProcessStatus.FAILED
            )

            stdout = result.stdout

            stderr = result.stderr

            exit_code = result.returncode

            PipelineLogger.info(
                f"Exit Code......: {exit_code}"
            )

            if stdout:
                PipelineLogger.debug(
                    f"STDOUT........: {stdout.rstrip()}"
                )

            if stderr:
                PipelineLogger.warning(
                    f"STDERR........: {stderr.rstrip()}"
                )

            PipelineLogger.info(
                f"Process Status.: {status}"
            )

        except Exception as ex:

            status = ProcessStatus.FAILED

            stdout = ""

            stderr = str(ex)

            exit_code = -1

            PipelineLogger.error(
                f"PROCESS EXECUTION - ERRO: {ex}"
            )

        finished_at = datetime.now()

        duration = (
            finished_at - started_at
        ).total_seconds()

        PipelineLogger.info(
            f"Duration.......: {duration:.3f}s"
        )

        PipelineLogger.info(
            "PROCESS EXECUTION - FINAL"
        )

        return ProcessResult(
            status=status,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            duration=duration,
            started_at=started_at,
            finished_at=finished_at,
            executable=executable,
            working_directory=working_directory,
            command_line=command_line,
        )
