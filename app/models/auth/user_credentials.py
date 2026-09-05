"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : user_credentials.py
Descrição : Representa os dados necessários para autenticação.
--------------------------------------------------------------------
"""

from datetime import datetime

from pydantic import BaseModel

from app.models.auth.user import User


class UserCredentials(BaseModel):
    """
    Representa os dados de autenticação de um usuário.
    """

    user: User

    password_hash: str

    created_at: datetime