"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : user.py
Descrição : Representa o usuário autenticado da aplicação.
--------------------------------------------------------------------
"""

from datetime import (
    datetime,
)

from pydantic import (
    BaseModel,
)


class User(
    BaseModel,
):
    """
    Representa um usuário do OuroBuild.
    """

    id: int

    username: str

    display_name: str

    email: str | None

    is_active: bool

    created_at: datetime

    last_login_at: datetime | None