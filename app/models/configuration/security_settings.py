"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : security_settings.py
Descrição : Representa as configurações de segurança da aplicação.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class SecuritySettings(
    BaseModel,
):
    """
    Representa as configurações utilizadas pela autenticação.
    """

    jwt_secret: str = ""

    jwt_algorithm: str = "HS256"

    token_expiration_minutes: int = 60