"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : create_user_request.py
Descrição : Modelo de entrada para criação de usuários.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class CreateUserRequest(
    BaseModel,
):
    """
    Dados necessários para criação de um usuário.
    """

    username: str

    display_name: str

    email: str | None = None

    password: str

    is_active: bool = True

    must_change_password: bool = True