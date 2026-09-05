"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : update_project_status_request.py
Descrição : Dados necessários para alteração do status de um projeto.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class UpdateProjectStatusRequest(
    BaseModel,
):
    """
    Representa os dados para alteração do status de um projeto.
    """

    enabled: bool