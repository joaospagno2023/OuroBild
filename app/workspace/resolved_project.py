"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : resolved_project.py
Descrição : Representa um projeto completamente resolvido para um
             Workspace específico.
--------------------------------------------------------------------
"""

from dataclasses import dataclass
from pathlib import Path

from app.models.environment.environment import Environment
from app.models.project.project import Project


@dataclass(
    frozen=True,
    slots=True,
)
class ResolvedProject:
    """
    Representa um projeto após a resolução do Workspace.
    """

    project: Project

    environment: Environment

    workspace_root: Path

    project_file: Path

    solution_file: Path | None = None

    def has_solution(
        self,
    ) -> bool:
        """
        Indica se existe um arquivo de solução associado.
        """

        return (
            self.solution_file is not None
        )