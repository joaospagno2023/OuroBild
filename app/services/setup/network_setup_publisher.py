"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : network_setup_publisher.py
Descrição : Publica Setups na estrutura de rede configurada.
--------------------------------------------------------------------
"""

from datetime import datetime
from pathlib import Path
from shutil import copytree, rmtree
from time import perf_counter

from app.abstractions.setup_network_publisher import (
    SetupNetworkPublisher,
)
from app.models.configuration.app_settings import AppSettings
from app.models.setup.setup_network_publish_result import (
    SetupNetworkPublishResult,
)
from app.utils.pipeline_logger import (
    PipelineLogger,
)


class DefaultSetupNetworkPublisher(
    SetupNetworkPublisher,
):
    """
    Implementação padrão da publicação de Setup na rede.
    """

    def __init__(
        self,
        settings: AppSettings,
    ) -> None:
        self.__settings = settings

    def publish(
        self,
        project_id: str,
        source_path: Path,
        version: str,
        revision: int,
    ) -> SetupNetworkPublishResult:
        """
        Publica o Setup gerado na rede.

        A estrutura publicada é:

            <network_root>
                <major.minor>
                    <major.minor.patch>
                        Client
                        Server

        O network_root já deve apontar para a pasta Setups.

        O diretório local de origem nunca é movido ou removido.
        """

        started_at = perf_counter()

        source_path = Path(source_path)

        network_root = Path(
            self.__settings.setup.network_root_path
        )

        full_version = f"{version}.{revision}"

        PipelineLogger.info(
            "SETUP NETWORK PUBLISH START | "
            f"project_id={project_id!r} | "
            f"source={source_path} | "
            f"version={full_version}"
        )

        backup_path: Path | None = None
        destination_path: Path | None = None
        backup_created = False

        try:
            major_minor, published_version = (
                self.__resolve_network_version(
                    full_version
                )
            )

            destination_path = (
                network_root
                / major_minor
                / published_version
            )

            PipelineLogger.info(
                "SETUP NETWORK DESTINATION | "
                f"destination={destination_path}"
            )

            self.__validate_request(
                source_path=source_path,
                network_root=network_root,
                destination_path=destination_path,
            )

            self.__validate_source(
                source_path=source_path,
            )

            self.__validate_network_root(
                network_root=network_root,
            )

            self.__validate_destination_parent(
                destination_path=destination_path,
            )

            PipelineLogger.info(
                "SETUP NETWORK PRECHECK SUCCESS | "
                f"source={source_path} | "
                f"network_root={network_root} | "
                f"destination={destination_path}"
            )

            destination_exists = destination_path.exists()

            if destination_exists:
                backup_path = self.__create_backup(
                    destination_path=destination_path,
                )

                backup_created = True

                PipelineLogger.info(
                    "SETUP NETWORK BACKUP CREATED | "
                    f"original={destination_path} | "
                    f"backup={backup_path}"
                )
            else:
                PipelineLogger.info(
                    "SETUP NETWORK BACKUP SKIPPED | "
                    "destination does not exist"
                )

            try:
                PipelineLogger.info(
                    "SETUP NETWORK COPY START | "
                    f"source={source_path} | "
                    f"destination={destination_path}"
                )

                self.__copy_setup(
                    source_path=source_path,
                    destination_path=destination_path,
                )

                PipelineLogger.info(
                    "SETUP NETWORK COPY COMPLETED | "
                    f"destination={destination_path}"
                )

                files_copied = self.__validate_destination(
                    destination_path=destination_path,
                )

                PipelineLogger.info(
                    "SETUP NETWORK VALIDATION SUCCESS | "
                    f"destination={destination_path} | "
                    f"files_copied={files_copied}"
                )

            except Exception as exception:
                PipelineLogger.error(
                    "SETUP NETWORK COPY FAILED | "
                    f"destination={destination_path} | "
                    f"error={exception}"
                )

                self.__cleanup_failed_destination(
                    destination_path=destination_path,
                    destination_existed=destination_exists,
                    backup_created=backup_created,
                )

                PipelineLogger.warning(
                    "SETUP NETWORK PARTIAL DESTINATION CLEANED | "
                    f"destination={destination_path} | "
                    f"backup={backup_path}"
                )

                raise

            backup_removed = False

            if backup_path is not None:
                self.__remove_backup(
                    backup_path=backup_path,
                )

                backup_removed = True

                PipelineLogger.info(
                    "SETUP NETWORK BACKUP REMOVED | "
                    f"backup={backup_path}"
                )

            duration = perf_counter() - started_at

            PipelineLogger.info(
                "SETUP NETWORK PUBLISH SUCCESS | "
                f"project_id={project_id!r} | "
                f"destination={destination_path} | "
                f"files_copied={files_copied} | "
                f"duration_seconds={duration:.3f}"
            )

            return SetupNetworkPublishResult(
                success=True,
                message=(
                    "Setup publicado na rede com sucesso."
                ),
                project_id=project_id,
                source_path=source_path,
                destination_path=destination_path,
                backup_path=backup_path,
                backup_created=backup_created,
                backup_removed=backup_removed,
                files_copied=files_copied,
                duration_seconds=duration,
            )

        except Exception as exception:
            duration = perf_counter() - started_at

            PipelineLogger.error(
                "SETUP NETWORK PUBLISH FAILED | "
                f"project_id={project_id!r} | "
                f"source={source_path} | "
                f"destination={destination_path} | "
                f"backup={backup_path} | "
                f"duration_seconds={duration:.3f} | "
                f"error={exception}"
            )

            return SetupNetworkPublishResult(
                success=False,
                message=(
                    "Falha ao publicar Setup na rede: "
                    f"{exception}"
                ),
                project_id=project_id,
                source_path=source_path,
                destination_path=destination_path,
                backup_path=backup_path,
                backup_created=backup_created,
                backup_removed=False,
                files_copied=0,
                duration_seconds=duration,
            )

    @staticmethod
    def __resolve_network_version(
        full_version: str,
    ) -> tuple[str, str]:
        """
        Converte A.B.C.D em:

            major_minor = A.B
            published_version = A.B.C
        """

        parts = full_version.split(".")

        if len(parts) < 3:
            raise ValueError(
                "A versão deve possuir pelo menos "
                "três componentes."
            )

        major_minor = ".".join(parts[:2])
        published_version = ".".join(parts[:3])

        return (
            major_minor,
            published_version,
        )

    @staticmethod
    def __validate_request(
        source_path: Path,
        network_root: Path,
        destination_path: Path,
    ) -> None:
        """
        Valida os caminhos básicos da publicação.
        """

        if not source_path.exists():
            raise FileNotFoundError(
                "Diretório de origem não encontrado: "
                f"{source_path}"
            )

        if not source_path.is_dir():
            raise NotADirectoryError(
                "A origem do Setup não é um diretório: "
                f"{source_path}"
            )

        if not network_root.exists():
            raise FileNotFoundError(
                "Diretório raiz da rede não encontrado: "
                f"{network_root}"
            )

        if not network_root.is_dir():
            raise NotADirectoryError(
                "A raiz da rede não é um diretório: "
                f"{network_root}"
            )

        if destination_path == network_root:
            raise ValueError(
                "O destino do Setup não pode ser "
                "a raiz da rede."
            )

    @staticmethod
    def __validate_source(
        source_path: Path,
    ) -> None:
        """
        Valida a estrutura mínima do Setup local.

        O cliente pode estar como Client ou Cliente,
        pois o resolver local atual utiliza Cliente.
        """

        client_path = source_path / "Client"
        cliente_path = source_path / "Cliente"
        server_path = source_path / "Server"

        PipelineLogger.info(
            "SETUP NETWORK SOURCE STRUCTURE | "
            f"source={source_path} | "
            f"client_exists={client_path.exists()} | "
            f"client_is_dir={client_path.is_dir()} | "
            f"cliente_exists={cliente_path.exists()} | "
            f"cliente_is_dir={cliente_path.is_dir()} | "
            f"server_exists={server_path.exists()} | "
            f"server_is_dir={server_path.is_dir()}"
        )

        if not client_path.is_dir() and not cliente_path.is_dir():
            raise FileNotFoundError(
                "Diretório Client/Cliente não encontrado "
                f"na origem: {source_path}"
            )

        if not server_path.is_dir():
            raise FileNotFoundError(
                "Diretório Server não encontrado "
                f"na origem: {source_path}"
            )

    @staticmethod
    def __validate_network_root(
        network_root: Path,
    ) -> None:
        """
        Verifica se a raiz da rede permite escrita.
        """

        test_file = (
            network_root
            / ".ourobuild_write_test"
        )

        try:
            test_file.write_text(
                "OuroBuild",
                encoding="utf-8",
            )

            test_file.unlink()

        except Exception as exception:
            if test_file.exists():
                test_file.unlink()

            raise PermissionError(
                "Não foi possível validar a permissão "
                "de escrita na raiz da rede: "
                f"{network_root}"
            ) from exception

    @staticmethod
    def __validate_destination_parent(
        destination_path: Path,
    ) -> None:
        """
        Valida a possibilidade de criar o diretório pai.

        Não cria diretórios nesta etapa.
        """

        parent = destination_path.parent

        while not parent.exists():
            previous = parent.parent

            if previous == parent:
                raise FileNotFoundError(
                    "Não foi possível encontrar um "
                    "diretório existente para validação."
                )

            parent = previous

        if not parent.is_dir():
            raise NotADirectoryError(
                "O diretório pai do destino não é válido: "
                f"{parent}"
            )

        test_file = (
            parent
            / ".ourobuild_write_test"
        )

        try:
            test_file.write_text(
                "OuroBuild",
                encoding="utf-8",
            )

            test_file.unlink()

        except Exception as exception:
            if test_file.exists():
                test_file.unlink()

            raise PermissionError(
                "Não foi possível escrever no diretório "
                f"da rede: {parent}"
            ) from exception

    @staticmethod
    def __create_backup(
        destination_path: Path,
    ) -> Path:
        """
        Renomeia o destino existente para um backup.
        """

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        backup_path = destination_path.with_name(
            f"{destination_path.name}.backup.{timestamp}"
        )

        counter = 1

        while backup_path.exists():
            backup_path = destination_path.with_name(
                f"{destination_path.name}.backup."
                f"{timestamp}_{counter}"
            )

            counter += 1

        destination_path.rename(
            backup_path
        )

        return backup_path

    @staticmethod
    def __copy_setup(
        source_path: Path,
        destination_path: Path,
    ) -> None:
        """
        Copia Client/Cliente e Server para o destino.
        """

        destination_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination_path.mkdir(
            parents=False,
            exist_ok=False,
        )

        client_source = source_path / "Client"

        if not client_source.is_dir():
            client_source = source_path / "Cliente"

        client_destination = (
            destination_path / "Client"
        )

        server_source = source_path / "Server"

        server_destination = (
            destination_path / "Server"
        )

        copytree(
            client_source,
            client_destination,
        )

        copytree(
            server_source,
            server_destination,
        )

    @staticmethod
    def __validate_destination(
        destination_path: Path,
    ) -> int:
        """
        Valida a estrutura copiada e retorna a
        quantidade de arquivos.
        """

        client_path = (
            destination_path / "Client"
        )

        server_path = (
            destination_path / "Server"
        )

        if not client_path.is_dir():
            raise FileNotFoundError(
                "Diretório Client não encontrado "
                "no destino."
            )

        if not server_path.is_dir():
            raise FileNotFoundError(
                "Diretório Server não encontrado "
                "no destino."
            )

        files = list(
            client_path.rglob("*")
        ) + list(
            server_path.rglob("*")
        )

        file_count = 0

        for file_path in files:
            if not file_path.is_file():
                continue

            file_count += 1

        return file_count

    @staticmethod
    def __cleanup_failed_destination(
        destination_path: Path,
        destination_existed: bool,
        backup_created: bool,
    ) -> None:
        """
        Remove uma cópia parcial criada durante uma
        publicação que falhou.

        Um destino original somente pode ser removido
        neste ponto quando ele já foi transformado em
        backup.
        """

        if not destination_path.exists():
            return

        if destination_existed and not backup_created:
            return

        if not destination_path.is_dir():
            destination_path.unlink()
            return

        rmtree(
            destination_path
        )

    @staticmethod
    def __remove_backup(
        backup_path: Path,
    ) -> None:
        """
        Remove o backup após uma publicação validada.
        """

        if not backup_path.exists():
            return

        if backup_path.is_dir():
            rmtree(
                backup_path
            )

            return

        backup_path.unlink()
