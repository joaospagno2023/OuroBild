"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : workspace_context.py
Descrição : Representa as informações resolvidas de um Workspace.
--------------------------------------------------------------------
"""

from dataclasses import dataclass
from pathlib import Path

from app.models.environment.build_environment import (
    BuildEnvironment,
)

from app.models.project.project import (
    Project,
)


@dataclass
class WorkspaceContext:
    """
    Contém todas as informações resolvidas
    de um projeto dentro de um ambiente.
    """

    project: Project

    environment: BuildEnvironment

    project_file: Path