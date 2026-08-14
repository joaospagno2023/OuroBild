"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : installer_service.py
Descrição : Contrato responsável pela geração de instaladores.
--------------------------------------------------------------------
"""

from abc import ABC
from abc import abstractmethod

from app.models.setup.setup_definition import (
    SetupDefinition,
)

from app.models.setup.setup_paths import (
    SetupPaths,
)

from app.models.setup.setup_request import (
    SetupRequest,
)

from app.models.setup.setup_result import (
    SetupResult,
)


class InstallerService(
    ABC,
):
    """
    Contrato responsável pela geração de um instalador.
    """

    @abstractmethod
    def install(
        self,
        request: SetupRequest,
        definition: SetupDefinition,
        paths: SetupPaths,
    ) -> SetupResult:
        """
        Gera o instalador a partir da solicitação,
        da definição do Setup e dos caminhos resolvidos.

        Args:
            request:
                Solicitação de geração do Setup.

            definition:
                Definição específica do Setup do projeto.

            paths:
                Caminhos físicos resolvidos para a geração.

        Returns:
            Resultado da geração do Setup.
        """

        raise NotImplementedError