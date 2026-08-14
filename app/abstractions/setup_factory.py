"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_factory.py
Descrição : Contrato para criação do serviço responsável pela
            geração do Setup.
--------------------------------------------------------------------
"""

from abc import ABC
from abc import abstractmethod

from app.abstractions.installer_service import (
    InstallerService,
)

from app.models.setup.setup_engine import (
    SetupEngine,
)


class SetupFactory(
    ABC,
):
    """
    Contrato responsável por selecionar o serviço
    de geração de Setup.
    """

    @abstractmethod
    def create(
        self,
        engine: SetupEngine,
    ) -> InstallerService:
        """
        Cria o serviço responsável pela geração
        do Setup conforme o mecanismo informado.

        Args:
            engine:
                Mecanismo de geração do Setup.

        Returns:
            Implementação de InstallerService.
        """

        raise NotImplementedError