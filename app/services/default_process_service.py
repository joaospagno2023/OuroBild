"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : default_process_service.py
Descrição : Implementação responsável pela execução de processos.
--------------------------------------------------------------------
"""

import os
import subprocess

from datetime import datetime
from pathlib import Path

from app.abstractions.process_service import ProcessService

from app.models.process.command import Command

from app.models.process.process_result import ProcessResult

from app.models.process.process_status import ProcessStatus


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

        #
        # Inicialização dos valores de retorno.
        #

        status = ProcessStatus.FAILED
        stdout = ""
        stderr = ""
        exit_code = -1

        #
        # Monta exatamente a lista de argumentos que será
        # enviada ao subprocess.run().
        #
        # É importante montar uma única vez para que o
        # diagnóstico represente exatamente a execução real.
        #

        args = [
            str(command.executable),
            *[
                str(argument.value)
                for argument in command.arguments
            ],
        ]

        #
        # Monta uma representação amigável do comando.
        #
        # Essa representação serve para copiar o comando
        # para o PowerShell.
        #

        command_line = (
            self.__build_command_line(
                args,
            )
        )

        try:

            #
            # ========================================================
            # DIAGNÓSTICO DO PROCESSO
            # ========================================================
            #

            print()
            print(
                "=" * 70
            )

            print(
                "[OuroBuild] PROCESS EXECUTION"
            )

            print(
                "=" * 70
            )

            #
            # Executável
            #

            print(
                "[OuroBuild] Executable:"
            )

            print(
                f"[OuroBuild] {command.executable}"
            )

            #
            # Working Directory
            #

            print(
                "[OuroBuild] Working Directory:"
            )

            print(
                f"[OuroBuild] {command.working_directory}"
            )

            #
            # Verifica se o executável realmente existe.
            #

            executable_path = Path(
                command.executable,
            )

            print(
                "[OuroBuild] Executable Exists:"
            )

            print(
                f"[OuroBuild] "
                f"{executable_path.exists()}"
            )

            #
            # Verifica se o Working Directory existe.
            #

            working_directory = Path(
                command.working_directory,
            )

            print(
                "[OuroBuild] Working Directory Exists:"
            )

            print(
                f"[OuroBuild] "
                f"{working_directory.exists()}"
            )

            #
            # ========================================================
            # ARGUMENTOS REAIS
            # ========================================================
            #

            print()
            print(
                "[OuroBuild] Arguments:"
            )

            for index, argument in enumerate(
                args
            ):

                print(
                    f"[OuroBuild] "
                    f"  [{index}] "
                    f"{argument!r}"
                )

            #
            # ========================================================
            # COMANDO COMPLETO
            # ========================================================
            #

            print()
            print(
                "[OuroBuild] Command Line:"
            )

            print(
                f"[OuroBuild] {command_line}"
            )

            #
            # ========================================================
            # AMBIENTE
            # ========================================================
            #

            print()
            print(
                "[OuroBuild] Process Environment:"
            )

            print(
                "[OuroBuild] USERNAME:",
                os.environ.get(
                    "USERNAME",
                ),
            )

            print(
                "[OuroBuild] USERDOMAIN:",
                os.environ.get(
                    "USERDOMAIN",
                ),
            )

            print(
                "[OuroBuild] COMPUTERNAME:",
                os.environ.get(
                    "COMPUTERNAME",
                ),
            )

            print(
                "[OuroBuild] TEMP:",
                os.environ.get(
                    "TEMP",
                ),
            )

            print(
                "[OuroBuild] TMP:",
                os.environ.get(
                    "TMP",
                ),
            )

            print(
                "[OuroBuild] PATH:"
            )

            print(
                os.environ.get(
                    "PATH",
                    "",
                ),
            )

            print(
                "=" * 70
            )

            #
            # ========================================================
            # EXECUÇÃO
            # ========================================================
            #

            print()
            print(
                "[OuroBuild] Starting subprocess..."
            )

            result = subprocess.run(
                args=args,
                cwd=str(
                    command.working_directory,
                ),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            #
            # Resultado
            #

            status = (
                ProcessStatus.SUCCESS
                if result.returncode == 0
                else ProcessStatus.FAILED
            )

            stdout = (
                result.stdout
                or ""
            )

            stderr = (
                result.stderr
                or ""
            )

            exit_code = (
                result.returncode
            )

            #
            # ========================================================
            # RESULTADO
            # ========================================================
            #

            print()
            print(
                "=" * 70
            )

            print(
                "[OuroBuild] PROCESS RESULT"
            )

            print(
                "=" * 70
            )

            print(
                "[OuroBuild] Status:"
            )

            print(
                f"[OuroBuild] {status}"
            )

            print(
                "[OuroBuild] ExitCode:"
            )

            print(
                f"[OuroBuild] {exit_code}"
            )

            print()
            print(
                "[OuroBuild] STDOUT:"
            )

            print(
                stdout
                if stdout
                else "<vazio>"
            )

            print()
            print(
                "[OuroBuild] STDERR:"
            )

            print(
                stderr
                if stderr
                else "<vazio>"
            )

            print(
                "=" * 70
            )

        except Exception as ex:

            #
            # ========================================================
            # EXCEÇÃO
            # ========================================================
            #

            status = (
                ProcessStatus.FAILED
            )

            stdout = ""

            stderr = str(
                ex,
            )

            exit_code = -1

            print()
            print(
                "=" * 70
            )

            print(
                "[OuroBuild] PROCESS EXCEPTION"
            )

            print(
                "=" * 70
            )

            print(
                "[OuroBuild] Exception:"
            )

            print(
                f"[OuroBuild] {type(ex).__name__}"
            )

            print(
                "[OuroBuild] Message:"
            )

            print(
                f"[OuroBuild] {ex}"
            )

            print(
                "=" * 70
            )

        #
        # Finalização
        #

        finished_at = datetime.now()

        duration = (
            finished_at
            - started_at
        ).total_seconds()

        #
        # Resultado final.
        #

        return ProcessResult(
            status=status,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            duration=duration,
            started_at=started_at,
            finished_at=finished_at,
            executable=str(
                command.executable,
            ),
            working_directory=str(
                command.working_directory,
            ),
            command_line=command_line,
        )

    @staticmethod
    def __build_command_line(
        args: list[str],
    ) -> str:
        """
        Cria uma representação do comando para diagnóstico.

        Os argumentos que possuem espaços são colocados
        entre aspas, permitindo copiar o comando para
        o PowerShell.

        A lista original de argumentos NÃO é alterada.
        """

        formatted_arguments = []

        for index, argument in enumerate(
            args
        ):

            #
            # O primeiro argumento é o executável.
            #

            if index == 0:

                value = argument

                if (
                    " " in value
                    or "\t" in value
                ):

                    value = (
                        '"'
                        + value
                        + '"'
                    )

                formatted_arguments.append(
                    value,
                )

                continue

            #
            # Demais argumentos.
            #

            value = argument

            if (
                " " in value
                or "\t" in value
            ):

                value = (
                    '"'
                    + value.replace(
                        '"',
                        '\\"',
                    )
                    + '"'
                )

            formatted_arguments.append(
                value,
            )

        return " ".join(
            formatted_arguments,
        )