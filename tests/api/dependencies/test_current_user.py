"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_current_user.py
Descrição : Testes da dependência de usuário autenticado.
--------------------------------------------------------------------
"""

from unittest.mock import (
    MagicMock,
)

import pytest
from fastapi import (
    HTTPException,
)

from app.api.dependencies.current_user import (
    get_current_user,
)


def test_deve_rejeitar_token_invalido():
    """
    Deve rejeitar um token inválido.
    """

    request = MagicMock()

    request.app.state.bootstrap.jwt_service.decode.side_effect = (
        ValueError(
            "Token inválido."
        )
    )

    credentials = MagicMock()

    credentials.credentials = "token-invalido"

    with pytest.raises(
        HTTPException,
    ) as exception:

        get_current_user(
            request=request,
            credentials=credentials,
        )

    assert exception.value.status_code == 401


def test_deve_rejeitar_token_sem_subject():
    """
    Deve rejeitar um token sem o campo sub.
    """

    request = MagicMock()

    request.app.state.bootstrap.jwt_service.decode.return_value = {
        "username": "joaospagnol",
    }

    credentials = MagicMock()

    credentials.credentials = "token-sem-sub"

    with pytest.raises(
        HTTPException,
    ) as exception:

        get_current_user(
            request=request,
            credentials=credentials,
        )

    assert exception.value.status_code == 401