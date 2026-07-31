"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_repository.py
Descrição : Contrato para leitura dos projetos configurados.
--------------------------------------------------------------------
"""

from abc import ABC, abstractmethod

from app.models.project.project import Project


class ProjectRepository(ABC):
    """
    Define o contrato para obtenção dos projetos.
    """

    @abstractmethod
    def get_all(self) -> list[Project]:
        """
        Retorna todos os projetos configurados.
        """
        raise NotImplementedError
    @abstractmethod
    def get_by_id(self,project_id: str,) -> Project | None:
        """
        Retorna um projeto pelo identificador.
        """
        raise NotImplementedError