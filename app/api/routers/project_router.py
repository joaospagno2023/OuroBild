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
    HTTPException,
    Request,
    status,
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

from app.models.project.create_project_request import (
    CreateProjectRequest,
)

from app.models.project.project import (
    Project,
)

from app.models.project.update_project_request import (
    UpdateProjectRequest,
)

from app.models.project.update_project_status_request import (
    UpdateProjectStatusRequest,
)


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
    dependencies=[
        Depends(get_current_user),
    ],
)


@router.get(
    "",
    response_model=list[Project],
)
def get_projects(
    request: Request,
) -> list[Project]:
    """
    Retorna todos os projetos.
    """

    bootstrap = request.app.state.bootstrap

    return bootstrap.project_service.get_all()


@router.get(
    "/{project_id}",
    response_model=Project,
)
def get_project(
    project_id: str,
    request: Request,
) -> Project:
    """
    Retorna um projeto pelo identificador.
    """

    bootstrap = request.app.state.bootstrap

    project = bootstrap.project_service.get_by_id(
        project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado.",
        )

    return project


@router.post(
    "",
    response_model=Project,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    request: Request,
    project_request: CreateProjectRequest,
) -> Project:
    """
    Cria um novo projeto.
    """

    bootstrap = request.app.state.bootstrap

    try:
        return bootstrap.project_service.create(
            request=project_request,
        )

    except ValueError as exc:
        message = str(exc)

        if message == "ProjectId já está cadastrado.":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        ) from exc


@router.put(
    "/{project_id}",
    response_model=Project,
)
def update_project(
    project_id: str,
    request: Request,
    project_request: UpdateProjectRequest,
) -> Project:
    """
    Atualiza um projeto existente.
    """

    bootstrap = request.app.state.bootstrap

    try:
        return bootstrap.project_service.update(
            project_id=project_id,
            request=project_request,
        )

    except ValueError as exc:
        message = str(exc)

        if message == "Projeto não encontrado.":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        ) from exc


@router.patch(
    "/{project_id}/status",
    response_model=Project,
)
def update_project_status(
    project_id: str,
    request: Request,
    status_request: UpdateProjectStatusRequest,
) -> Project:
    """
    Atualiza somente o status de um projeto.
    """

    bootstrap = request.app.state.bootstrap

    try:
        return bootstrap.project_service.update_status(
            project_id=project_id,
            enabled=status_request.enabled,
        )

    except ValueError as exc:
        message = str(exc)

        if message == "Projeto não encontrado.":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        ) from exc


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