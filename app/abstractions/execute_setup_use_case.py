"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : execute_setup_use_case.py
Descrição : Contrato para execução da geração de Setup.
--------------------------------------------------------------------
"""

from abc import ABC
from abc import abstractmethod

from app.models.setup.setup_request import (
    SetupRequest,
)

from app.models.setup.setup_result import (
    SetupResult,
)


class ExecuteSetupUseCase(
    ABC,
):
    """
    Contrato para execução da geração de Setup.
    """

    @abstractmethod
    def execute(
        self,
        request: SetupRequest,
    ) -> SetupResult:
        """
        Executa a geração do Setup.
        """

        raise NotImplementedError