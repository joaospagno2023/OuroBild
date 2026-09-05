"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : environment_router.py
Descrição : Endpoints relacionados aos ambientes de Build.
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

from app.models.environment.build_environment import (
    BuildEnvironment,
)

from app.models.environment.create_environment_request import (
    CreateEnvironmentRequest,
)

from app.models.environment.environment_response import (
    EnvironmentResponse,
)

from app.models.environment.update_environment_request import (
    UpdateEnvironmentRequest,
)


router = APIRouter(
    prefix="/environments",
    tags=["Environments"],
    dependencies=[
        Depends(get_current_user),
    ],
)


def _to_response(
    environment: BuildEnvironment,
) -> EnvironmentResponse:
    """
    Converte o modelo de domínio para o modelo de resposta da API.
    """

    return EnvironmentResponse(
        id=environment.id,
        name=environment.name,
        resolver=environment.resolver,
        root_path=str(environment.root_path),
    )


@router.get(
    "",
    response_model=list[EnvironmentResponse],
)
def get_environments(
    request: Request,
) -> list[EnvironmentResponse]:
    """
    Retorna todos os ambientes.
    """

    bootstrap = request.app.state.bootstrap

    environments = bootstrap.environment_service.get_all()

    return [
        _to_response(environment)
        for environment in environments
    ]


@router.get(
    "/{environment_id}",
    response_model=EnvironmentResponse,
)
def get_environment(
    environment_id: str,
    request: Request,
) -> EnvironmentResponse:
    """
    Retorna um ambiente pelo identificador.
    """

    bootstrap = request.app.state.bootstrap

    environment = bootstrap.environment_service.get_by_id(
        environment_id,
    )

    if environment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ambiente não encontrado.",
        )

    return _to_response(environment)


@router.post(
    "",
    response_model=EnvironmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_environment(
    request: Request,
    environment_request: CreateEnvironmentRequest,
) -> EnvironmentResponse:
    """
    Cria um novo ambiente.
    """

    bootstrap = request.app.state.bootstrap

    try:
        environment = bootstrap.environment_service.create(
            request=environment_request,
        )

        return _to_response(environment)

    except ValueError as exc:
        message = str(exc)

        if message == "EnvironmentId já está cadastrado.":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        ) from exc


@router.put(
    "/{environment_id}",
    response_model=EnvironmentResponse,
)
def update_environment(
    environment_id: str,
    request: Request,
    environment_request: UpdateEnvironmentRequest,
) -> EnvironmentResponse:
    """
    Atualiza um ambiente existente.
    """

    bootstrap = request.app.state.bootstrap

    try:
        environment = bootstrap.environment_service.update(
            environment_id=environment_id,
            request=environment_request,
        )

        if environment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ambiente não encontrado.",
            )

        return _to_response(environment)

    except ValueError as exc:
        message = str(exc)

        if message == "Ambiente não encontrado.":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        ) from exc