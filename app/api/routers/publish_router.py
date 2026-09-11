"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : publish_router.py
Descrição : Endpoints responsáveis pela execução de Publish.
--------------------------------------------------------------------
"""

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Request,
)

from app.api.dependencies.authorization_dependencies import (
    require_permission,
)
from app.api.dependencies.current_user import (
    get_current_user,
)
from app.models.publish.publish_request import (
    PublishRequest,
)
from app.models.setup.publish_setups_request import (
    PublishSetupsRequest,
)
from app.models.setup.setup_batch_publish_request import (
    SetupBatchPublishRequest,
)
from app.models.setup.setup_batch_publish_result import (
    SetupBatchPublishResult,
)
from app.models.setup.setup_publication_status_result import (
    SetupPublicationProjectStatus,
    SetupPublicationStatusResult,
)


router = APIRouter(
    prefix="/publishes",
    tags=["Publishes"],
    dependencies=[
        Depends(get_current_user),
    ],
)


@router.post(
    "",
    dependencies=[
        Depends(
            require_permission(
                "build.execute",
            ),
        ),
    ],
)
def execute_publish(
    publish_request: PublishRequest,
    request: Request,
):
    """
    Executa um Publish.

    Requer a permissão:

        build.execute
    """

    bootstrap = request.app.state.bootstrap

    return (
        bootstrap.execute_publish_use_case.execute(
            publish_request,
        )
    )


@router.post(
    "/setups/network",
    response_model=SetupBatchPublishResult,
    dependencies=[
        Depends(
            require_permission(
                "setup.execute",
            ),
        ),
    ],
)
def publish_setups_network(
    publish_request: PublishSetupsRequest,
    request: Request,
    background_tasks: BackgroundTasks,
) -> SetupBatchPublishResult:
    """
    Cria um lote de publicação e inicia a cópia em segundo plano.

    Requer a permissão:

        setup.execute
    """

    bootstrap = request.app.state.bootstrap

    try:
        setup_batch_request = SetupBatchPublishRequest(
            execution_ids=publish_request.execution_ids,
            version=publish_request.version,
            revision=publish_request.revision,
        )

        result = bootstrap.publish_setups_use_case.start(
            setup_batch_request,
        )

        background_tasks.add_task(
            bootstrap.publish_setups_use_case.execute_batch,
            setup_batch_request,
            result.batch_id,
        )

        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except (FileNotFoundError, NotADirectoryError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get(
    "/setups/network/{batch_id}",
    response_model=SetupPublicationStatusResult,
    dependencies=[
        Depends(
            require_permission(
                "setup.execute",
            ),
        ),
    ],
)
def get_setup_publication_status(
    batch_id: str,
    request: Request,
) -> SetupPublicationStatusResult:
    """Retorna o estado atual de um lote de publicação."""

    bootstrap = request.app.state.bootstrap

    try:
        batch = bootstrap.setup_publication_batch_repository.get_by_batch_id(
            batch_id,
        )
        if batch is None:
            raise HTTPException(
                status_code=404,
                detail=f"Lote não encontrado: {batch_id}",
            )

        logs = bootstrap.setup_publication_log_repository.get_by_batch_id(
            batch_id,
        )

        projects = _build_project_statuses(logs)
        progress_percent = (
            round(
                (batch.completed_setups / batch.total_setups) * 100
            )
            if batch.total_setups > 0
            else 0
        )

        success: bool | None
        if batch.status == "completed":
            success = True
        elif batch.status == "failed":
            success = False
        else:
            success = None

        return SetupPublicationStatusResult(
            batch_id=batch.batch_id,
            status=batch.status,
            success=success,
            message=batch.message,
            total=batch.total_setups,
            completed=batch.completed_setups,
            failed=batch.failed_setups,
            progress_percent=progress_percent,
            projects=projects,
        )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


def _build_project_statuses(
    logs,
) -> list[SetupPublicationProjectStatus]:
    project_data: dict[str, SetupPublicationProjectStatus] = {}

    for log in logs:
        if not log.project_id:
            continue

        execution_id = log.execution_id or ""
        current = project_data.get(log.project_id)

        if current is None:
            current = SetupPublicationProjectStatus(
                project_id=log.project_id,
                execution_id=execution_id,
                status="waiting",
                message="Aguardando início da cópia...",
            )
            project_data[log.project_id] = current

        if log.execution_id:
            current.execution_id = log.execution_id

        if log.event_type == "PROJECT_PUBLISH_START":
            current.status = "publishing"
            current.message = log.message
        elif log.event_type == "PROJECT_PUBLISH_SUCCESS":
            current.status = "success"
            current.message = log.message
        elif log.event_type == "PROJECT_PUBLISH_FAILED":
            current.status = "error"
            current.message = log.message

    return list(project_data.values())
