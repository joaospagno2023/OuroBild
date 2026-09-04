"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : advanced_installer_service.py
Descrição : Gera o Setup utilizando o Advanced Installer.
--------------------------------------------------------------------
"""

from pathlib import Path
import re

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

from app.services.cleanup.build_artifact_cleanup_factory import (
    BuildArtifactCleanupFactory,
)

from app.services.setup.advanced_installer_aip_synchronizer import (
    AdvancedInstallerAipSynchronizer,
)

from app.services.setup.advanced_installer_workspace_service import (
    AdvancedInstallerWorkspaceService,
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
        cleanup_factory: BuildArtifactCleanupFactory,
        workspace_service: AdvancedInstallerWorkspaceService,
        aip_synchronizer: AdvancedInstallerAipSynchronizer | None = None,
        excluirpastawork: bool = False,
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

        if cleanup_factory is None:
            raise ValueError(
                "BuildArtifactCleanupFactory "
                "não foi informado."
            )

        if workspace_service is None:
            raise ValueError(
                "AdvancedInstallerWorkspaceService "
                "não foi informado."
            )

        if not isinstance(
            excluirpastawork,
            bool,
        ):
            raise ValueError(
                "ExcluirPastawork deve ser booleano."
            )

        self.__process_service = (
            process_service
        )

        self.__advanced_installer_path = Path(
            advanced_installer_path,
        )

        self.__cleanup_factory = (
            cleanup_factory
        )

        # Mantido por compatibilidade com o Bootstrap atual.
        # O sincronizador não é mais utilizado neste fluxo; a atualização
        # dos arquivos é feita pelo RefreshSync nativo do Advanced Installer.
        self.__aip_synchronizer = aip_synchronizer

        self.__workspace_service = (
            workspace_service
        )

        self.__excluirpastawork = (
            excluirpastawork
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

            1. Criação do workspace temporário.
            2. Cópia do AIP, Prerequisites e Release.
            3. Cleanup dos artefatos dentro do workspace.
            4. Atualização da pasta de origem da sincronização.
            5. Atualização do nome e da pasta de saída do MSI.
            6. Atualização da versão do produto.
            7. RefreshSync nativo do Advanced Installer.
            8. Build do AIP de trabalho.
            9. Validação do MSI gerado.
            10. Remoção do workspace quando
                excluirpastawork estiver habilitado.
        """

        self.__validate(
            request=request,
            definition=definition,
            paths=paths,
        )

        original_aip_path = Path(
            paths.aip_path,
        ).resolve()

        prerequisites_path = (
            original_aip_path.parent
            / "Prerequisites"
        )

        workspace = self.__workspace_service.prepare(
            project_id=request.project_id,
            aip_path=original_aip_path,
            prerequisites_path=prerequisites_path,
            publish_path=Path(paths.publish_path),
        )

        workspace_path = workspace.workspace_path
        workspace_aip_path = workspace.aip_path
        workspace_publish_path = workspace.publish_path

        try:
            #
            # ============================================================
            # Cleanup
            # ============================================================
            #

            cleanup_service = (
                self.__cleanup_factory.create(
                    project_id=request.project_id,
                )
            )

            cleanup_result = (
                cleanup_service.execute(
                    workspace_path=workspace_publish_path,
                    project_id=request.project_id,
                )
            )

            if cleanup_result.errors:
                return SetupResult(
                    success=False,
                    message=(
                        "Falha durante a limpeza "
                        "dos artefatos da publicação: "
                        + "; ".join(
                            cleanup_result.errors
                        )
                    ),
                    project_id=request.project_id,
                    output_msi=None,
                    duration_seconds=0.0,
                )

            try:
                self.__update_synchronized_folder_source(
                    aip_path=workspace_aip_path,
                    publish_path=workspace_publish_path,
                )

            except Exception as exc:
                return SetupResult(
                    success=False,
                    message=(
                        "Falha durante a configuração da "
                        "pasta sincronizada do AIP: "
                        f"{exc}"
                    ),
                    project_id=request.project_id,
                    output_msi=None,
                    duration_seconds=0.0,
                )

            package_name = (
                Path(paths.output_msi)
            )

            set_package_name_result = (
                self.__execute_set_package_name(
                    aip_path=workspace_aip_path,
                    output_msi=package_name,
                )
            )

            if (
                set_package_name_result.status
                != ProcessStatus.SUCCESS
            ):
                return self.__create_process_failure_result(
                    request=request,
                    process_result=set_package_name_result,
                    operation="SetPackageName",
                )

            set_version_result = (
                self.__execute_set_version(
                    aip_path=workspace_aip_path,
                    version=definition.version,
                )
            )

            if (
                set_version_result.status
                != ProcessStatus.SUCCESS
            ):
                return self.__create_process_failure_result(
                    request=request,
                    process_result=set_version_result,
                    operation="SetVersion",
                    previous_duration=(
                        set_package_name_result.duration
                    ),
                )

            refresh_sync_result = (
                self.__execute_refresh_sync(
                    aip_path=workspace_aip_path,
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
                    aip_path=workspace_aip_path,
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
                set_package_name_result.duration
                + set_version_result.duration
                + refresh_sync_result.duration
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

        finally:
            if self.__excluirpastawork:
                self.__workspace_service.cleanup(
                    workspace_path=workspace_path,
                )

    def __update_synchronized_folder_source(
        self,
        aip_path: Path,
        publish_path: Path,
    ) -> None:
        """
        Atualiza somente o SourcePath da pasta sincronizada do AIP.

        O Advanced Installer continua responsável por criar, remover
        e atualizar todos os arquivos e componentes durante o
        RefreshSync. O OuroBuild apenas aponta a sincronização para
        a pasta Release do workspace atual.
        """

        aip_path = Path(aip_path)
        publish_path = Path(publish_path).resolve()

        if not aip_path.exists():
            raise FileNotFoundError(
                "Arquivo AIP não encontrado: "
                f"{aip_path}"
            )

        if not publish_path.exists():
            raise FileNotFoundError(
                "Pasta de publicação não encontrada: "
                f"{publish_path}"
            )

        if not publish_path.is_dir():
            raise ValueError(
                "A pasta de publicação não é um diretório: "
                f"{publish_path}"
            )

        content = aip_path.read_text(
            encoding="utf-8",
        )

        synchronized_component = (
            "caphyon.advinst.msicomp.SynchronizedFolderComponent"
        )

        component_pattern = re.compile(
            r'(?P<header>'
            r'<COMPONENT\b'
            r'(?=[^>]*\bcid\s*=\s*"'
            + re.escape(synchronized_component)
            + r'"'
            r')[^>]*>'
            r')'
            r'(?P<body>.*?)'
            r'(?P<footer></COMPONENT>)',
            re.IGNORECASE | re.DOTALL,
        )

        match = component_pattern.search(
            content,
        )

        if match is None:
            raise ValueError(
                "SynchronizedFolderComponent não encontrado no AIP."
            )

        body = match.group("body")

        source_pattern = re.compile(
            r'(?P<prefix>\bSourcePath\s*=\s*")'
            r'(?P<value>[^"]*)'
            r'(?P<suffix>")',
            re.IGNORECASE,
        )

        source_match = source_pattern.search(
            body,
        )

        if source_match is None:
            raise ValueError(
                "A pasta sincronizada do AIP não possui SourcePath."
            )

        source_path_text = (
            str(publish_path)
            .replace("\\", "\\\\")
        )

        updated_body = source_pattern.sub(
            lambda current_match: (
                current_match.group("prefix")
                + source_path_text
                + current_match.group("suffix")
            ),
            body,
            count=1,
        )

        updated_content = (
            content[:match.start("body")]
            + updated_body
            + content[match.end("body"):]
        )

        aip_path.write_text(
            updated_content,
            encoding="utf-8",
        )

    def __execute_set_package_name(
        self,
        aip_path: Path,
        output_msi: Path,
    ):
        """
        Define o nome e a pasta de saída do MSI no build padrão.

        O caminho completo informado ao /SetPackageName faz com que
        o Advanced Installer atualize o nome do pacote e o diretório
        pai de saída.
        """

        output_msi = Path(output_msi).resolve()

        output_msi.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        command = Command(
            executable=self.__advanced_installer_path,
            working_directory=aip_path.parent,
            arguments=[
                CommandArgument(
                    value="/edit",
                ),
                CommandArgument(
                    value=str(aip_path),
                ),
                CommandArgument(
                    value="/SetPackageName",
                ),
                CommandArgument(
                    value=str(output_msi),
                ),
                CommandArgument(
                    value="-buildname",
                ),
                CommandArgument(
                    value="DefaultBuild",
                ),
            ],
        )

        return self.__process_service.execute(
            command,
        )

    def __execute_set_version(
        self,
        aip_path: Path,
        version: str,
    ):
        """
        Atualiza a Product Version do AIP usando o comando nativo.
        """

        normalized_version = str(
            version,
        ).strip()

        if not normalized_version:
            raise ValueError(
                "A versão do Setup não foi informada."
            )

        command = Command(
            executable=self.__advanced_installer_path,
            working_directory=aip_path.parent,
            arguments=[
                CommandArgument(
                    value="/edit",
                ),
                CommandArgument(
                    value=str(aip_path),
                ),
                CommandArgument(
                    value="/SetVersion",
                ),
                CommandArgument(
                    value=normalized_version,
                ),
            ],
        )

        return self.__process_service.execute(
            command,
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

        if paths.publish_path is None:
            raise ValueError(
                "O caminho de publicação "
                "não foi informado."
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

