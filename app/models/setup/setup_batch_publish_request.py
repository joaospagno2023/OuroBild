"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_batch_publish_request.py
Descrição : Representa uma solicitação de publicação em lote de
            Setups na rede.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class SetupBatchPublishRequest(
    BaseModel,
):
    """
    Dados necessários para publicar uma geração completa
    de Setup na rede.
    """

    execution_ids: list[str]

    version: str

    revision: int
