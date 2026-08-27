"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_file_synchronizer.py
Descrição : Identifica alterações entre os arquivos do Setup e
            os arquivos existentes no diretório de publicação.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.models.setup.setup_file import (
    SetupFile,
)

from app.models.setup.setup_file_action import (
    SetupFileAction,
)

from app.models.setup.setup_file_sync import (
    SetupFileSync,
)


class SetupFileSynchronizer:
    """
    Identifica diferenças entre os arquivos atualmente presentes
    no Setup e os arquivos existentes no publish_path.

    Responsabilidades:

        - identificar arquivos para UPDATE;
        - identificar arquivos para REMOVE;
        - identificar arquivos para ADD.

    O Synchronizer não altera o projeto de Setup.
    Ele apenas produz a lista de SetupFileSync.
    """

    def synchronize(
        self,
        setup_files: list[SetupFile],
        publish_path: Path,
    ) -> list[SetupFileSync]:
        """
        Compara os arquivos do Setup com o conteúdo publicado.

        :param setup_files:
            Arquivos atualmente presentes no Setup.

        :param publish_path:
            Diretório contendo os arquivos publicados.

        :return:
            Lista de alterações identificadas.
        """

        if setup_files is None:

            raise ValueError(
                "Arquivos do Setup não foram informados."
            )

        if publish_path is None:

            raise ValueError(
                "Pasta de publicação não foi informada."
            )

        publish_path = Path(
            publish_path,
        )

        if not publish_path.exists():

            raise FileNotFoundError(
                "Pasta de publicação não encontrada:\n"
                f"{publish_path}"
            )

        if not publish_path.is_dir():

            raise ValueError(
                "Pasta de publicação não é um diretório:\n"
                f"{publish_path}"
            )

        setup_by_name = (
            self.__index_setup_files(
                setup_files,
            )
        )

        publish_by_name = (
            self.__index_publish_files(
                publish_path,
            )
        )

        changes: list[SetupFileSync] = []

        #
        # ------------------------------------------------------------
        # Arquivos existentes no Setup.
        # ------------------------------------------------------------
        #

        for name, setup_file in (
            setup_by_name.items()
        ):
            publish_file = (
                publish_by_name.get(
                    name,
                )
            )

            #
            # Arquivo existe no Setup mas não existe
            # mais no publish.
            #

            if publish_file is None:

                changes.append(
                    SetupFileSync(
                        name=setup_file.name,
                        source_path=setup_file.source_path,
                        publish_path=(
                            publish_path
                            / setup_file.name
                        ),
                        assembly_display_name=(
                            getattr(
                                setup_file,
                                "assembly_display_name",
                                None,
                            )
                        ),
                        action=(
                            SetupFileAction.REMOVE
                        ),
                    )
                )

                continue

            #
            # Arquivo existe nos dois locais.
            #

            changes.append(
                SetupFileSync(
                    name=setup_file.name,
                    source_path=(
                        setup_file.source_path
                    ),
                    publish_path=publish_file,
                    assembly_display_name=(
                        getattr(
                            setup_file,
                            "assembly_display_name",
                            None,
                        )
                    ),
                    action=(
                        SetupFileAction.UPDATE
                    ),
                )
            )

        #
        # ------------------------------------------------------------
        # Arquivos existentes somente no publish.
        # ------------------------------------------------------------
        #

        for publish_file in (
            publish_by_name.values()
        ):
            name = publish_file.name

            if name.lower() in setup_by_name:

                continue

            changes.append(
                SetupFileSync(
                    name=name,
                    source_path=name,
                    publish_path=publish_file,
                    action=(
                        SetupFileAction.ADD
                    ),
                )
            )

        return changes

    @staticmethod
    def __index_setup_files(
        setup_files: list[SetupFile],
    ) -> dict[str, SetupFile]:
        """
        Cria índice dos arquivos do Setup pelo nome.

        A chave é normalizada para comparação case-insensitive,
        mas o objeto original é preservado.
        """

        result: dict[str, SetupFile] = {}

        for setup_file in setup_files:

            if setup_file is None:

                continue

            if not setup_file.name:

                continue

            result[
                setup_file.name.lower()
            ] = setup_file

        return result

    @staticmethod
    def __index_publish_files(
        publish_path: Path,
    ) -> dict[str, Path]:
        """
        Cria índice dos arquivos publicados.

        A chave é normalizada para comparação case-insensitive,
        enquanto o Path original é preservado para manter
        o nome real do arquivo.
        """

        result: dict[str, Path] = {}

        for path in (
            publish_path.iterdir()
        ):

            if not path.is_file():

                continue

            result[
                path.name.lower()
            ] = path

        return result