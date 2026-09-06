"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : path_selection_response.py
Descrição : Contrato de resposta para seleção de caminhos no Windows.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class PathSelectionResponse(BaseModel):
    """
    Representa o resultado de uma seleção de pasta ou arquivo.
    """

    path: str | None