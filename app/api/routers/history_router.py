"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : history_router.py
Descrição : Endpoints do histórico de execuções.
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
from app.models.history.pipeline_history_detail import (
    PipelineHistoryDetail,
)
from app.models.history.pipeline_history_item import (
    PipelineHistoryItem,
)
from app.models.history.pipeline_history_logs import (
    PipelineHistoryLogs,
)
from app.services.history.pipeline_history_service import (
    PipelineHistoryService,
)


router = APIRouter(
    prefix="/history",
    tags=["History"],
    dependencies=[
        Depends(get_current_user),
    ],
)


def __get_service(
    request: Request,
) -> PipelineHistoryService:
    return request.app.state.bootstrap.pipeline_history_service


@router.get(
    "",
    response_model=list[PipelineHistoryItem],
)
def get_history(
    request: Request,
) -> list[PipelineHistoryItem]:
    """
    Retorna o histórico resumido das execuções.
    """

    return __get_service(request).get_all()


@router.get(
    "/{execution_id}/logs",
    response_model=PipelineHistoryLogs,
)
def get_history_logs(
    execution_id: str,
    request: Request,
) -> PipelineHistoryLogs:
    """
    Retorna os logs associados a uma execução.
    """

    logs = __get_service(request).get_logs(
        execution_id,
    )

    if logs is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Logs da execução não encontrados.",
        )

    return logs


@router.get(
    "/{execution_id}",
    response_model=PipelineHistoryDetail,
)
def get_history_detail(
    execution_id: str,
    request: Request,
) -> PipelineHistoryDetail:
    """
    Retorna os detalhes de uma execução.
    """

    execution = __get_service(request).get_by_execution_id(
        execution_id,
    )

    if execution is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execução não encontrada no histórico.",
        )

    return execution