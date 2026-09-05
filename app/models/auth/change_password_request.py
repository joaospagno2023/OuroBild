"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : change_password_request.py
Descrição : Modelo de entrada para alteração de senha.
--------------------------------------------------------------------
"""

from pydantic import (
    BaseModel,
)


class ChangePasswordRequest(
    BaseModel,
):
    """
    Dados necessários para alterar uma senha.
    """

    current_password: str

    new_password: str