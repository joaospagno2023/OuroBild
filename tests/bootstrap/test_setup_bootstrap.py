"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : test_setup_bootstrap.py
Descrição : Testes da composição do Setup no Bootstrap.
--------------------------------------------------------------------
"""

from app.bootstrap import (
    Bootstrap,
)

from app.use_cases.execute_setup_use_case import (
    DefaultExecuteSetupUseCase,
)

from app.services.setup.setup_orchestrator import (
    DefaultSetupOrchestrator,
)


def test_bootstrap_deve_disponibilizar_setup_orchestrator():
    """
    O Bootstrap deve disponibilizar o SetupOrchestrator.
    """

    bootstrap = Bootstrap()

    assert isinstance(
        bootstrap.setup_orchestrator,
        DefaultSetupOrchestrator,
    )


def test_bootstrap_deve_disponibilizar_execute_setup_use_case():
    """
    O Bootstrap deve disponibilizar o Use Case
    de execução do Setup.
    """

    bootstrap = Bootstrap()

    assert isinstance(
        bootstrap.execute_setup_use_case,
        DefaultExecuteSetupUseCase,
    )