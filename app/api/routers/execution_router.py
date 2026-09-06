"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : execution_router.py
Descrição : Endpoints de acompanhamento das execuções assíncronas.
--------------------------------------------------------------------
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)

from app.api.dependencies.current_user import (
    get_current_user,
)
from app.models.auth.user import (
    User,
)
from app.models.execution.pipeline_execution_response import (
    PipelineExecutionResponse,
)
from app.services.pipeline.pipeline_execution_service import (
    get_pipeline_execution_service,
)


router = APIRouter(
    prefix="/executions",
    tags=["Executions"],
    dependencies=[
        Depends(get_current_user),
    ],
)


@router.get(
    "/{execution_id}",
    response_model=PipelineExecutionResponse,
)
def get_execution(
    execution_id: str,
    request: Request,
) -> PipelineExecutionResponse:
    """
    Retorna o estado atual de uma execução.
    """

    execution_service = (
        get_pipeline_execution_service()
    )

    execution = execution_service.get(
        execution_id,
    )

    if execution is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Execução não encontrada.",
        )

    return execution