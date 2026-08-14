"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_api_request.py
Descrição : Modelo da solicitação de geração de Setup pela API.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class SetupApiRequest(
    BaseModel,
):
    """
    Dados recebidos pela API para geração de Setup.

    O project_id não pertence ao body porque é informado
    através da URL.
    """

    environment_id: str

    version: str | None = None

    revision: int | None = None