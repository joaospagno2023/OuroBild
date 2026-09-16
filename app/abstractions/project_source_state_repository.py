"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_source_state_repository.py
Descrição : Contrato para persistência do estado dos fontes.
--------------------------------------------------------------------
"""

from abc import ABC, abstractmethod

from app.models.source_control.project_source_state import ProjectSourceState


class ProjectSourceStateRepository(ABC):
    """Define a persistência do estado dos fontes por projeto."""

    @abstractmethod
    def get_by_project_id(
        self,
        project_id: str,
    ) -> ProjectSourceState | None:
        raise NotImplementedError

    @abstractmethod
    def save(
        self,
        state: ProjectSourceState,
    ) -> ProjectSourceState:
        raise NotImplementedError
