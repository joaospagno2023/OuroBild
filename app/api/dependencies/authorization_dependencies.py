"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : authorization_dependencies.py
Descrição : Dependências de autorização da API.
--------------------------------------------------------------------
"""

from collections.abc import Callable

from fastapi import (
    Depends,
    HTTPException,
    Request,
    status,
)

from app.api.dependencies.current_user import (
    get_current_user,
)
from app.models.auth.user import User


def require_permission(
    permission_key: str,
) -> Callable:
    """
    Cria uma dependency que exige uma determinada permissão.

    Args:
        permission_key:
            Chave da permissão exigida.

    Returns:
        Dependency do FastAPI.
    """

    if not permission_key:
        raise ValueError(
            "PermissionKey não foi informado."
        )

    def permission_dependency(
        request: Request,
        current_user: User = Depends(
            get_current_user,
        ),
    ) -> User:
        """
        Valida a permissão do usuário autenticado.
        """

        bootstrap = request.app.state.bootstrap

        has_permission = (
            bootstrap.permission_service.has_permission(
                user_id=current_user.id,
                permission_key=permission_key,
            )
        )

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Usuário não possui a permissão "
                    f"'{permission_key}'."
                ),
            )

        return current_user

    return permission_dependency