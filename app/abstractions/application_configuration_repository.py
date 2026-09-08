"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : application_configuration_repository.py
Descrição : Define o contrato do repositório de configuração.
--------------------------------------------------------------------
"""

from abc import (
    ABC,
    abstractmethod,
)

from app.models.configuration.app_settings import (
    AppSettings,
)


class ApplicationConfigurationRepository(
    ABC,
):
    """
    Define as operações necessárias para a configuração
    persistida da aplicação.
    """

    @abstractmethod
    def get(self) -> AppSettings | None:
        """
        Retorna a configuração persistida.

        Returns:
            Configuração encontrada ou None.
        """

        raise NotImplementedError

    @abstractmethod
    def save(
        self,
        settings: AppSettings,
    ) -> AppSettings:
        """
        Persiste a configuração da aplicação.

        Args:
            settings: Configuração completa da aplicação.

        Returns:
            Configuração persistida.
        """

        raise NotImplementedError