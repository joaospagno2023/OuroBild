"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_router.py
Descrição : Endpoints responsáveis pela execução e publicação de Setup.
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
from app.models.publish.publish_request import (
    PublishRequest,
)
from app.models.setup.setup_publication_request import (
    SetupPublicationRequest,
)
from app.models.setup.setup_publication_start_result import (
    SetupPublicationStartResult,
)
from app.models.setup.setup_publication_status_result import (
    SetupPublicationStatusResult,
)


from app.services.publish_execution_lock import (
    PublishExecutionLock,
)


publish_execution_lock = PublishExecutionLock()


router = APIRouter(
    prefix="/publishes",
    tags=["Publishes"],
    dependencies=[
        Depends(get_current_user),
    ],
)


@router.post(
    "",
    dependencies=[
        Depends(
            require_permission(
                "build.execute",
            ),
        ),
    ],
)
def execute_publish(
    publish_request: PublishRequest,
    request: Request,
):
    """
    Executa um Publish.

    Requer a permissão:

        build.execute
    """

    if not publish_execution_lock.try_acquire():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "status": "busy",
                "message": (
                    "Já existe uma publicação "
                    "em execução. Aguarde a "
                    "conclusão da publicação atual."
                ),
            },
        )

    try:
        bootstrap = request.app.state.bootstrap

        return (
            bootstrap.execute_publish_use_case.execute(
                publish_request,
            )
        )
    finally:
        publish_execution_lock.release()


@router.post(
    "/setups/network",
    response_model=SetupPublicationStartResult,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[
        Depends(
            require_permission(
                "setup.execute",
            ),
        ),
    ],
)
def start_setup_network_publication(
    publication_request: SetupPublicationRequest,
    request: Request,
) -> SetupPublicationStartResult:
    """Inicia a cópia dos Setups para a rede em background."""

    bootstrap = request.app.state.bootstrap

    return bootstrap.setup_network_publication_service.start(
        publication_request,
    )


@router.get(
    "/setups/network/{batch_id}",
    response_model=SetupPublicationStatusResult,
)
def get_setup_network_publication_status(
    batch_id: str,
    request: Request,
) -> SetupPublicationStatusResult:
    """Retorna o progresso atual de uma publicação de Setup."""

    bootstrap = request.app.state.bootstrap

    result = bootstrap.setup_network_publication_service.get(
        batch_id,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publicação de Setup não encontrada.",
        )

    return result
