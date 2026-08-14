"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_orchestrator.py
Descrição : Contrato responsável pela orquestração da geração
            de Setup.
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


class SetupOrchestrator(
    ABC,
):
    """
    Contrato responsável por coordenar
    a geração de um Setup.
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