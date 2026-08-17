"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_file_synchronizer.py
Descrição : Compara arquivos do Setup com o publish_path.
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
    Compara os arquivos existentes no Setup com os arquivos
    disponíveis no publish_path.

    Este serviço não altera o .vdproj.
    """

    def synchronize(
        self,
        setup_files: list[SetupFile],
        publish_path: Path,
    ) -> list[SetupFileSync]:
        """
        Calcula as alterações necessárias.
        """

        if setup_files is None:
            raise ValueError(
                "Os arquivos do Setup não foram informados."
            )

        if publish_path is None:
            raise ValueError(
                "PublishPath não foi informado."
            )

        publish_path = Path(
            publish_path,
        )

        if not publish_path.exists():
            raise FileNotFoundError(
                "PublishPath não encontrado: "
                f"{publish_path}"
            )

        if not publish_path.is_dir():
            raise ValueError(
                "PublishPath não é um diretório: "
                f"{publish_path}"
            )

        setup_by_name = {
            item.name.lower(): item
            for item in setup_files
        }

        published_files = {
            item.name.lower(): item
            for item in publish_path.iterdir()
            if item.is_file()
            and item.suffix.lower() == ".dll"
        }

        result: list[SetupFileSync] = []

        #
        # Arquivos existentes no Setup
        #

        for setup_file in setup_files:

            key = setup_file.name.lower()

            published_file = (
                published_files.get(key)
            )

            if published_file is None:

                data = setup_file.model_dump()

                data["action"] = (
                    SetupFileAction.REMOVE
                )

                result.append(
                    SetupFileSync(
                        **data,
                    )
                )

                continue

            data = setup_file.model_dump()

            data["publish_path"] = (
                published_file
            )

            data["action"] = (
                SetupFileAction.UPDATE
            )

            result.append(
                SetupFileSync(
                    **data,
                )
            )

        #
        # Arquivos novos publicados
        #

        setup_names = set(
            setup_by_name.keys()
        )

        for key, published_file in (
            published_files.items()
        ):

            if key in setup_names:
                continue

            result.append(
                SetupFileSync(
                    name=published_file.name,
                    source_path=published_file.name,
                    publish_path=published_file,
                    assembly_display_name=None,
                    action=(
                        SetupFileAction.ADD
                    ),
                )
            )

        return result