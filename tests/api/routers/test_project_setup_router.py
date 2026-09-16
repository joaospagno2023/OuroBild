"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_project_setup_router.py
Descrição : Testes do endpoint de execução assíncrona da Pipeline.
--------------------------------------------------------------------
"""

from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies.current_user import (
    get_current_user,
)
from app.api.routers import project_router
from app.models.execution.pipeline_execution_response import (
    PipelineExecutionResponse,
)
from app.models.execution.pipeline_execution_state import (
    PipelineExecutionPhase,
    PipelineExecutionStatus,
)
from app.models.setup.setup_publication_mode import (
    SetupPublicationMode,
)
from app.utils.pipeline_logger import (
    PipelineLogger,
)


def create_client():
    """Cria a aplicação isolada e seus colaboradores simulados."""

    app = FastAPI()
    app.include_router(project_router.router)

    bootstrap = MagicMock()
    bootstrap.permission_service.has_permission.return_value = True

    execution_service = MagicMock()
    execution_service.start.return_value = PipelineExecutionResponse(
        execution_id="EXECUTION-001",
        project_id="teste",
        status=PipelineExecutionStatus.PENDING,
        phase=PipelineExecutionPhase.PIPELINE,
        current_step=None,
        current_step_index=0,
        total_steps=0,
        progress_percent=0,
        message="Execução agendada.",
        started_at=None,
        finished_at=None,
        elapsed_seconds=0.0,
        success=None,
        failed_step=None,
    )

    app.state.bootstrap = bootstrap
    app.dependency_overrides[get_current_user] = (
        lambda: MagicMock(id=1)
    )

    return (
        TestClient(app),
        bootstrap,
        execution_service,
    )


def test_deve_iniciar_execucao_assincrona_do_projeto():
    """Deve aceitar a solicitação e retornar a execução pendente."""

    client, bootstrap, execution_service = create_client()

    with (
        patch.object(
            project_router,
            "get_pipeline_execution_service",
            return_value=execution_service,
        ),
        patch.object(PipelineLogger, "info"),
    ):
        response = client.post(
            "/projects/teste/execute",
            json={
                "environment_id": "producao",
                "version": "1.0.0",
                "revision": 1,
            },
        )

    assert response.status_code == 202
    assert response.json() == {
        "execution_id": "EXECUTION-001",
        "project_id": "teste",
        "status": "pending",
        "phase": "pipeline",
        "current_step": None,
        "current_step_index": 0,
        "total_steps": 0,
        "progress_percent": 0,
        "message": "Execução agendada.",
        "started_at": None,
        "finished_at": None,
        "elapsed_seconds": 0.0,
        "success": None,
        "failed_step": None,
    }

    execution_service.start.assert_called_once_with(
        execute_pipeline_use_case=(
            bootstrap.execute_pipeline_use_case
        ),
        project_id="teste",
        environment_id="producao",
        version="1.0.0",
        revision=1,
        publication_mode=SetupPublicationMode.LOCAL,
    )


def test_deve_usar_project_id_e_publicacao_da_solicitacao():
    """Deve encaminhar à fila os dados recebidos pela rota."""

    client, bootstrap, execution_service = create_client()

    with (
        patch.object(
            project_router,
            "get_pipeline_execution_service",
            return_value=execution_service,
        ),
        patch.object(PipelineLogger, "info"),
    ):
        response = client.post(
            "/projects/OuroNet/execute",
            json={
                "environment_id": "producao",
                "version": "2.0.0",
                "revision": 3,
                "publication_mode": "network",
            },
        )

    assert response.status_code == 202

    request = execution_service.start.call_args.kwargs

    assert request["execute_pipeline_use_case"] is (
        bootstrap.execute_pipeline_use_case
    )
    assert request["project_id"] == "OuroNet"
    assert request["environment_id"] == "producao"
    assert request["version"] == "2.0.0"
    assert request["revision"] == 3
    assert request["publication_mode"] is (
        SetupPublicationMode.NETWORK
    )
