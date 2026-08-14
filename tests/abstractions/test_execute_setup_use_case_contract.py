"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_execute_setup_use_case.py
Descrição : Testes do contrato ExecuteSetupUseCase.
--------------------------------------------------------------------
"""

from app.abstractions.execute_setup_use_case import (
    ExecuteSetupUseCase,
)

from app.models.setup.setup_request import (
    SetupRequest,
)

from app.models.setup.setup_result import (
    SetupResult,
)


def test_execute_setup_use_case_deve_ser_abstrato():
    """
    O contrato não deve poder ser instanciado diretamente.
    """

    try:

        ExecuteSetupUseCase()

        assert False

    except TypeError:

        assert True


def test_implementacao_deve_respeitar_contrato():
    """
    Uma implementação concreta deve conseguir
    executar o contrato.
    """

    class FakeExecuteSetupUseCase(
        ExecuteSetupUseCase,
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

    use_case = (
        FakeExecuteSetupUseCase()
    )

    request = SetupRequest(
        project_id="teste",
        environment_id="producao",
    )

    result = use_case.execute(
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