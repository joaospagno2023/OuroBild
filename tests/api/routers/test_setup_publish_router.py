"""
Testes do endpoint de publicação em lote de Setups.
"""

from unittest.mock import MagicMock

from app.api.routers.setup_publish_router import (
    publish_setups,
)
from app.models.setup.setup_batch_publish_request import (
    SetupBatchPublishRequest,
)
from app.models.setup.setup_batch_publish_result import (
    SetupBatchPublishResult,
)


def test_deve_publicar_setups_em_lote():
    request = MagicMock()
    bootstrap = MagicMock()
    request.app.state.bootstrap = bootstrap

    expected = SetupBatchPublishResult(
        success=True,
        message="OK",
        execution_ids=["exec-1", "exec-2"],
        project_ids=["projeto-1", "projeto-2"],
    )

    bootstrap.publish_setups_use_case.execute.return_value = expected

    publish_request = SetupBatchPublishRequest(
        execution_ids=["exec-1", "exec-2"],
        version="10.4.7",
        revision=2,
    )

    result = publish_setups(
        publish_request=publish_request,
        request=request,
    )

    assert result is expected
    bootstrap.publish_setups_use_case.execute.assert_called_once_with(
        publish_request,
    )
