"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_request.py
Descrição : Representa uma solicitação de Build.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class BuildRequest(BaseModel):
    """
    Representa uma solicitação de execução de Build.
    """

    project_id: str

    environment_id: str

    version: str | None = None

    revision: int | None = None