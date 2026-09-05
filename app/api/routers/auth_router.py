"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : auth_router.py
Descrição : Endpoints de autenticação do OuroBuild.
--------------------------------------------------------------------
"""

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
    status,
)

from app.api.dependencies.current_user import (
    get_current_user,
)

from app.models.auth.change_password_request import (
    ChangePasswordRequest,
)

from app.models.auth.token import (
    TokenResponse,
)

from app.models.auth.user import (
    User,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/token",
    response_model=TokenResponse,
)
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
) -> TokenResponse:
    """
    Autentica um usuário e retorna um JWT.
    """

    bootstrap = request.app.state.bootstrap

    return (
        bootstrap.authentication_service.authenticate(
            username=username,
            password=password,
        )
    )


@router.get(
    "/me",
    response_model=User,
)
def get_me(
    current_user: User = Depends(
        get_current_user,
    ),
) -> User:
    """
    Retorna o usuário autenticado.
    """

    return current_user


@router.post(
    "/change-password",
    response_model=User,
)
def change_password(
    request: Request,
    password_request: ChangePasswordRequest,
    current_user: User = Depends(
        get_current_user,
    ),
) -> User:
    """
    Altera a senha do usuário autenticado.
    """

    bootstrap = request.app.state.bootstrap

    try:
        return bootstrap.user_service.change_password(
            user=current_user,
            current_password=(
                password_request.current_password
            ),
            new_password=(
                password_request.new_password
            ),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc