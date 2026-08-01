"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : environment_repository.py
Descrição : Contrato do repositório de ambientes.
--------------------------------------------------------------------
"""

from abc import ABC
from abc import abstractmethod

from app.models.environment.build_environment import (
    BuildEnvironment,
)


class EnvironmentRepository(ABC):
    """
    Contrato do repositório de ambientes.
    """

    @abstractmethod
    def get_all(
        self,
    ) -> list[BuildEnvironment]:
        """
        Retorna todos os ambientes cadastrados.
        """
        raise NotImplementedError

    @abstractmethod
    def get_by_id(
        self,
        environment_id: str,
    ) -> BuildEnvironment | None:
        """
        Retorna um ambiente pelo identificador.
        """
        raise NotImplementedError