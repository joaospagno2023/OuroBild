"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : environment_response.py
Descrição : Modelo de resposta da API para ambientes.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class EnvironmentResponse(BaseModel):
    id: str
    name: str
    resolver: str
    root_path: str