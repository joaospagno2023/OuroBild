"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_publication_request.py
Descrição : Solicitação para publicação assíncrona de Setups na rede.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class SetupPublicationRequest(BaseModel):
    """Representa uma solicitação de publicação de Setups."""

    execution_ids: list[str]

    version: str

    revision: int
