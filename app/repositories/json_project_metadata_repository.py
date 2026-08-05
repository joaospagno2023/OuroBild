"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : json_project_metadata_repository.py
Descrição : Persistência da metadata dos projetos em JSON.
--------------------------------------------------------------------
"""

import json

from dataclasses import asdict
from pathlib import Path

from app.abstractions.project_metadata_repository import (
    ProjectMetadataRepository,
)

from app.models.project.project_metadata import (
    ProjectMetadata,
)


class JsonProjectMetadataRepository(
    ProjectMetadataRepository,
):
    """
    Responsável por persistir a metadata
    dos projetos em arquivos JSON.
    """

    def __init__(
        self,
        metadata_path: Path,
    ) -> None:
        """
        Inicializa o repositório.
        """

        self.__metadata_path = metadata_path

    def __get_file(
        self,
        project_id: str,
    ) -> Path:
        """
        Retorna o caminho do arquivo de metadata.
        """

        return (
            self.__metadata_path
            / project_id
            / "metadata.json"
        )

    def load(
        self,
        project_id: str,
    ) -> ProjectMetadata | None:
        """
        Carrega a metadata do projeto.
        """

        file = self.__get_file(
            project_id,
        )

        if not file.exists():

            return None

        #
        # Nesta Sprint retornaremos o JSON.
        #
        # A reconstrução completa do
        # ProjectMetadata será implementada
        # na próxima Sprint.
        #

        with open(
            file,
            "r",
            encoding="utf-8",
        ) as fp:

            data = json.load(
                fp,
            )

        return ProjectMetadata(
            **data,
        )

    def save(
        self,
        metadata: ProjectMetadata,
    ) -> None:
        """
        Salva a metadata do projeto.
        """

        file = self.__get_file(
            metadata.project_id,
        )

        file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            file,
            "w",
            encoding="utf-8",
        ) as fp:

            json.dump(

                asdict(
                    metadata,
                ),

                fp,

                indent=4,

                ensure_ascii=False,

                default=str,
            )

    def exists(
        self,
        project_id: str,
    ) -> bool:
        """
        Verifica se existe metadata.
        """

        return self.__get_file(
            project_id,
        ).exists()

    def delete(
        self,
        project_id: str,
    ) -> None:
        """
        Remove a metadata do projeto.
        """

        file = self.__get_file(
            project_id,
        )

        if file.exists():

            file.unlink()