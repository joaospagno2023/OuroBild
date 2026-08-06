"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_context.py
Descrição : Contexto utilizado durante a execução de um Build.
--------------------------------------------------------------------
"""

from app.models.build.build_definition import (
    BuildDefinition,
)
from app.models.build.build_paths import (
    BuildPaths,
)
from app.models.build.build_request import (
    BuildRequest,
)
from app.models.environment.build_environment import (
    BuildEnvironment,
)
from app.models.project.project import (
    Project,
)


class BuildContext:
    """
    Contexto compartilhado durante
    toda a execução do Build.
    """

    def __init__(
        self,
    ) -> None:

        #
        # Entrada
        #

        self.request: BuildRequest | None = None

        self.environment: BuildEnvironment | None = None

        self.project: Project | None = None

        #
        # Definição do Build
        #

        self.definition: BuildDefinition | None = None

        #
        # Caminhos
        #

        self.paths = BuildPaths()

        #
        # Dados compartilhados
        #

        self.artifacts: dict[str, object] = {}

        self.metadata: dict[str, object] = {}