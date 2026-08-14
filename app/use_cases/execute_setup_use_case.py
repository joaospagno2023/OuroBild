"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : execute_setup_use_case.py
Descrição : Caso de uso responsável pela geração de Setup.
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

from app.services.setup.setup_orchestrator import (
    DefaultSetupOrchestrator,
)


class DefaultExecuteSetupUseCase(
    ExecuteSetupUseCase,
):
    """
    Implementação do caso de uso de geração de Setup.

    Responsabilidade:

    - Receber a solicitação de Setup.
    - Delegar a execução para o SetupOrchestrator.
    - Retornar o resultado da operação.
    """

    def __init__(
        self,
        setup_orchestrator: DefaultSetupOrchestrator,
    ) -> None:
        """
        Inicializa o caso de uso.
        """

        if setup_orchestrator is None:

            raise ValueError(
                "SetupOrchestrator não foi informado."
            )

        self.__setup_orchestrator = (
            setup_orchestrator
        )

    def execute(
        self,
        request: SetupRequest,
    ) -> SetupResult:
        """
        Executa a geração do Setup.
        """

        if request is None:

            raise ValueError(
                "SetupRequest não foi informado."
            )

        return self.__setup_orchestrator.execute(
            request,
        )