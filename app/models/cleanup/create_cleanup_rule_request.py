"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : create_cleanup_rule_request.py
Descrição : Dados necessários para criar uma regra de limpeza.
--------------------------------------------------------------------
"""

from pydantic import BaseModel

from app.models.cleanup.cleanup_rule import (
    CleanupAction,
    CleanupTarget,
)


class CreateCleanupRuleRequest(
    BaseModel,
):
    """
    Representa os dados necessários para criar
    uma regra específica de limpeza.
    """

    target: CleanupTarget

    pattern: str

    action: CleanupAction

    recursive: bool = True

    description: str | None = None

    enabled: bool = True