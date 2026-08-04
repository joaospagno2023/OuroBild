"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_router.py
Descrição : Endpoints responsáveis pela execução de Publish.
--------------------------------------------------------------------
"""

from fastapi import APIRouter
from fastapi import Request

from app.models.publish.publish_request import (
    PublishRequest,
)

router = APIRouter(
    prefix="/publishes",
    tags=["Publishes"],
)


@router.post("")
def execute_publish(
    publish_request: PublishRequest,
    request: Request,
):
    """
    Inicia um Publish.
    """

    bootstrap = request.app.state.bootstrap

    return bootstrap.execute_publish_use_case.execute(
        publish_request,
    )