"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_router.py
Descrição : Endpoints relacionados aos projetos.
--------------------------------------------------------------------
"""

from fastapi import APIRouter, Request

from app.models.setup.setup_api_request import (
    SetupApiRequest,
)

from app.models.setup.setup_request import (
    SetupRequest,
)


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.get("")
def get_projects(
    request: Request,
):

    bootstrap = request.app.state.bootstrap

    return (
        bootstrap
        .get_projects_use_case
        .execute()
    )


@router.post("/{project_id}/execute")
def execute_pipeline(
    project_id: str,
    request: Request,
):

    bootstrap = request.app.state.bootstrap

    return (
        bootstrap
        .execute_pipeline_use_case
        .execute(
            project_id=project_id,
        )
    )


@router.post("/{project_id}/setup")
def execute_setup(
    project_id: str,
    setup_request: SetupApiRequest,
    request: Request,
):

    bootstrap = request.app.state.bootstrap

    setup_request = SetupRequest(
        project_id=project_id,
        environment_id=(
            setup_request.environment_id
        ),
        version=setup_request.version,
        revision=setup_request.revision,
        configuration=setup_request.configuration,
    )

    return (
        bootstrap
        .execute_setup_use_case
        .execute(
            setup_request,
        )
    )