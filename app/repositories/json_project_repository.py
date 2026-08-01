"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : json_project_repository.py
Descrição : Repositório responsável pela leitura dos projetos.
--------------------------------------------------------------------
"""

import json
from pathlib import Path

from app.abstractions.project_repository import ProjectRepository
from app.models.configuration.app_settings import AppSettings
from app.models.project.project import Project


class JsonProjectRepository(ProjectRepository):
    """
    Implementação do repositório de projetos baseada em JSON.
    """

    def __init__(
        self,
        configuration_path: Path,
        settings: AppSettings,
    ) -> None:
        """
        Inicializa o repositório.

        Args:
            configuration_path: Caminho da pasta de configuração.
            settings: Configurações da aplicação.
        """

        self.__projects_file = (
            configuration_path / "projects.json"
        )

        self.__settings = settings

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
                self.__resolve_project(item),
            )

            projects.append(project)

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

    def __resolve_project(
        self,
        project: dict,
    ) -> dict:
        """
        Resolve as variáveis existentes no projects.json.
        """

        resolved = project.copy()

        replacements = {
            "{BASE_PATH}": str(self.__settings.base_path),
            "{INSTALLER_PATH}": str(
                self.__settings.installer_path,
            ),
            "{PUBLISH_PATH}": str(
                self.__settings.publish_path,
            ),
        }

        for key, value in resolved.items():

            if not isinstance(value, str):
                continue

            for placeholder, replacement in replacements.items():

                value = value.replace(
                    placeholder,
                    replacement,
                )

            resolved[key] = value

        return resolved