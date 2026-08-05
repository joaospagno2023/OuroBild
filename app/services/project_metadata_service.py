"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_metadata_service.py
Descrição : Serviço responsável pelo gerenciamento da metadata
            dos projetos.
--------------------------------------------------------------------
"""

from datetime import datetime
from pathlib import Path

from app.abstractions.project_metadata_repository import (
    ProjectMetadataRepository,
)
from app.models.project.project_metadata import (
    ProjectMetadata,
)
from app.services.hash_service import (
    HashService,
)


class ProjectMetadataService:
    """
    Serviço responsável por gerenciar
    a metadata dos projetos.
    """

    def __init__(
        self,
        repository: ProjectMetadataRepository,
        hash_service: HashService,
    ) -> None:
        """
        Inicializa o serviço.
        """

        self.__repository = repository
        self.__hash_service = hash_service

    def load(
        self,
        project_id: str,
    ) -> ProjectMetadata | None:
        """
        Carrega a metadata de um projeto.
        """

        return self.__repository.load(
            project_id,
        )

    def save(
        self,
        metadata: ProjectMetadata,
    ) -> None:
        """
        Salva a metadata de um projeto.
        """

        self.__repository.save(
            metadata,
        )

    def exists(
        self,
        project_id: str,
    ) -> bool:
        """
        Verifica se existe metadata.
        """

        return self.__repository.exists(
            project_id,
        )

    def delete(
        self,
        project_id: str,
    ) -> None:
        """
        Remove a metadata.
        """

        self.__repository.delete(
            project_id,
        )

    def update_from_analysis(
        self,
        project_id: str,
        project_file: Path,
    ) -> ProjectMetadata:
        """
        Atualiza a metadata após uma análise.
        """

        metadata = ProjectMetadata(
            project_id=project_id,
            project_hash=self.__hash_service.calculate_file_hash(
                project_file,
            ),
            project_last_write=datetime.fromtimestamp(
                project_file.stat().st_mtime,
            ),
            last_analysis=datetime.now(),
        )

        self.__repository.save(
            metadata,
        )

        return metadata