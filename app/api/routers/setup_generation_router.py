"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_generation_router.py
Descrição : Endpoints relacionados ao início da geração de Setups.
--------------------------------------------------------------------
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)

from app.api.dependencies.authorization_dependencies import (
    require_permission,
)
from app.api.dependencies.current_user import (
    get_current_user,
)
from app.models.setup.setup_output_cleanup_result import (
    SetupOutputCleanupResult,
)


router = APIRouter(
    prefix="/setups",
    tags=["Setups"],
    dependencies=[
        Depends(get_current_user),
    ],
)


@router.post(
    "/prepare-output",
    response_model=SetupOutputCleanupResult,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            require_permission(
                "setup.execute",
            ),
        ),
    ],
)
def prepare_setup_output(
    request: Request,
) -> SetupOutputCleanupResult:
    """
    Prepara a pasta de saída para uma nova execução de geração.

    A pasta configurada é limpa uma única vez quando este endpoint
    é chamado. A pasta `.work` existente dentro dela é preservada.
    """

    bootstrap = request.app.state.bootstrap

    try:
        return bootstrap.setup_output_cleanup_service.execute()
    except (ValueError, OSError) as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
