"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : cleanup_rule.py
Descrição : Representa uma regra de limpeza do Build.
--------------------------------------------------------------------
"""

from enum import Enum

from pydantic import BaseModel


class CleanupAction(str, Enum):
    """
    Ação que será aplicada pela regra de limpeza.
    """

    REMOVE = "remove"

    PRESERVE = "preserve"


class CleanupTarget(str, Enum):
    """
    Tipo de recurso ao qual a regra se aplica.
    """

    FILE = "file"

    DIRECTORY = "directory"


class CleanupRule(BaseModel):
    """
    Representa uma regra de limpeza de arquivos ou diretórios.

    project_id:
        None  -> regra global.

        Informado -> regra específica de um projeto.
    """

    target: CleanupTarget

    pattern: str

    action: CleanupAction

    recursive: bool = True

    project_id: str | None = None

    description: str | None = None