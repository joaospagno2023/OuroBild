"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_publish_router.py
Descrição : Endpoints relacionados à publicação em lote de Setups.
--------------------------------------------------------------------
"""

from fastapi import (
    APIRouter,
    Depends,
    Request,
)

from app.api.dependencies.authorization_dependencies import (
    require_permission,
)

from app.api.dependencies.current_user import (
    get_current_user,
)

from app.models.setup.setup_batch_publish_request import (
    SetupBatchPublishRequest,
)

from app.models.setup.setup_batch_publish_result import (
    SetupBatchPublishResult,
)


router = APIRouter(
    prefix="/setups",
    tags=["Setups"],
    dependencies=[
        Depends(get_current_user),
    ],
)


@router.post(
    "/publish",
    response_model=SetupBatchPublishResult,
    dependencies=[
        Depends(
            require_permission(
                "setup.execute",
            ),
        ),
    ],
)
def publish_setups(
    publish_request: SetupBatchPublishRequest,
    request: Request,
) -> SetupBatchPublishResult:
    """
    Publica a versão gerada na rede após validar
    todas as execuções selecionadas.
    """

    bootstrap = request.app.state.bootstrap

    return bootstrap.publish_setups_use_case.execute(
        publish_request,
    )
