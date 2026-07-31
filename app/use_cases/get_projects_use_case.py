"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : get_projects_use_case.py
Descrição : Caso de uso responsável por retornar os projetos
             configurados.
--------------------------------------------------------------------
"""

from app.abstractions.project_repository import ProjectRepository
from app.models.project.project import Project


class GetProjectsUseCase:
    """
    Caso de uso responsável por listar os projetos.
    """

    def __init__(
        self,
        repository: ProjectRepository,
    ) -> None:
        self._repository = repository

    def execute(self) -> list[Project]:
        """
        Retorna todos os projetos cadastrados.
        """
        return self._repository.get_all()