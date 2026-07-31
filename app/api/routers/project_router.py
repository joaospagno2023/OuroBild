"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : project_router.py
Descrição : Endpoints relacionados aos projetos.
--------------------------------------------------------------------
"""

from fastapi import APIRouter, Request

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.get("")
def get_projects(request: Request):

    bootstrap = request.app.state.bootstrap

    return bootstrap.get_projects_use_case.execute()