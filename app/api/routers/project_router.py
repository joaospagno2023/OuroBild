"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_router.py
Descrição : Endpoints relacionados aos projetos.
--------------------------------------------------------------------
"""

from fastapi import (
    APIRouter,
    Depends,
    Request,
)

from app.api.dependencies.authorization_dependencies import (
    require_permission,
)

from app.api.dependencies.current_user import (
    get_current_user,
)

from app.models.pipeline.pipeline_execution_request import (
    PipelineExecutionRequest,
)


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
    dependencies=[
        Depends(get_current_user),
    ],
)


@router.get("")
def get_projects(
    request: Request,
):
    """
    Retorna os projetos disponíveis.
    """

    bootstrap = request.app.state.bootstrap

    return bootstrap.get_projects_use_case.execute()


@router.post(
    "/{project_id}/execute",
    dependencies=[
        Depends(
            require_permission(
                "build.execute",
            ),
        ),
        Depends(
            require_permission(
                "setup.execute",
            ),
        ),
    ],
)
def execute_pipeline(
    project_id: str,
    request: Request,
    execution: PipelineExecutionRequest,
):
    """
    Executa a Pipeline do projeto.

    Requer as permissões:

        - build.execute
        - setup.execute
    """

    bootstrap = request.app.state.bootstrap

    return bootstrap.execute_pipeline_use_case.execute(
        project_id=project_id,
        environment_id=execution.environment_id,
        version=execution.version,
        revision=execution.revision,
    )