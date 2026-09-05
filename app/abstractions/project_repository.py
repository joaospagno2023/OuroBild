"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_repository.py
Descrição : Contrato para gerenciamento dos projetos configurados.
--------------------------------------------------------------------
"""

from abc import (
    ABC,
    abstractmethod,
)

from app.models.project.create_project_request import (
    CreateProjectRequest,
)

from app.models.project.project import (
    Project,
)

from app.models.project.update_project_request import (
    UpdateProjectRequest,
)


class ProjectRepository(
    ABC,
):
    """
    Define as operações necessárias para gerenciamento de projetos.
    """

    @abstractmethod
    def get_all(
        self,
    ) -> list[Project]:
        """
        Retorna todos os projetos configurados.
        """

        raise NotImplementedError

    @abstractmethod
    def get_by_id(
        self,
        project_id: str,
    ) -> Project | None:
        """
        Retorna um projeto pelo identificador.
        """

        raise NotImplementedError

    @abstractmethod
    def create(
        self,
        request: CreateProjectRequest,
    ) -> Project:
        """
        Cria um novo projeto.
        """

        raise NotImplementedError

    @abstractmethod
    def update(
        self,
        project_id: str,
        request: UpdateProjectRequest,
    ) -> Project:
        """
        Atualiza um projeto existente.
        """

        raise NotImplementedError

    @abstractmethod
    def update_status(
        self,
        project_id: str,
        enabled: bool,
    ) -> Project:
        """
        Atualiza somente o status do projeto.
        """

        raise NotImplementedError