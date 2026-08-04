"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : analyze_request.py
Descrição : Modelo de requisição para análise de projeto.
--------------------------------------------------------------------
"""

from pydantic import BaseModel, Field


class AnalyzeRequest(
    BaseModel,
):
    """
    Requisição utilizada para iniciar
    uma análise de projeto.
    """

    project_file: str = Field(
        description="Caminho completo do arquivo .csproj.",
        min_length=1,
    )