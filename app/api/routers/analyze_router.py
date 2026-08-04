"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : analyze.py
Descrição : Endpoints responsáveis pela execução de Análises.
--------------------------------------------------------------------
"""

from fastapi import APIRouter
from fastapi import Request

from app.models.analyzers.analyze_request import (
    AnalyzeRequest,
)

router = APIRouter(
    prefix="/analyzes",
    tags=["Analyzes"],
)


@router.post("")
def execute_analyze(
    analyze_request: AnalyzeRequest,
    request: Request,
):
    """
    Inicia uma análise.
    """

    bootstrap = request.app.state.bootstrap

    return bootstrap.execute_analyze_use_case.execute(
        analyze_request,
    )