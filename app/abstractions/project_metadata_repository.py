"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_metadata_repository.py
Descrição : Contrato para persistência da metadata dos projetos.
--------------------------------------------------------------------
"""

from abc import ABC
from abc import abstractmethod

from app.models.project.project_metadata import (
    ProjectMetadata,
)


class ProjectMetadataRepository(
    ABC,
):
    """
    Contrato para persistência da metadata
    dos projetos.
    """

    @abstractmethod
    def load(
        self,
        project_id: str,
    ) -> ProjectMetadata | None:
        """
        Carrega a metadata de um projeto.
        """
        pass

    @abstractmethod
    def save(
        self,
        metadata: ProjectMetadata,
    ) -> None:
        """
        Persiste a metadata de um projeto.
        """
        pass

    @abstractmethod
    def exists(
        self,
        project_id: str,
    ) -> bool:
        """
        Verifica se existe metadata para o projeto.
        """
        pass

    @abstractmethod
    def delete(
        self,
        project_id: str,
    ) -> None:
        """
        Remove a metadata de um projeto.
        """
        pass