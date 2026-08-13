"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_router.py
Descrição : Endpoints responsáveis pela execução de Publish.
--------------------------------------------------------------------
"""

from fastapi import (
    APIRouter,
    HTTPException,
    Request,
)

from app.models.publish.publish_request import (
    PublishRequest,
)

from app.services.publish_execution_lock import (
    PublishExecutionLock,
)


router = APIRouter(
    prefix="/publishes",
    tags=["Publishes"],
)


publish_execution_lock = (
    PublishExecutionLock()
)


@router.post("")
def execute_publish(
    publish_request: PublishRequest,
    request: Request,
):
    """
    Inicia um Publish.

    Somente uma execução de Publish pode
    ocorrer simultaneamente.
    """

    #
    # Tenta adquirir o Lock.
    #

    if not publish_execution_lock.try_acquire():

        raise HTTPException(
            status_code=409,
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

        #
        # Executa o Publish.
        #

        bootstrap = (
            request.app.state.bootstrap
        )

        return (
            bootstrap
            .execute_publish_use_case
            .execute(
                publish_request,
            )
        )

    finally:

        #
        # O Lock deve ser liberado sempre,
        # inclusive quando ocorrer uma exceção.
        #

        publish_execution_lock.release()