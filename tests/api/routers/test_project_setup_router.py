"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_project_setup_router.py
Descrição : Testes do endpoint de geração de Setup.
--------------------------------------------------------------------
"""

from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routers.project_router import (
    router,
)

from app.models.setup.setup_result import (
    SetupResult,
)


def create_client():

    app = FastAPI()

    app.include_router(
        router,
    )

    bootstrap = MagicMock()

    bootstrap.execute_setup_use_case = (
        MagicMock()
    )

    bootstrap.execute_setup_use_case.execute.return_value = (
        SetupResult(
            success=True,
            message="Setup gerado com sucesso.",
            project_id="teste",
        )
    )

    app.state.bootstrap = (
        bootstrap
    )

    return (
        TestClient(app),
        bootstrap,
    )


def test_deve_executar_setup_do_projeto():

    client, bootstrap = (
        create_client()
    )

    response = client.post(
        "/projects/teste/setup",
        json={
            "environment_id": "producao",
            "version": "1.0.0",
            "revision": 1,
            "configuration": "Release",
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "success": True,
        "message": "Setup gerado com sucesso.",
        "project_id": "teste",
        "output_msi": None,
        "duration_seconds": 0.0,
    }

    bootstrap.execute_setup_use_case.execute.assert_called_once()


def test_deve_usar_project_id_da_url():

    client, bootstrap = (
        create_client()
    )

    client.post(
        "/projects/OuroNet/setup",
        json={
            "environment_id": "producao",
            "version": "2.0.0",
            "revision": 3,
            "configuration": "Release",
        },
    )

    request = (
        bootstrap
        .execute_setup_use_case
        .execute
        .call_args.args[0]
    )

    assert request.project_id == (
        "OuroNet"
    )

    assert request.environment_id == (
        "producao"
    )

    assert request.version == (
        "2.0.0"
    )

    assert request.revision == 3

    assert request.configuration == (
        "Release"
    )