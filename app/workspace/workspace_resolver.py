"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : workspace_resolver.py
Descrição : Responsável por resolver o caminho físico de um projeto
             a partir do projeto e do ambiente informados.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.abstractions.environment_repository import (
    EnvironmentRepository,
)
from app.abstractions.project_repository import (
    ProjectRepository,
)


class WorkspaceResolver:
    """
    Responsável por resolver o caminho físico
    de um projeto.
    """

    def __init__(
        self,
        project_repository: ProjectRepository,
        environment_repository: EnvironmentRepository,
    ) -> None:
        """
        Inicializa o resolver.
        """

        self.__project_repository = (
            project_repository
        )

        self.__environment_repository = (
            environment_repository
        )

    def resolve_project(
        self,
        project_id: str,
        environment_id: str,
    ) -> Path:
        """
        Resolve o caminho completo do arquivo
        do projeto (.csproj).

        Args:
            project_id:
                Identificador do projeto.

            environment_id:
                Identificador do ambiente.

        Returns:
            Caminho completo do arquivo .csproj.
        """

        project = (
            self.__project_repository.get_by_id(
                project_id=project_id,
            )
        )

        environment = (
            self.__environment_repository.get_by_id(
                environment_id=environment_id,
            )
        )

        return (
            Path(
                environment.root_path,
            )
            / project.project_path
        )