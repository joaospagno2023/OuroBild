"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : dotnet_build_executor_service.py
Descrição : Executor de Build utilizando a CLI do .NET.
--------------------------------------------------------------------
"""

from app.models.build.build_context import (
    BuildContext,
)
from app.models.process.process_result import (
    ProcessResult,
)
from app.models.process.process_status import (
    ProcessStatus,
)
from app.services.build.build_executor_service import (
    BuildExecutorService,
)
from app.services.process.process_executor_service import (
    ProcessExecutorService,
)


class DotnetBuildExecutorService(
    BuildExecutorService,
):
    """
    Executor responsável por realizar
    a compilação utilizando a CLI do .NET.
    """

    def __init__(
        self,
        process_executor_service: ProcessExecutorService,
    ) -> None:
        """
        Inicializa o executor.
        """

        self.__process = (
            process_executor_service
        )

    def __execute_step(
        self,
        command: str,
        context: BuildContext,
        additional_arguments: list[str] | None = None,
    ) -> ProcessResult:
        """
        Executa um comando da CLI do .NET.
        """

        arguments = [
            command,
            str(
                context.paths.project_file,
            ),
        ]

        #
        # Configuração
        #

        if (
            context.definition is not None
            and context.definition.configuration
        ):
            arguments.extend(
                [
                    "--configuration",
                    context.definition.configuration,
                ]
            )

        #
        # Argumentos adicionais
        #

        if additional_arguments:

            arguments.extend(
                additional_arguments,
            )

        return self.__process.execute(
            executable="dotnet",
            arguments=arguments,
            working_directory=(
                context.paths.project_file.parent
            ),
        )

    def __restore(
        self,
        context: BuildContext,
    ) -> ProcessResult:
        """
        Executa o Restore.
        """

        return self.__execute_step(
            command="restore",
            context=context,
        )

    def __clean(
        self,
        context: BuildContext,
    ) -> ProcessResult:
        """
        Executa o Clean.
        """

        return self.__execute_step(
            command="clean",
            context=context,
        )

    def __build(
        self,
        context: BuildContext,
    ) -> ProcessResult:
        """
        Executa o Build.
        """

        return self.__execute_step(
            command="build",
            context=context,
            additional_arguments=[
                "--no-restore",
            ],
        )

    def execute(
        self,
        context: BuildContext,
    ) -> ProcessResult:
        """
        Executa o pipeline:

        Restore
            ↓
        Clean
            ↓
        Build

        Caso alguma etapa falhe,
        interrompe imediatamente a execução.
        """

        #
        # Restore
        #

        process = self.__restore(
            context,
        )

        if process.status != ProcessStatus.SUCCESS:
            return process

        #
        # Clean
        #

        process = self.__clean(
            context,
        )

        if process.status != ProcessStatus.SUCCESS:
            return process

        #
        # Build
        #

        return self.__build(
            context,
        )