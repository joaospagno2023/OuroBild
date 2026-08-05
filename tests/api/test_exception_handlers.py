"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_exception_handlers.py
Descrição : Testes dos tratadores globais de exceção.
--------------------------------------------------------------------
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.exception_handlers import (
    register_exception_handlers,
)
from app.exceptions.ourobuild_exception import (
    OuroBuildException,
)
from app.models.api.api_error_code import (
    ErrorCode,
)


def create_test_app() -> TestClient:
    """
    Cria uma aplicação temporária apenas para testes.
    """

    app = FastAPI()

    register_exception_handlers(app)

    @app.get("/ourobuild-error")
    def ourobuild_error():
        raise OuroBuildException(
                status_code=404,
                code=ErrorCode.PROJECT_NOT_FOUND,
                message="Projeto não encontrado.",
            )

    @app.get("/unexpected-error")
    def unexpected_error():
        raise Exception("Erro inesperado")

    return TestClient(
        app,
        raise_server_exceptions=False,
    )


def test_should_handle_ourobuild_exception():
    """
    Deve tratar uma OuroBuildException.
    """

    client = create_test_app()

    response = client.get("/ourobuild-error")

    assert response.status_code == 404

    body = response.json()

    assert body["code"] == ErrorCode.PROJECT_NOT_FOUND

    assert body["message"] == "Projeto não encontrado."


def test_should_handle_unexpected_exception():
    """
    Deve tratar uma exceção inesperada.
    """

    client = create_test_app()

    response = client.get("/unexpected-error")

    assert response.status_code == 500

    body = response.json()

    assert body["code"] == ErrorCode.INTERNAL_ERROR

    assert body["message"] == "Erro interno da aplicação."