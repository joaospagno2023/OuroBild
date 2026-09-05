"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : analyze_router.py
Descrição : Endpoints responsáveis pela execução de Análises.
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

from app.models.analyzers.analyze_request import (
    AnalyzeRequest,
)


router = APIRouter(
    prefix="/analyzes",
    tags=["Analyzes"],
    dependencies=[
        Depends(get_current_user),
    ],
)


@router.post("")
def execute_analyze(
    analyze_request: AnalyzeRequest,
    request: Request,
):
    """
    Executa uma análise.
    """

    bootstrap = request.app.state.bootstrap

    return (
        bootstrap.execute_analyze_use_case.execute(
            analyze_request,
        )
    )