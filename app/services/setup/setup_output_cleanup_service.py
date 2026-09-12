"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_output_cleanup_service.py
Descrição : Prepara a pasta de saída para uma nova execução de
            geração de Setups, preservando a pasta .work.
--------------------------------------------------------------------
"""

from pathlib import Path
import os
import shutil
from threading import Lock

from app.models.configuration.app_settings import (
    AppSettings,
)
from app.models.setup.setup_output_cleanup_result import (
    SetupOutputCleanupResult,
)


class SetupOutputCleanupService:
    """
    Prepara a pasta configurada para saída dos Setups.

    A limpeza nunca remove a pasta raiz e nunca remove a pasta
    `.work` existente diretamente dentro dela.
    """

    __LOCK = Lock()
    __PRESERVED_DIRECTORY_NAME = ".work"

    def __init__(
        self,
        settings: AppSettings,
    ) -> None:
        if settings is None:
            raise ValueError(
                "AppSettings não foi informado."
            )

        self.__settings = settings

    def execute(self) -> SetupOutputCleanupResult:
        """
        Limpa a pasta de saída configurada, preservando `.work`.

        A pasta raiz permanece existente. Caso ainda não exista,
        ela é criada sem que uma remoção seja realizada.
        """

        output_root = Path(
            self.__settings.setup.output_root,
        )

        if str(output_root).strip() == "":
            raise ValueError(
                "O caminho da pasta de saída dos Setups não foi informado."
            )

        output_root = output_root.expanduser()
        preserved_path = (
            output_root
            / self.__PRESERVED_DIRECTORY_NAME
        )

        with self.__LOCK:
            output_root.mkdir(
                parents=True,
                exist_ok=True,
            )

            if not output_root.is_dir():
                raise NotADirectoryError(
                    f"A pasta de saída dos Setups não é um diretório: {output_root}"
                )

            removed_items = 0

            for item in output_root.iterdir():
                if item.name.lower() == (
                    self.__PRESERVED_DIRECTORY_NAME.lower()
                ):
                    continue

                self.__remove_item(item)
                removed_items += 1

        return SetupOutputCleanupResult(
            success=True,
            message=(
                "Pasta de saída dos Setups preparada com sucesso. "
                f"Itens removidos: {removed_items}. "
                f"Pasta preservada: {preserved_path}."
            ),
            output_root=str(output_root),
            preserved_path=str(preserved_path),
            removed_items=removed_items,
        )

    @classmethod
    def __remove_item(
        cls,
        item: Path,
    ) -> None:
        """
        Remove um item da pasta de saída.
        """

        if item.is_symlink():
            cls.__make_writable(item)
            item.unlink()
            return

        if item.is_dir():
            shutil.rmtree(
                item,
                onerror=cls.__handle_remove_error,
            )
            return

        cls.__make_writable(item)
        item.unlink()

    @staticmethod
    def __make_writable(
        path: Path,
    ) -> None:
        """
        Remove o atributo somente leitura quando necessário.
        """

        try:
            os.chmod(
                path,
                os.stat(path).st_mode | 0o200,
            )
        except OSError:
            pass

    @classmethod
    def __handle_remove_error(
        cls,
        function,
        path,
        exc_info,
    ) -> None:
        """
        Trata arquivos somente leitura durante a remoção.
        """

        path_obj = Path(path)
        cls.__make_writable(path_obj)
        function(path)
