"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_setup_orchestrator.py
Descrição : Testes do contrato SetupOrchestrator.
--------------------------------------------------------------------
"""

from unittest.mock import MagicMock

from app.abstractions.setup_orchestrator import (
    SetupOrchestrator,
)

from app.models.setup.setup_request import (
    SetupRequest,
)

from app.models.setup.setup_result import (
    SetupResult,
)


def test_setup_orchestrator_deve_ser_abstrato():
    """
    Deve impedir a criação direta do contrato.
    """

    try:

        SetupOrchestrator()

        assert False, (
            "SetupOrchestrator não deveria "
            "poder ser instanciado."
        )

    except TypeError:

        assert True


def test_implementacao_deve_respeitar_contrato():
    """
    Uma implementação concreta deve conseguir
    implementar o contrato.
    """

    class FakeSetupOrchestrator(
        SetupOrchestrator,
    ):

        def execute(
            self,
            request: SetupRequest,
        ) -> SetupResult:

            return SetupResult(
                success=True,
                message="OK",
                project_id=request.project_id,
            )

    orchestrator = (
        FakeSetupOrchestrator()
    )

    request = SetupRequest(
        project_id="teste",
        environment_id="producao",
    )

    result = orchestrator.execute(
        request,
    )

    assert isinstance(
        result,
        SetupResult,
    )

    assert result.success is True

    assert result.project_id == (
        "teste"
    )