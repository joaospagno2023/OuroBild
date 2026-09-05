"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : update_user_status_request.py
Descrição : Dados para atualização do status do usuário.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class UpdateUserStatusRequest(BaseModel):
    """
    Define o novo status de um usuário.
    """

    is_active: bool