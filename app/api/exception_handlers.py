"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : exception_handlers.py
Descrição : Registro dos tratadores globais de exceção da API.
--------------------------------------------------------------------
"""

import traceback

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions.ourobuild_exception import (
    OuroBuildException,
)

from app.models.api.api_error_response import (
    ApiErrorResponse,
)

from app.models.api.api_error_code import (
    ErrorCode,
)


def register_exception_handlers(
    app: FastAPI,
) -> None:
    """
    Registra os tratadores globais de exceção.
    """

    @app.exception_handler(
        OuroBuildException,
    )
    async def handle_ourobuild_exception(
        request: Request,
        exception: OuroBuildException,
    ):
        #
        # Durante o desenvolvimento, imprime o erro.
        #

        traceback.print_exc()

        return JSONResponse(

            status_code=exception.status_code,

            content=ApiErrorResponse(

                code=exception.code,

                message=exception.message,

            ).model_dump(),

        )

    @app.exception_handler(
        Exception,
    )
    async def handle_unexpected_exception(
        request: Request,
        exception: Exception,
    ):
        #
        # Durante o desenvolvimento, deixa o Uvicorn
        # exibir o stack trace completo.
        #

        traceback.print_exc()

        raise exception

        #
        # Em produção, substituir pelo código abaixo:
        #
        # return JSONResponse(
        #
        #     status_code=500,
        #
        #     content=ApiErrorResponse(
        #
        #         code=ErrorCode.INTERNAL_ERROR,
        #
        #         message="Erro interno da aplicação.",
        #
        #     ).model_dump(),
        #
        # )