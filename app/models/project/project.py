"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project.py
Descrição : Modelo que representa um projeto configurado para build.
--------------------------------------------------------------------
"""

from pydantic import BaseModel

from app.models.build.compilation_engine import (
    CompilationEngine,
)

from app.models.build.compilation_target import (
    CompilationTarget,
)
from app.models.project.project_type import (
    ProjectType,
)


class Project(BaseModel):
    """
    Representa um projeto configurado no arquivo projects.json.
    """

    id: str

    name: str

    description: str

    type: ProjectType

    #
    # Origem da compilação
    #

    solution_path: str | None = None

    project_path: str | None = None

    compilation_target: CompilationTarget

    compilation_engine: CompilationEngine

    #
    # Publicação
    #

    publish_path: str

    publish_profile: str | None = None

    #
    # Instalador
    #

    aip_path: str

    output_msi: str

    network_path: str

    #
    # Configuração
    #

    configuration: str

    platform: str

    enabled: bool

    