"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : update_user_request.py
Descrição : Dados para atualização de usuário.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class UpdateUserRequest(BaseModel):
    """
    Define os dados que podem ser alterados em um usuário.
    """

    display_name: str
    email: str | None = None
    is_active: bool = True
    must_change_password: bool = False
