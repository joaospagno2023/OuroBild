"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_republish_request.py
Descrição : Solicitação para copiar para a rede Setups já gerados,
            sem gerá-los novamente.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class SetupRepublishRequest(BaseModel):
    """Identifica a versão local já gerada que será copiada."""

    version: str

    revision: int
