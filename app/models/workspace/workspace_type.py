"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : workspace_type.py
Descrição : Tipos de Workspace suportados pelo OuroBuild.
--------------------------------------------------------------------
"""

from enum import Enum


class WorkspaceType(str, Enum):
    """
    Tipos de Workspace.
    """

    VERSIONED = "versioned"

    PRODUCTION = "production"