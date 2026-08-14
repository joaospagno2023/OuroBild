"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_execute_setup_use_case.py
Descrição : Testes do ExecuteSetupUseCase.
--------------------------------------------------------------------
"""

from unittest.mock import MagicMock

import pytest

from app.models.setup.setup_request import (
    SetupRequest,
)

from app.models.setup.setup_result import (
    SetupResult,
)

from app.services.setup.setup_orchestrator import (
    DefaultSetupOrchestrator,
)

from app.use_cases.execute_setup_use_case import (
    DefaultExecuteSetupUseCase,
)


def create_request() -> SetupRequest:
    """
    Cria uma solicitação mínima de Setup.
    """

    return SetupRequest(
        project_id="teste",
        environment_id="producao",
        version="1.0.0",
        revision=1,
        configuration="Release",
    )


def create_result() -> SetupResult:
    """
    Cria um resultado mínimo de Setup.
    """

    return SetupResult(
        success=True,
        message="Setup gerado com sucesso.",
        project_id="teste",
    )


def test_deve_delegar_execucao_para_orchestrator():
    """
    Deve delegar a execução para o SetupOrchestrator.
    """

    request = create_request()

    expected_result = (
        create_result()
    )

    orchestrator = MagicMock(
        spec=DefaultSetupOrchestrator,
    )

    orchestrator.execute.return_value = (
        expected_result
    )

    use_case = (
        DefaultExecuteSetupUseCase(
            setup_orchestrator=orchestrator,
        )
    )

    result = use_case.execute(
        request,
    )

    assert result is expected_result

    orchestrator.execute.assert_called_once_with(
        request,
    )


def test_deve_rejeitar_request_nulo():
    """
    Deve rejeitar uma solicitação nula.
    """

    orchestrator = MagicMock(
        spec=DefaultSetupOrchestrator,
    )

    use_case = (
        DefaultExecuteSetupUseCase(
            setup_orchestrator=orchestrator,
        )
    )

    with pytest.raises(
        ValueError,
        match="SetupRequest não foi informado",
    ):
        use_case.execute(
            None,
        )

    orchestrator.execute.assert_not_called()


def test_deve_rejeitar_orchestrator_nulo():
    """
    Deve rejeitar um Orchestrator inexistente.
    """

    with pytest.raises(
        ValueError,
        match="SetupOrchestrator não foi informado",
    ):
        DefaultExecuteSetupUseCase(
            setup_orchestrator=None,
        )