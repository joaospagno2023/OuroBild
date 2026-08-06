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

    print("=" * 80)
    print("ENTROU NO ENDPOINT /builds")
    print("=" * 80)

    bootstrap = request.app.state.bootstrap

    try:

        result = bootstrap.execute_build_use_case.execute(
            build_request,
        )

        print("=" * 80)
        print("BUILD EXECUTADO COM SUCESSO")
        print("=" * 80)

        return result

    except Exception as ex:

        print("=" * 80)
        print("ERRO NO ENDPOINT BUILD")
        print("=" * 80)

        traceback.print_exc()

        print(type(ex))
        print(ex)

        raise