"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : configuration_router.py
Descrição : Endpoints de gerenciamento das configurações do OuroBuild.
--------------------------------------------------------------------
"""

from fastapi import (
    APIRouter,
    Depends,
    Request,
)

from app.api.dependencies.current_user import (
    get_current_user,
)

from app.models.auth.user import (
    User,
)

from app.models.configuration.configuration_response import (
    ConfigurationResponse,
)

from app.models.configuration.configuration_update_request import (
    ConfigurationUpdateRequest,
)

from app.models.configuration.path_selection_response import (
    PathSelectionResponse,
)


router = APIRouter(
    prefix="/configuration",
    tags=["Configuration"],
)


@router.get(
    "",
    response_model=ConfigurationResponse,
)
def get_configuration(
    request: Request,
    current_user: User = Depends(
        get_current_user,
    ),
) -> ConfigurationResponse:
    """
    Retorna as configurações operacionais da aplicação.
    """

    _ = current_user

    bootstrap = request.app.state.bootstrap

    return (
        bootstrap.configuration_service
        .get_configuration()
    )


@router.put(
    "",
    response_model=ConfigurationResponse,
)
def update_configuration(
    request: Request,
    configuration_request: ConfigurationUpdateRequest,
    current_user: User = Depends(
        get_current_user,
    ),
) -> ConfigurationResponse:
    """
    Atualiza as configurações operacionais da aplicação.
    """

    _ = current_user

    bootstrap = request.app.state.bootstrap

    return (
        bootstrap.configuration_service
        .update_configuration(
            request=configuration_request,
        )
    )


@router.get(
    "/browse-folder",
    response_model=PathSelectionResponse,
)
def browse_folder(
    request: Request,
    initial_path: str | None = None,
    current_user: User = Depends(
        get_current_user,
    ),
) -> PathSelectionResponse:
    """
    Abre o seletor nativo de pastas do Windows.
    """

    _ = current_user

    bootstrap = request.app.state.bootstrap

    selected_path = (
        bootstrap.configuration_service
        .browse_folder(
            initial_path=initial_path,
        )
    )

    return PathSelectionResponse(
        path=selected_path,
    )


@router.get(
    "/browse-file",
    response_model=PathSelectionResponse,
)
def browse_file(
    request: Request,
    initial_path: str | None = None,
    current_user: User = Depends(
        get_current_user,
    ),
) -> PathSelectionResponse:
    """
    Abre o seletor nativo de arquivos do Windows.
    """

    _ = current_user

    bootstrap = request.app.state.bootstrap

    selected_path = (
        bootstrap.configuration_service
        .browse_file(
            initial_path=initial_path,
        )
    )

    return PathSelectionResponse(
        path=selected_path,
    )