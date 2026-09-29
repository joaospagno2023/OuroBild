"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : network_setup_publisher.py
Descrição : Publica Setups na estrutura de rede configurada.
--------------------------------------------------------------------
"""

import os
import subprocess
from collections import deque
from datetime import datetime
from pathlib import Path
from shutil import copy2, copytree, rmtree
from typing import Callable
from time import perf_counter

from app.abstractions.setup_network_publisher import (
    SetupNetworkPublisher,
)
from app.models.configuration.app_settings import AppSettings
SetupNetworkPublishProgressCallback = Callable[[int, int, str, int], None]


from app.models.setup.setup_network_publish_result import (
    SetupNetworkPublishResult,
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
        progress_callback: SetupNetworkPublishProgressCallback | None = None,
    ) -> SetupNetworkPublishResult:
        """
        Publica o Setup gerado na rede.

        A estrutura publicada é:

            <network_root>
                <major.minor>
                    Setups
                        <major.minor.patch>
                            Client
                            Server

        O diretório local de origem nunca é movido ou removido.
        """

        started_at = perf_counter()

        source_path = Path(source_path)

        network_root = Path(
            self.__settings.setup.network_root_path
        )

        full_version = f"{version}.{revision}"

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
                / "Setups"
                / published_version
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

            destination_exists = destination_path.exists()

            in_place = False

            if destination_exists:
                try:
                    backup_path = self.__create_backup(
                        destination_path=destination_path,
                    )

                    backup_created = True

                except OSError:
                    #
                    # Renomear pastas em SMB falha com facilidade
                    # (arquivo aberto, falta de permissão de
                    # exclusão). Com o Robocopy disponível,
                    # atualiza o destino no próprio lugar (/MIR),
                    # sem backup.
                    #

                    if self.__resolve_robocopy_path() is None:
                        raise

                    in_place = True

            try:
                files_copied, total_files = self.__copy_setup(
                    source_path=source_path,
                    destination_path=destination_path,
                    progress_callback=progress_callback,
                    in_place=in_place,
                )

                validated_files = self.__validate_destination(
                    destination_path=destination_path,
                )

                if validated_files != files_copied:
                    raise IOError(
                        "A quantidade de arquivos copiados não "
                        "corresponde à quantidade validada no destino."
                    )

            except Exception:
                self.__cleanup_failed_destination(
                    destination_path=destination_path,
                    destination_existed=destination_exists,
                    backup_created=backup_created,
                )

                raise

            backup_removed = False

            if backup_path is not None:
                self.__remove_backup(
                    backup_path=backup_path,
                )

                backup_removed = True

            duration = perf_counter() - started_at

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

    def __copy_setup(
        self,
        source_path: Path,
        destination_path: Path,
        progress_callback: SetupNetworkPublishProgressCallback | None = None,
        in_place: bool = False,
    ) -> tuple[int, int]:
        """
        Copia Client/Cliente e Server para o destino.

        Usa Robocopy (multi-thread) quando disponível, que é
        muito mais rápido que a cópia arquivo a arquivo em
        Python sobre SMB. Se o Robocopy não for encontrado,
        usa a cópia em Python como fallback.
        """

        robocopy_path = self.__resolve_robocopy_path()

        if robocopy_path is None:
            return self.__copy_setup_python(
                source_path=source_path,
                destination_path=destination_path,
                progress_callback=progress_callback,
            )

        destination_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination_path.mkdir(
            parents=False,
            exist_ok=in_place,
        )

        client_source = source_path / "Client"

        if not client_source.is_dir():
            client_source = source_path / "Cliente"

        server_source = source_path / "Server"

        total_files = (
            self.__count_files(client_source)
            + self.__count_files(server_source)
        )

        if progress_callback is not None:
            progress_callback(
                0,
                total_files,
                "Preparando cópia...",
                0,
            )

        files_done = 0

        for source_dir, destination_dir in (
            (client_source, destination_path / "Client"),
            (server_source, destination_path / "Server"),
        ):
            files_done = self.__run_robocopy(
                robocopy_path=robocopy_path,
                source_dir=source_dir,
                destination_dir=destination_dir,
                files_done=files_done,
                total_files=total_files,
                progress_callback=progress_callback,
                mirror=in_place,
            )

        #
        # O Robocopy terminou sem erro (exit code < 8).
        # A integridade é conferida depois por
        # __validate_destination, que compara a contagem
        # real do destino com a origem.
        #

        return total_files, total_files

    def __resolve_robocopy_path(
        self,
    ) -> Path | None:
        """
        Retorna o caminho do Robocopy configurado, ou None
        se não existir (usa o fallback em Python).
        """

        try:
            configured = Path(
                self.__settings.build_tools.robocopy_path
            )
        except Exception:
            return None

        if configured.is_file():
            return configured

        return None

    @staticmethod
    def __run_robocopy(
        robocopy_path: Path,
        source_dir: Path,
        destination_dir: Path,
        files_done: int,
        total_files: int,
        progress_callback: SetupNetworkPublishProgressCallback | None,
        mirror: bool = False,
    ) -> int:
        """
        Executa o Robocopy para um diretório e retorna o
        total acumulado de arquivos copiados.

        Exit codes 0 a 7 indicam sucesso; 8 ou mais, falha.
        """

        threads = os.environ.get(
            "OUROBUILD_ROBOCOPY_THREADS",
            "16",
        )

        command = [
            str(robocopy_path),
            str(source_dir),
            str(destination_dir),
            "/MIR" if mirror else "/E",
            f"/MT:{threads}",
            "/R:2",
            "/W:2",
            "/XJ",
            "/NP",
            "/NDL",
            "/NJH",
            "/NJS",
            "/NC",
            "/NS",
        ]

        is_windows = os.name == "nt"

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="oem" if is_windows else "utf-8",
            errors="replace",
            creationflags=getattr(
                subprocess,
                "CREATE_NO_WINDOW",
                0,
            ),
        )

        tail: deque[str] = deque(maxlen=20)

        assert process.stdout is not None

        for line in process.stdout:
            text = line.strip()

            if not text:
                continue

            tail.append(text)

            if "ERROR" in text.upper():
                continue

            files_done += 1

            if progress_callback is not None:
                percent = (
                    min(
                        99,
                        int(
                            (files_done / total_files) * 100
                        ),
                    )
                    if total_files > 0
                    else 100
                )

                progress_callback(
                    min(files_done, total_files),
                    total_files,
                    Path(text).name,
                    percent,
                )

        return_code = process.wait()

        if return_code >= 8:
            raise IOError(
                f"Robocopy falhou (exit code {return_code}) "
                f"ao copiar '{source_dir}'. Últimas linhas: "
                + " | ".join(tail)
            )

        return files_done

    @staticmethod
    def __count_files(
        directory: Path,
    ) -> int:
        """
        Conta arquivos usando os.walk, que evita um stat
        por arquivo (importante em compartilhamentos de rede).
        """

        return sum(
            len(files)
            for _, _, files in os.walk(directory)
        )

    @staticmethod
    def __copy_setup_python(
        source_path: Path,
        destination_path: Path,
        progress_callback: SetupNetworkPublishProgressCallback | None = None,
    ) -> tuple[int, int]:
        """
        Fallback: copia Client/Cliente e Server em Python,
        arquivo a arquivo.
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

        source_files = [
            source_file
            for source_root in (
                client_source,
                server_source,
            )
            for source_file in source_root.rglob("*")
            if source_file.is_file()
        ]

        total_files = len(source_files)
        files_copied = 0

        if progress_callback is not None:
            progress_callback(
                0,
                total_files,
                "Preparando cópia...",
                0,
            )

        def copy_file(
            source_file: str,
            destination_file: str,
        ) -> str:
            nonlocal files_copied

            copied_path = copy2(
                source_file,
                destination_file,
            )

            files_copied += 1

            if progress_callback is not None:
                progress_callback(
                    files_copied,
                    total_files,
                    Path(source_file).name,
                    int(
                        (files_copied / total_files) * 100
                    )
                    if total_files > 0
                    else 100,
                )

            return copied_path

        copytree(
            client_source,
            client_destination,
            copy_function=copy_file,
        )

        copytree(
            server_source,
            server_destination,
            copy_function=copy_file,
        )

        return files_copied, total_files

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

        return sum(
            len(files)
            for root in (client_path, server_path)
            for _, _, files in os.walk(root)
        )

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