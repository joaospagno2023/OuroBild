"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_setups_result.py
Descrição : Resultado da publicação de múltiplos Setups na rede.
--------------------------------------------------------------------
"""

from pydantic import BaseModel, Field

from app.models.setup.setup_network_publish_result import (
    SetupNetworkPublishResult,
)


class PublishSetupsResult(BaseModel):
    """Representa o resultado consolidado da publicação em lote."""

    success: bool

    message: str

    total: int = 0

    completed: int = 0

    failed: int = 0

    projects: list[SetupNetworkPublishResult] = Field(
        default_factory=list,
    )
