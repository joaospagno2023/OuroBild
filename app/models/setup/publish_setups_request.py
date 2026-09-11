"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_setups_request.py
Descrição : Solicitação para publicação de múltiplos Setups na rede.
--------------------------------------------------------------------
"""

from pydantic import BaseModel, Field


class PublishSetupsRequest(BaseModel):
    """Representa uma solicitação de publicação em lote."""

    execution_ids: list[str] = Field(
        min_length=1,
    )

    version: str

    revision: int = 0
