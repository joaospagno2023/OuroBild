"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : create_project_request.py
Descrição : Dados necessários para criação de um projeto.
--------------------------------------------------------------------
"""

from pydantic import (
    BaseModel,
)

from app.models.build.compilation_engine import (
    CompilationEngine,
)

from app.models.build.compilation_target import (
    CompilationTarget,
)

from app.models.project.project_type import (
    ProjectType,
)


class CreateProjectRequest(
    BaseModel,
):
    """
    Representa os dados para criação de um projeto.
    """

    id: str
    name: str
    description: str
    type: ProjectType

    solution_path: str | None = None
    project_path: str | None = None

    compilation_target: CompilationTarget
    compilation_engine: CompilationEngine

    publish_path: str
    publish_profile: str | None = None

    aip_path: str
    visualstudio_setup_path: str | None = None

    output_msi: str
    network_path: str

    configuration: str
    platform: str
    enabled: bool = True