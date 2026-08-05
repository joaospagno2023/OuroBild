"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : workspace_context_factory.py
Descrição : Responsável por criar um WorkspaceContext.
--------------------------------------------------------------------
"""

from pathlib import Path

from app.abstractions.environment_repository import (
    EnvironmentRepository,
)

from app.abstractions.project_repository import (
    ProjectRepository,
)

from app.workspace.workspace_context import (
    WorkspaceContext,
)


class WorkspaceContextFactory:
    """
    Responsável por criar um WorkspaceContext.
    """

    def __init__(
        self,
        project_repository: ProjectRepository,
        environment_repository: EnvironmentRepository,
    ) -> None:

        self.__project_repository = (
            project_repository
        )

        self.__environment_repository = (
            environment_repository
        )

    def create(
        self,
        project_id: str,
        environment_id: str,
    ) -> WorkspaceContext:
        """
        Resolve todas as informações de um projeto.
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

        project_file = (
            Path(
                environment.root_path,
            )
            / project.project_path
        )

        return WorkspaceContext(

            project=project,

            environment=environment,

            project_file=project_file,

        )