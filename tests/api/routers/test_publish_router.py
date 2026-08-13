"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_publish_router.py
Descrição : Testes do endpoint de Publish.
--------------------------------------------------------------------
"""

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.api.routers.publish_router import (
    execute_publish,
    publish_execution_lock,
)

from app.models.publish.publish_batch_result import (
    PublishBatchResult,
)

from app.models.publish.publish_request import (
    PublishRequest,
)


def test_publish_deve_executar_quando_nao_houver_outra_execucao():
    """
    Deve executar o Publish quando não existir
    outra execução em andamento.
    """

    #
    # Arrange
    #

    request = MagicMock()

    request.app.state.bootstrap = (
        MagicMock()
    )

    expected_result = (
        PublishBatchResult()
    )

    request.app.state.bootstrap \
        .execute_publish_use_case \
        .execute.return_value = (
            expected_result
        )

    publish_request = PublishRequest(
        environment_id="production",
    )

    #
    # Act
    #

    result = execute_publish(
        publish_request=publish_request,
        request=request,
    )

    #
    # Assert
    #

    assert result is (
        expected_result
    )

    request.app.state.bootstrap \
        .execute_publish_use_case \
        .execute.assert_called_once_with(
            publish_request,
        )


def test_publish_deve_rejeitar_quando_ja_houver_execucao():
    """
    Deve rejeitar uma nova execução quando
    já existir um Publish em andamento.
    """

    #
    # Arrange
    #

    request = MagicMock()

    publish_request = PublishRequest(
        environment_id="production",
    )

    #
    # Simula uma execução em andamento.
    #

    assert (
        publish_execution_lock.try_acquire()
        is True
    )

    try:

        #
        # Act / Assert
        #

        with pytest.raises(
            HTTPException,
        ) as exception:

            execute_publish(
                publish_request=publish_request,
                request=request,
            )

        assert exception.value.status_code == 409

        assert exception.value.detail == {
            "status": "busy",
            "message": (
                "Já existe uma publicação "
                "em execução. Aguarde a "
                "conclusão da publicação atual."
            ),
        }

    finally:

        publish_execution_lock.release()


def test_publish_deve_liberar_lock_apos_execucao():
    """
    Deve liberar o Lock depois que o Publish
    terminar normalmente.
    """

    #
    # Arrange
    #

    request = MagicMock()

    request.app.state.bootstrap = (
        MagicMock()
    )

    publish_request = PublishRequest(
        environment_id="production",
    )

    #
    # Act
    #

    execute_publish(
        publish_request=publish_request,
        request=request,
    )

    #
    # Assert
    #

    assert (
        publish_execution_lock.try_acquire()
        is True
    )

    publish_execution_lock.release()


def test_publish_deve_liberar_lock_quando_ocorrer_erro():
    """
    Deve liberar o Lock mesmo quando o Publish
    lançar uma exceção.
    """

    #
    # Arrange
    #

    request = MagicMock()

    request.app.state.bootstrap \
        .execute_publish_use_case \
        .execute.side_effect = (
            RuntimeError(
                "Erro durante Publish.",
            )
        )

    publish_request = PublishRequest(
        environment_id="production",
    )

    #
    # Act / Assert
    #

    with pytest.raises(
        RuntimeError,
        match="Erro durante Publish.",
    ):

        execute_publish(
            publish_request=publish_request,
            request=request,
        )

    #
    # O Lock deve estar disponível novamente.
    #

    assert (
        publish_execution_lock.try_acquire()
        is True
    )

    publish_execution_lock.release()