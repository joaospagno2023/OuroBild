"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : update_profile_request.py
Descrição : Dados para atualização do perfil do usuário autenticado.
--------------------------------------------------------------------
"""

from pydantic import (
    BaseModel,
)


class UpdateProfileRequest(
    BaseModel,
):
    """
    Define os dados que o próprio usuário pode alterar no perfil.
    """

    display_name: str