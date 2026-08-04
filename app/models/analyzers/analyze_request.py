"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : analyze_request.py
Descrição : Modelo de requisição da análise de projetos.
--------------------------------------------------------------------
"""

from pydantic import BaseModel
from pydantic import Field


class AnalyzeRequest(
    BaseModel,
):
    """
    Requisição para execução da análise de um projeto.
    """

    project: str = Field(
        ...,
        description="Identificador do projeto.",
        examples=[
            "ouronet.client.winservice.linkpagamento",
        ],
    )

    environment: str = Field(
        ...,
        description="Identificador do ambiente.",
        examples=[
            "production",
        ],
    )