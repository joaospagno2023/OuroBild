"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_context.py
Descrição : Contexto utilizado durante a execução de um Publish.
--------------------------------------------------------------------
"""

from app.models.environment.build_environment import (
    BuildEnvironment,
)
from app.models.project.project import Project
from app.models.publish.publish_paths import PublishPaths
from app.models.publish.publish_request import PublishRequest


class PublishContext:
    """
    Contexto compartilhado durante toda a execução do Publish.
    """

    def __init__(
        self,
    ) -> None:

        #
        # Entrada
        #

        self.request: PublishRequest | None = None

        self.environment: BuildEnvironment | None = None

        self.project: Project | None = None

        #
        # Caminhos
        #

        self.paths = PublishPaths()

        #
        # Dados compartilhados
        #

        self.artifacts: dict[str, object] = {}

        self.metadata: dict[str, object] = {}