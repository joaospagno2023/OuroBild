"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : advanced_installer_service.py
Descrição : Gera o Setup utilizando o Advanced Installer.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.abstractions.installer_service import (
    InstallerService,
)

from app.abstractions.process_service import (
    ProcessService,
)

from app.models.process.command import (
    Command,
)

from app.models.process.command_argument import (
    CommandArgument,
)

from app.models.process.process_status import (
    ProcessStatus,
)

from app.models.setup.setup_definition import (
    SetupDefinition,
)

from app.models.setup.setup_paths import (
    SetupPaths,
)

from app.models.setup.setup_request import (
    SetupRequest,
)

from app.models.setup.setup_result import (
    SetupResult,
)


class AdvancedInstallerService(
    InstallerService,
):
    """
    Gera um instalador utilizando o Advanced Installer.
    """

    def __init__(
        self,
        process_service: ProcessService,
        advanced_installer_path: Path,
    ) -> None:
        """
        Inicializa o serviço.
        """

        if process_service is None:
            raise ValueError(
                "ProcessService "
                "não foi informado."
            )

        if advanced_installer_path is None:
            raise ValueError(
                "Caminho do Advanced Installer "
                "não foi informado."
            )

        self.__process_service = (
            process_service
        )

        self.__advanced_installer_path = Path(
            advanced_installer_path,
        )

    def install(
        self,
        request: SetupRequest,
        definition: SetupDefinition,
        paths: SetupPaths,
    ) -> SetupResult:
        """
        Gera o Setup utilizando o Advanced Installer.

        O fluxo executado é:

            1. RefreshSync do AIP.
            2. Build do AIP.
            3. Validação do MSI gerado.
        """

        self.__validate(
            request=request,
            definition=definition,
            paths=paths,
        )

        aip_path = Path(
            paths.aip_path,
        )

        refresh_sync_result = (
            self.__execute_refresh_sync(
                aip_path=aip_path,
            )
        )

        if (
            refresh_sync_result.status
            != ProcessStatus.SUCCESS
        ):
            return self.__create_process_failure_result(
                request=request,
                process_result=refresh_sync_result,
                operation="RefreshSync",
            )

        build_result = (
            self.__execute_build(
                aip_path=aip_path,
            )
        )

        if (
            build_result.status
            != ProcessStatus.SUCCESS
        ):
            return self.__create_process_failure_result(
                request=request,
                process_result=build_result,
                operation="Build",
                previous_duration=(
                    refresh_sync_result.duration
                ),
            )

        output_msi = Path(
            paths.output_msi,
        )

        total_duration = (
            refresh_sync_result.duration
            + build_result.duration
        )

        if not output_msi.exists():
            return SetupResult(
                success=False,
                message=(
                    "O Advanced Installer finalizou "
                    "a geração do Setup, porém o "
                    "arquivo MSI não foi encontrado: "
                    f"{output_msi}"
                ),
                project_id=request.project_id,
                output_msi=None,
                duration_seconds=(
                    total_duration
                ),
            )

        return SetupResult(
            success=True,
            message=(
                "Setup gerado com sucesso."
            ),
            project_id=request.project_id,
            output_msi=output_msi,
            duration_seconds=(
                total_duration
            ),
        )

    def __execute_refresh_sync(
        self,
        aip_path: Path,
    ):
        """
        Executa o RefreshSync do Advanced Installer.

        Comando:

            AdvancedInstaller.com
                /edit
                <AIP>
                /RefreshSync
        """

        command = (
            self.__create_refresh_sync_command(
                aip_path=aip_path,
            )
        )

        return self.__process_service.execute(
            command,
        )

    def __execute_build(
        self,
        aip_path: Path,
    ):
        """
        Executa o Build do Advanced Installer.

        Comando:

            AdvancedInstaller.com
                /build
                <AIP>
        """

        command = (
            self.__create_build_command(
                aip_path=aip_path,
            )
        )

        return self.__process_service.execute(
            command,
        )

    def __validate(
        self,
        request: SetupRequest,
        definition: SetupDefinition,
        paths: SetupPaths,
    ) -> None:
        """
        Valida os dados necessários para geração.
        """

        if request is None:
            raise ValueError(
                "A solicitação de Setup "
                "não foi informada."
            )

        if definition is None:
            raise ValueError(
                "A definição do Setup "
                "não foi informada."
            )

        if paths is None:
            raise ValueError(
                "Os caminhos do Setup "
                "não foram informados."
            )

        if not self.__advanced_installer_path.exists():
            raise FileNotFoundError(
                "AdvancedInstaller.com "
                "não encontrado: "
                f"{self.__advanced_installer_path}"
            )

        if not self.__advanced_installer_path.is_file():
            raise ValueError(
                "O caminho do Advanced Installer "
                "não é um arquivo: "
                f"{self.__advanced_installer_path}"
            )

        aip_path = Path(
            paths.aip_path,
        )

        if not aip_path.exists():
            raise FileNotFoundError(
                "Arquivo AIP "
                "não encontrado: "
                f"{aip_path}"
            )

        if not aip_path.is_file():
            raise ValueError(
                "O caminho do AIP "
                "não é um arquivo: "
                f"{aip_path}"
            )

    def __create_refresh_sync_command(
        self,
        aip_path: Path,
    ) -> Command:
        """
        Cria o comando de RefreshSync.

        O Advanced Installer utiliza:

            /edit <AIP> /RefreshSync
        """

        arguments = [
            CommandArgument(
                value="/edit",
            ),
            CommandArgument(
                value=str(
                    aip_path,
                ),
            ),
            CommandArgument(
                value="/RefreshSync",
            ),
        ]

        return Command(
            executable=(
                self.__advanced_installer_path
            ),
            working_directory=(
                aip_path.parent
            ),
            arguments=arguments,
        )

    def __create_build_command(
        self,
        aip_path: Path,
    ) -> Command:
        """
        Cria o comando de Build.

        O Advanced Installer utiliza:

            /build <AIP>
        """

        arguments = [
            CommandArgument(
                value="/build",
            ),
            CommandArgument(
                value=str(
                    aip_path,
                ),
            ),
        ]

        return Command(
            executable=(
                self.__advanced_installer_path
            ),
            working_directory=(
                aip_path.parent
            ),
            arguments=arguments,
        )

    def __create_process_failure_result(
        self,
        request: SetupRequest,
        process_result,
        operation: str,
        previous_duration: float = 0.0,
    ) -> SetupResult:
        """
        Cria um SetupResult de falha para uma
        operação do Advanced Installer.
        """

        return SetupResult(
            success=False,
            message=(
                "Falha durante a operação "
                f"{operation} do Advanced Installer. "
                f"ExitCode: "
                f"{process_result.exit_code}. "
                f"{process_result.stderr}"
            ).strip(),
            project_id=request.project_id,
            output_msi=None,
            duration_seconds=(
                previous_duration
                + process_result.duration
            ),
        )