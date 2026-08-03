"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_context_factory.py
Descrição : Responsável por criar o contexto de execução do Publish.
--------------------------------------------------------------------
"""

from app.abstractions.environment_repository import (
    EnvironmentRepository,
)
from app.abstractions.project_repository import (
    ProjectRepository,
)
from app.exceptions.project_not_found_exception import (
    ProjectNotFoundException,
)
from app.models.publish.publish_context import PublishContext
from app.models.publish.publish_request import PublishRequest


class PublishContextFactory:
    """
    Responsável por montar o PublishContext.
    """

    def __init__(
        self,
        project_repository: ProjectRepository,
        environment_repository: EnvironmentRepository,
    ) -> None:

        self.__project_repository = project_repository
        self.__environment_repository = environment_repository

    def create(
        self,
        request: PublishRequest,
    ) -> PublishContext:
        """
        Cria um PublishContext a partir da requisição.
        """

        context = PublishContext()

        context.request = request

        project = self.__project_repository.get_by_id(
            request.project_id,
        )

        if project is None:

            raise ProjectNotFoundException(
                f"Projeto '{request.project_id}' não encontrado."
            )

        environment = self.__environment_repository.get_by_id(
            request.environment_id,
        )

        if environment is None:

            raise ValueError(
                f"Ambiente '{request.environment_id}' não encontrado."
            )

        context.project = project
        context.environment = environment

        return context