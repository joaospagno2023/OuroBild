"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : advanced_installer_service.py
Descrição : Gera o Setup utilizando o Advanced Installer.
--------------------------------------------------------------------
"""

from pathlib import Path
import shutil
import os
import stat
import subprocess
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

from app.services.cleanup.build_artifact_cleanup_service import (
    BuildArtifactCleanupService,
)

from app.services.setup.advanced_installer_aip_synchronizer import (
    AdvancedInstallerAipSynchronizer,
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
        cleanup_service: BuildArtifactCleanupService,
        aip_synchronizer: AdvancedInstallerAipSynchronizer,
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

        if cleanup_service is None:

            raise ValueError(
                "BuildArtifactCleanupService "
                "não foi informado."
            )

        if aip_synchronizer is None:

            raise ValueError(
                "AdvancedInstallerAipSynchronizer "
                "não foi informado."
            )

        self.__process_service = (
            process_service
        )

        self.__advanced_installer_path = Path(
            advanced_installer_path,
        )

        self.__cleanup_service = (
            cleanup_service
        )

        self.__aip_synchronizer = (
            aip_synchronizer
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

            1. Cleanup dos artefatos da publicação.
            2. Sincronização do AIP com os arquivos reais
               do Release (KEEP/ADD/REMOVE + versão),
               sempre em cima de uma cópia de trabalho.
            3. Atualização do PATHFOLDER para a pasta de saída
               configurada (output_root/version.revision/...).
            4. RefreshSync do AIP de trabalho.
            5. Build do AIP de trabalho.
            6. Validação do MSI gerado.
        """

        self.__validate(
            request=request,
            definition=definition,
            paths=paths,
        )

        publish_path = Path(
            paths.publish_path,
        )

        cleanup_result = (
            self.__cleanup_service.execute(
                workspace_path=publish_path,
                project_id=request.project_id,
            )
        )

        if cleanup_result.errors:

            return SetupResult(
                success=False,
                message=(
                    "Falha durante a limpeza dos "
                    "artefatos da publicação: "
                    + "; ".join(
                        cleanup_result.errors
                    )
                ),
                project_id=request.project_id,
                output_msi=None,
                duration_seconds=0.0,
            )

        #
        # ------------------------------------------------------------
        # Preparar cópia de trabalho do AIP
        #
        # O arquivo original (normalmente em TFS) permanece somente
        # leitura/intocado. A cópia é criada na MESMA PASTA do AIP
        # original, para manter Prerequisites e demais caminhos.
        # ------------------------------------------------------------
        #

        original_aip_path = Path(
            paths.aip_path,
        ).resolve()

        aip_dir = original_aip_path.parent

        # Nome da cópia de trabalho (ex.: OuroNet...build.aip)
        workspace_aip_path = aip_dir / (
            original_aip_path.stem + ".build.aip"
        )

        shutil.copy2(
            original_aip_path,
            workspace_aip_path,
        )

        # Remover atributo somente leitura da cópia (Windows)
        try:
            subprocess.run(
                [
                    "attrib",
                    "-R",
                    str(workspace_aip_path),
                ],
                check=False,
                shell=False,
            )
        except Exception:
            pass

        try:
            os.chmod(
                workspace_aip_path,
                stat.S_IWRITE | stat.S_IREAD,
            )
        except OSError:
            pass

        #
        # ------------------------------------------------------------
        # Atualizar PATHFOLDER para a pasta de saída configurada.
        #
        # Usamos a pasta pai do paths.output_msi, que já é
        # resolvida pelo SetupPathResolver a partir do settings.json
        # (setup.output_root + versão + revisão + Cliente/Server).
        #
        # O PATHFOLDER é gravado como caminho RELATIVO ao AIP.
        # ------------------------------------------------------------
        #

        output_folder = Path(
            paths.output_msi,
        ).parent

        self.__update_pathfolder(
            aip_path=workspace_aip_path,
            output_folder=output_folder,
        )

        # Atualiza MSINAME com o nome configurado no projects.json
        self.__update_msiname(
            aip_path=workspace_aip_path,
            output_msi=Path(paths.output_msi),
        )

        #
        # ------------------------------------------------------------
        # Sincronizar o AIP em cima da cópia de trabalho.
        # ------------------------------------------------------------
        #

        try:

            self.__aip_synchronizer.synchronize(
                aip_path=workspace_aip_path,
                version=definition.version,
                publish_path=publish_path,
            )

        except Exception as exc:

            return SetupResult(
                success=False,
                message=(
                    "Falha durante a sincronização "
                    "do AIP com o Release: "
                    f"{exc}"
                ),
                project_id=request.project_id,
                output_msi=None,
                duration_seconds=0.0,
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

        # Remover a cópia de trabalho; o AIP original permanece intacto.
        try:
            if workspace_aip_path.exists():
                workspace_aip_path.unlink()
        except OSError:
            pass

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

    def __update_pathfolder(
        self,
        aip_path: Path,
        output_folder: Path,
    ) -> None:
        """
        Atualiza a propriedade PATHFOLDER no AIP de trabalho para
        apontar para a pasta de saída configurada.

        O valor gravado é um caminho relativo ao diretório do AIP,
        mantendo a mesma semântica utilizada no AIP original.
        """

        aip_path = Path(aip_path)
        output_folder = Path(output_folder)

        if not aip_path.exists():
            return

        try:
            content = aip_path.read_text(
                encoding="utf-8",
            )
        except OSError:
            return

        # Caminho relativo do output_folder em relação ao diretório do AIP.
        try:
            relative_folder = os.path.relpath(
                output_folder,
                start=aip_path.parent,
            )
        except ValueError:
            # Se não conseguir resolver relativo (drivers diferentes, etc.),
            # cai para o caminho absoluto mesmo.
            relative_folder = str(output_folder)

        # Normalizar para separadores de Windows, como no AIP original.
        relative_folder = (
            str(relative_folder)
            .replace("/", "\\")
            .strip()
        )

        if not relative_folder:
            return

        pattern = re.compile(
            r'(<ROW\b'
            r'(?=[^>]*\bProperty\s*=\s*"PATHFOLDER")'
            r'[^>]*\bValue\s*=\s*")'
            r'([^"]*)'
            r'(")',
            re.IGNORECASE | re.DOTALL,
        )

        def repl(match: re.Match) -> str:
            return (
                match.group(1)
                + relative_folder
                + match.group(3)
            )

        new_content, count = pattern.subn(
            repl,
            content,
            count=1,
        )

        if count == 0:
            # Nenhuma linha PATHFOLDER encontrada; não falha o fluxo.
            return

        try:
            aip_path.write_text(
                new_content,
                encoding="utf-8",
            )
        except OSError:
            # Se não conseguir gravar, não interrompe o fluxo.
            return

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
    
    def __update_msiname(
        self,
        aip_path: Path,
        output_msi: Path,
    ) -> None:
        """
        Atualiza a propriedade MSINAME no AIP de trabalho para
        refletir o nome configurado em output_msi (projects.json).

        O AIP usa [|MSINAME] em PackageFileName, e o Advanced Installer
        adiciona a extensão .msi automaticamente. Então aqui gravamos
        apenas o NOME base, sem .msi.
        """

        aip_path = Path(aip_path)
        output_msi = Path(output_msi)

        # Usa só o nome base; o Advanced Installer adiciona .msi
        if output_msi.suffix.lower() == ".msi":
            msi_name = output_msi.stem
        else:
            msi_name = output_msi.name

        msi_name = msi_name.strip()
        if not msi_name:
            return

        if not aip_path.exists():
            return

        try:
            content = aip_path.read_text(
                encoding="utf-8",
            )
        except OSError:
            return

        pattern = re.compile(
            r'(<ROW\b'
            r'(?=[^>]*\bProperty\s*=\s*"MSINAME")'
            r'[^>]*\bValue\s*=\s*")'
            r'([^"]*)'
            r'(")',
            re.IGNORECASE | re.DOTALL,
        )

        def repl(match: re.Match) -> str:
            return (
                match.group(1)
                + msi_name
                + match.group(3)
            )

        new_content, count = pattern.subn(
            repl,
            content,
            count=1,
        )

        if count == 0:
            # Nenhuma MSINAME encontrada; não quebra a geração.
            return

        try:
            aip_path.write_text(
                new_content,
                encoding="utf-8",
            )
        except OSError:
            # Se não conseguir gravar, apenas segue com o valor antigo.
            return

