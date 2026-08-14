"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : json_project_repository.py
Descrição : Repositório responsável pela leitura dos projetos.
--------------------------------------------------------------------
"""

import json
from pathlib import Path

from app.abstractions.project_repository import (
    ProjectRepository,
)

from app.models.project.project import (
    Project,
)


class JsonProjectRepository(
    ProjectRepository,
):
    """
    Implementação do repositório de projetos
    baseada em JSON.
    """

    def __init__(
        self,
        configuration_path: Path,
    ) -> None:
        """
        Inicializa o repositório.

        Args:
            configuration_path:
                Caminho da pasta de configuração.
        """

        self.__projects_file = (
            configuration_path
            / "projects.json"
        )

    def get_all(
        self,
    ) -> list[Project]:
        """
        Retorna todos os projetos configurados.
        """

        with self.__projects_file.open(
            mode="r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        projects: list[Project] = []

        for item in data:

            project = Project.model_validate(
                item,
            )

            projects.append(
                project,
            )

        return projects

    def get_by_id(
        self,
        project_id: str,
    ) -> Project | None:
        """
        Retorna um projeto pelo identificador.
        """

        for project in self.get_all():

            if project.id == project_id:
                return project

        return None