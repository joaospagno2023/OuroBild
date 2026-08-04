"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : analyze_request.py
Descrição : Modelo de requisição da análise de um projeto.
--------------------------------------------------------------------
"""

from pydantic import BaseModel, Field


class AnalyzeRequest(
    BaseModel,
):
    """
    Requisição para análise de um projeto.
    """

    project_file: str = Field(
        description="Caminho completo do arquivo .csproj.",
    )