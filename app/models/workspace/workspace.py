"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : workspace.py
Descrição : Representa um Workspace disponível para execução.
--------------------------------------------------------------------
"""

from pathlib import Path

from pydantic import BaseModel

from app.models.workspace.workspace_type import WorkspaceType


class Workspace(BaseModel):
    """
    Representa um Workspace.
    """

    id: str

    name: str

    root_path: Path

    workspace_type: WorkspaceType