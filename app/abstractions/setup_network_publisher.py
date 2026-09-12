"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_network_publisher.py
Descrição : Contrato para publicação de Setups na rede.
--------------------------------------------------------------------
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable

SetupNetworkPublishProgressCallback = Callable[[int, int, str, int], None]


from app.models.setup.setup_network_publish_result import (
    SetupNetworkPublishResult,
)


class SetupNetworkPublisher(ABC):
    """Define o contrato para publicação de um Setup na rede."""

    @abstractmethod
    def publish(
        self,
        project_id: str,
        source_path: Path,
        version: str,
        revision: int,
        progress_callback: SetupNetworkPublishProgressCallback | None = None,
    ) -> SetupNetworkPublishResult:
        """
        Publica a estrutura de Setup na rede.

        Args:
            project_id:
                Identificador do projeto.

            source_path:
                Pasta local da versão que será publicada.

            version:
                Versão do Setup sem a revisão.

            revision:
                Revisão do Setup.

        Returns:
            Resultado da publicação.
        """

        raise NotImplementedError