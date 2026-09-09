"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : update_profile_request.py
Descrição : Modelo para atualização do perfil do usuário autenticado.
--------------------------------------------------------------------
"""

from pydantic import (
    BaseModel,
)


class UpdateProfileRequest(
    BaseModel,
):
    """Dados editáveis pelo próprio usuário."""

    display_name: str
    email: str | None = None
