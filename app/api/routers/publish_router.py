"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_router.py
Descrição : Endpoints responsáveis pela execução de Publish.
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

from app.models.publish.publish_request import (
    PublishRequest,
)


router = APIRouter(
    prefix="/publishes",
    tags=["Publishes"],
    dependencies=[
        Depends(get_current_user),
    ],
)


@router.post("")
def execute_publish(
    publish_request: PublishRequest,
    request: Request,
):
    """
    Executa um Publish.
    """

    bootstrap = request.app.state.bootstrap

    return (
        bootstrap.execute_publish_use_case.execute(
            publish_request,
        )
    )