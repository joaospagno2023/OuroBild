"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : update_cleanup_rule_request.py
Descrição : Dados necessários para atualizar uma regra de limpeza.
--------------------------------------------------------------------
"""

from pydantic import BaseModel

from app.models.cleanup.cleanup_rule import (
    CleanupAction,
    CleanupTarget,
)


class UpdateCleanupRuleRequest(
    BaseModel,
):
    """
    Representa os dados necessários para atualizar
    uma regra específica de limpeza.
    """

    target: CleanupTarget

    pattern: str

    action: CleanupAction

    recursive: bool = True

    description: str | None = None

    enabled: bool = True