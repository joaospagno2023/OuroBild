"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : token.py
Descrição : Modelo de resposta da autenticação.
--------------------------------------------------------------------
"""

from pydantic import (
    BaseModel,
)


class TokenResponse(
    BaseModel,
):
    """
    Representa o resultado da autenticação.
    """

    access_token: str

    token_type: str

    expires_in: int

    must_change_password: bool