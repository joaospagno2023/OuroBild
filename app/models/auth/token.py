"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : token.py
Descrição : Representa o token retornado pela autenticação.
--------------------------------------------------------------------
"""

from pydantic import BaseModel


class TokenResponse(
    BaseModel,
):
    """
    Representa a resposta da autenticação.
    """

    access_token: str

    token_type: str = "bearer"

    expires_in: int