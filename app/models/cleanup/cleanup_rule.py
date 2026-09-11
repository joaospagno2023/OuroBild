"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : cleanup_rule.py
Descrição : Modelos de domínio das regras de limpeza.
--------------------------------------------------------------------
"""

from enum import Enum

from pydantic import BaseModel


class CleanupAction(
    str,
    Enum,
):
    """
    Define a ação aplicada por uma regra.
    """

    REMOVE = "remove"
    PRESERVE = "preserve"


class CleanupTarget(
    str,
    Enum,
):
    """
    Define o tipo de recurso tratado pela regra.
    """

    FILE = "file"
    DIRECTORY = "directory"


class CleanupRule(
    BaseModel,
):
    """
    Representa uma regra de limpeza persistida.
    """

    id: int | None = None

    target: CleanupTarget

    pattern: str

    action: CleanupAction

    recursive: bool = True

    project_id: str | None = None

    description: str | None = None

    priority: int = 100

    enabled: bool = True