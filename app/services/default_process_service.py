"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : default_process_service.py
Descrição : Implementação responsável pela execução de processos.
--------------------------------------------------------------------
"""

from datetime import datetime
import subprocess

from app.abstractions.process_service import ProcessService
from app.models.process.command import Command
from app.models.process.process_result import ProcessResult
from app.models.process.process_status import ProcessStatus
from pathlib import Path

class DefaultProcessService(ProcessService):
    """
    Executa comandos utilizando o subprocess.
    """

    def execute(
        self,
        command: Command,
    ) -> ProcessResult:
        """
        Executa um processo externo.
        """

        started_at = datetime.now()

        try:

            #
            # Diagnóstico da execução.
            #

            print()
            print("=" * 80)
            print("OUROBUILD - EXECUÇÃO DO PROCESSO")
            print("=" * 80)
            print(f"Executável : {command.executable}")
            print(f"Diretório  : {command.working_directory}")
            print("Argumentos :")

            for argument in command.arguments:
                print(f"   {argument.value}")

            print("=" * 80)
            print()
           
            result = subprocess.run(
                args=[
                    str(command.executable),
                    *[
                        argument.value
                        for argument in command.arguments
                    ],
                ],
                cwd=str(command.working_directory),
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

        except Exception as ex:

            status = ProcessStatus.FAILED
            stdout = ""
            stderr = str(ex)
            exit_code = -1

        finished_at = datetime.now()

        duration = (
            finished_at - started_at
        ).total_seconds()

        return ProcessResult(
            status=status,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            duration=duration,
        )