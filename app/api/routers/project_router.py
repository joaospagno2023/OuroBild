"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_router.py
Descrição : Endpoints relacionados aos projetos.
--------------------------------------------------------------------
"""

from fastapi import APIRouter, Request

from app.models.pipeline.pipeline_execution_request import (
    PipelineExecutionRequest,
)

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.get("")
def get_projects(request: Request):

    bootstrap = request.app.state.bootstrap

    return bootstrap.get_projects_use_case.execute()


@router.post("/{project_id}/execute")
def execute_pipeline(
    project_id: str,
    request: Request,
    execution: PipelineExecutionRequest,
):

    bootstrap = request.app.state.bootstrap

    return bootstrap.execute_pipeline_use_case.execute(
        project_id=project_id,
        environment_id=execution.environment_id,
        version=execution.version,
        revision=execution.revision,
    )
