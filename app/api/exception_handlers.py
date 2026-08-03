"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : exception_handlers.py
Descrição : Registro dos tratadores globais de exceção da API.
--------------------------------------------------------------------
"""

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions.ourobuild_exception import (
    OuroBuildException,
)
from app.exceptions.project_not_found_exception import (
    ProjectNotFoundException,
)


def register_exception_handlers(
    app: FastAPI,
) -> None:
    """
    Registra os tratadores globais de exceção.
    """

    @app.exception_handler(
        ProjectNotFoundException,
    )
    async def handle_project_not_found(
        request: Request,
        exception: ProjectNotFoundException,
    ):
        return JSONResponse(
            status_code=404,
            content={
                "message": str(
                    exception,
                ),
            },
        )

    @app.exception_handler(
        OuroBuildException,
    )
    async def handle_ourobuild_exception(
        request: Request,
        exception: OuroBuildException,
    ):
        return JSONResponse(
            status_code=400,
            content={
                "message": str(
                    exception,
                ),
            },
        )

    @app.exception_handler(
        Exception,
    )
    async def handle_unexpected_exception(
        request: Request,
        exception: Exception,
    ):
        return JSONResponse(
            status_code=500,
            content={
                "message": (
                    "Erro interno da aplicação."
                ),
            },
        )