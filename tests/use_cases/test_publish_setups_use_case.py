"""
Testes do caso de uso de publicação em lote de Setups.
"""

from pathlib import Path
from unittest.mock import MagicMock

from app.models.setup.setup_batch_publish_request import (
    SetupBatchPublishRequest,
)
from app.models.setup.setup_network_publish_result import (
    SetupNetworkPublishResult,
)
from app.use_cases.publish_setups_use_case import (
    DefaultPublishSetupsUseCase,
)


def create_use_case(
    executions,
    output_root: Path,
    publication_result: SetupNetworkPublishResult | None = None,
):
    repository = MagicMock()
    repository.get_by_execution_id.side_effect = (
        lambda execution_id: executions.get(execution_id)
    )

    publisher = MagicMock()

    if publication_result is not None:
        publisher.publish.return_value = publication_result

    settings = MagicMock()
    settings.setup.output_root = output_root

    use_case = DefaultPublishSetupsUseCase(
        pipeline_execution_repository=repository,
        setup_network_publisher=publisher,
        settings=settings,
    )

    return (
        use_case,
        repository,
        publisher,
    )


def test_publica_somente_quando_todas_execucoes_estao_concluidas(
    tmp_path,
):
    source = tmp_path / "10.4.7.2"
    (source / "Cliente").mkdir(parents=True)
    (source / "Server").mkdir()

    executions = {
        "exec-1": {
            "execution_id": "exec-1",
            "project_id": "client-1",
            "status": "completed",
            "success": True,
            "version": "10.4.7",
        },
        "exec-2": {
            "execution_id": "exec-2",
            "project_id": "server-1",
            "status": "completed",
            "success": True,
            "version": "10.4.7",
        },
    }

    publication = SetupNetworkPublishResult(
        success=True,
        message="OK",
        project_id="batch",
        source_path=source,
        destination_path=tmp_path / "network",
    )

    use_case, _, publisher = create_use_case(
        executions,
        tmp_path,
        publication,
    )

    result = use_case.execute(
        SetupBatchPublishRequest(
            execution_ids=["exec-1", "exec-2"],
            version="10.4.7",
            revision=2,
        )
    )

    assert result.success is True
    assert result.project_ids == [
        "client-1",
        "server-1",
    ]
    publisher.publish.assert_called_once_with(
        project_id="batch",
        source_path=source,
        version="10.4.7",
        revision=2,
    )


def test_nao_publica_quando_uma_execucao_falhou(
    tmp_path,
):
    source = tmp_path / "10.4.7.2"
    source.mkdir(parents=True)

    executions = {
        "exec-1": {
            "execution_id": "exec-1",
            "project_id": "client-1",
            "status": "completed",
            "success": True,
            "version": "10.4.7",
        },
        "exec-2": {
            "execution_id": "exec-2",
            "project_id": "server-1",
            "status": "failed",
            "success": False,
            "version": "10.4.7",
        },
    }

    use_case, _, publisher = create_use_case(
        executions,
        tmp_path,
    )

    result = use_case.execute(
        SetupBatchPublishRequest(
            execution_ids=["exec-1", "exec-2"],
            version="10.4.7",
            revision=2,
        )
    )

    assert result.success is False
    assert "não está concluída" in result.message
    publisher.publish.assert_not_called()


def test_nao_publica_quando_uma_execucao_ainda_esta_em_andamento(
    tmp_path,
):
    source = tmp_path / "10.4.7.2"
    source.mkdir(parents=True)

    executions = {
        "exec-1": {
            "execution_id": "exec-1",
            "project_id": "client-1",
            "status": "completed",
            "success": True,
            "version": "10.4.7",
        },
        "exec-2": {
            "execution_id": "exec-2",
            "project_id": "server-1",
            "status": "running",
            "success": None,
            "version": "10.4.7",
        },
    }

    use_case, _, publisher = create_use_case(
        executions,
        tmp_path,
    )

    result = use_case.execute(
        SetupBatchPublishRequest(
            execution_ids=["exec-1", "exec-2"],
            version="10.4.7",
            revision=2,
        )
    )

    assert result.success is False
    assert "ainda não está concluída" in result.message
    publisher.publish.assert_not_called()


def test_nao_publica_quando_execucao_nao_existe(
    tmp_path,
):
    use_case, _, publisher = create_use_case(
        {},
        tmp_path,
    )

    result = use_case.execute(
        SetupBatchPublishRequest(
            execution_ids=["exec-inexistente"],
            version="10.4.7",
            revision=2,
        )
    )

    assert result.success is False
    assert "Execução não encontrada" in result.message
    publisher.publish.assert_not_called()
