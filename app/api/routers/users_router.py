"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : users_router.py
Descrição : Endpoints de gerenciamento de usuários do OuroBuild.
--------------------------------------------------------------------
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)

from app.api.dependencies.current_user import (
    get_current_user,
)

from app.models.auth.create_user_request import (
    CreateUserRequest,
)

from app.models.auth.reset_password_response import (
    ResetPasswordResponse,
)

from app.models.auth.update_user_request import (
    UpdateUserRequest,
)

from app.models.auth.update_user_status_request import (
    UpdateUserStatusRequest,
)

from app.models.auth.user import (
    User,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "",
    response_model=list[User],
)
def get_users(
    request: Request,
    current_user: User = Depends(
        get_current_user,
    ),
) -> list[User]:
    """
    Retorna todos os usuários autenticados.
    """

    _ = current_user

    bootstrap = request.app.state.bootstrap

    return bootstrap.user_service.get_all()


@router.post(
    "",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    request: Request,
    user_request: CreateUserRequest,
    current_user: User = Depends(
        get_current_user,
    ),
) -> User:
    """
    Cria um novo usuário autenticado.
    """

    _ = current_user

    bootstrap = request.app.state.bootstrap

    try:
        return bootstrap.user_service.create(
            request=user_request,
        )

    except ValueError as exc:
        message = str(exc)

        if message == "Username já está cadastrado.":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        ) from exc


@router.put(
    "/{user_id}",
    response_model=User,
)
def update_user(
    user_id: int,
    request: Request,
    user_request: UpdateUserRequest,
    current_user: User = Depends(
        get_current_user,
    ),
) -> User:
    """
    Atualiza os dados de um usuário autenticado.
    """

    _ = current_user

    bootstrap = request.app.state.bootstrap

    try:
        return bootstrap.user_service.update(
            user_id=user_id,
            request=user_request,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{user_id}/status",
    response_model=User,
)
def update_user_status(
    user_id: int,
    request: Request,
    user_request: UpdateUserStatusRequest,
    current_user: User = Depends(
        get_current_user,
    ),
) -> User:
    """
    Atualiza somente o status de um usuário autenticado.
    """

    _ = current_user

    bootstrap = request.app.state.bootstrap

    try:
        return bootstrap.user_service.update_status(
            user_id=user_id,
            request=user_request,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/{user_id}/reset-password",
    response_model=ResetPasswordResponse,
)
def reset_user_password(
    user_id: int,
    request: Request,
    current_user: User = Depends(
        get_current_user,
    ),
) -> ResetPasswordResponse:
    """
    Redefine administrativamente a senha de um usuário.
    """

    _ = current_user

    bootstrap = request.app.state.bootstrap

    try:
        return bootstrap.user_service.reset_password(
            user_id=user_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc