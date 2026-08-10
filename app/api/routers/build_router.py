"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_router.py
Descrição : Endpoints responsáveis pela execução de Builds.
--------------------------------------------------------------------
"""

from fastapi import APIRouter
from fastapi import Request

from app.models.build.build_request import BuildRequest

router = APIRouter(
    prefix="/builds",
    tags=["Builds"],
)


@router.post("")
def execute_build(
    build_request: BuildRequest,
    request: Request,
):
    """
    Inicia uma Build.
    """

    import traceback

   
    bootstrap = request.app.state.bootstrap

    try:

        result = bootstrap.execute_build_use_case.execute(
            build_request,
        )

        return result

    except Exception as ex:
        traceback.print_exc()
        raise