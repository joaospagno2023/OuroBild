"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : current_user.py
Descrição : Dependência para obtenção do usuário autenticado.
--------------------------------------------------------------------
"""

from fastapi import (
    Depends,
    HTTPException,
    Request,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from jwt import (
    InvalidTokenError,
)

from app.models.auth.user import (
    User,
)


security = HTTPBearer(
    auto_error=True,
)


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(
        security,
    ),
) -> User:
    """
    Obtém o usuário autenticado a partir do JWT.

    Args:
        request:
            Requisição HTTP atual.

        credentials:
            Credenciais Bearer.

    Returns:
        Usuário autenticado.
    """

    bootstrap = request.app.state.bootstrap

    token = credentials.credentials

    try:
        payload = (
            bootstrap.jwt_service.decode(
                token,
            )
        )

    except (
        InvalidTokenError,
        ValueError,
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Token inválido ou expirado.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    subject = payload.get(
        "sub",
    )

    if subject is None:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Token sem identificador de usuário.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    try:
        user_id = int(
            subject,
        )

    except (
        TypeError,
        ValueError,
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Identificador de usuário inválido.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    user = (
        bootstrap.user_repository
        .get_by_id(
            user_id,
        )
    )

    if user is None:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Usuário não encontrado.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if not user.is_active:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail="Usuário inativo.",
        )

    return user