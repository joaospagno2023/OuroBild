"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : configuration_loader.py
Descrição : Responsável pelo carregamento das configurações da aplicação.
--------------------------------------------------------------------
"""

# Bibliotecas padrão
import json
from pathlib import Path

# Models
from app.models.configuration.app_settings import (
    AppSettings,
)

from app.models.configuration.database_settings import (
    DatabaseSettings,
)

# Abstrações
from app.abstractions.application_configuration_repository import (
    ApplicationConfigurationRepository,
)


class ConfigurationLoader:
    """
    Responsável pelo carregamento das configurações da aplicação.

    O arquivo settings.json contém somente as configurações
    necessárias para estabelecer a conexão inicial com o banco.

    As demais configurações são carregadas do SQL Server através
    do ApplicationConfigurationRepository.
    """

    def __init__(
        self,
        config_path: Path,
    ) -> None:
        """
        Inicializa o carregador de configurações.

        Args:
            config_path:
                Caminho da pasta config.
        """

        self._config_path = config_path

        self._configuration_repository: (
            ApplicationConfigurationRepository | None
        ) = None

    @property
    def config_path(
        self,
    ) -> Path:
        """
        Retorna o caminho da pasta de configuração.
        """

        return self._config_path

    def set_configuration_repository(
        self,
        repository: ApplicationConfigurationRepository,
    ) -> None:
        """
        Define o repository responsável pela configuração
        persistida no banco.

        Args:
            repository:
                Repository da configuração da aplicação.
        """

        if repository is None:
            raise ValueError(
                "ApplicationConfigurationRepository "
                "não foi informado."
            )

        self._configuration_repository = repository

    def load_database_settings(
        self,
    ) -> DatabaseSettings:
        """
        Carrega somente as configurações de banco do settings.json.

        O banco é a única configuração necessária antes da conexão
        inicial com o SQL Server.

        Returns:
            DatabaseSettings
        """

        file_path = (
            self._config_path
            / "settings.json"
        )

        if not file_path.exists():
            raise FileNotFoundError(
                f"Arquivo de configuração não encontrado: "
                f"{file_path}"
            )

        with file_path.open(
            mode="r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        database_data = data.get(
            "database"
        )

        if database_data is None:
            raise ValueError(
                "A seção 'database' não foi encontrada "
                "no settings.json."
            )

        return DatabaseSettings.model_validate(
            database_data,
        )

    def load_settings(
        self,
    ) -> AppSettings:
        """
        Carrega a configuração completa da aplicação.

        A configuração é obtida do SQL Server através do
        ApplicationConfigurationRepository.

        Returns:
            AppSettings

        Raises:
            RuntimeError:
                Quando o repository ainda não foi configurado.

            ValueError:
                Quando não existe configuração persistida no banco.
        """

        if self._configuration_repository is None:
            raise RuntimeError(
                "ApplicationConfigurationRepository "
                "não foi configurado no ConfigurationLoader."
            )

        settings = (
            self._configuration_repository.get()
        )

        if settings is None:
            raise ValueError(
                "A configuração da aplicação não foi "
                "encontrada no SQL Server."
            )

        return settings