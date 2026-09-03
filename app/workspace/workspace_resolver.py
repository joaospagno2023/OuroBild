"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : workspace_resolver.py
Descrição : Responsável por resolver as informações de um projeto
             dentro de um Workspace.
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

from app.exceptions.project_not_found_exception import (
    ProjectNotFoundException,
)

from app.exceptions.environment_not_found_exception import (
    EnvironmentNotFoundException,
)


class WorkspaceResolver:
    """
    Responsável por resolver um projeto
    dentro de um ambiente.
    """

    def __init__(
        self,
        project_repository: ProjectRepository,
        environment_repository: EnvironmentRepository,
    ) -> None:
        """
        Inicializa o resolver.
        """

        if project_repository is None:
            raise ValueError(
                "ProjectRepository não foi informado."
            )

        if environment_repository is None:
            raise ValueError(
                "EnvironmentRepository não foi informado."
            )

        self.__project_repository = (
            project_repository
        )

        self.__environment_repository = (
            environment_repository
        )

    def resolve(
        self,
        project_id: str,
        environment_id: str,
    ) -> WorkspaceContext:
        """
        Resolve todas as informações necessárias
        para trabalhar com um projeto.

        Args:
            project_id:
                Identificador do projeto.

            environment_id:
                Identificador do ambiente.

        Returns:
            WorkspaceContext contendo projeto,
            ambiente e caminho do arquivo.

        Raises:
            ProjectNotFoundException:
                Quando o projeto não existe.

            EnvironmentNotFoundException:
                Quando o ambiente não existe.
        """

        project = (
            self.__project_repository.get_by_id(
                project_id=project_id,
            )
        )

        if project is None:
            raise ProjectNotFoundException(
                project_id=project_id,
            )

        environment = (
            self.__environment_repository.get_by_id(
                environment_id=environment_id,
            )
        )

        if environment is None:
            raise EnvironmentNotFoundException(
                environment_id=environment_id,
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