"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : reset_password_response.py
Descrição : Resultado da redefinição administrativa de senha.
--------------------------------------------------------------------
"""

from pydantic import BaseModel

from app.models.auth.user import User


class ResetPasswordResponse(BaseModel):
    """
    Representa o resultado da redefinição de senha.
    """

    user: User
    temporary_password: str