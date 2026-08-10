"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : app_settings.py
Descrição : Representa as configurações gerais da aplicação.
--------------------------------------------------------------------
"""

from pathlib import Path

from pydantic import BaseModel

from app.models.configuration.build_tools_settings import (
    BuildToolsSettings,
)
from app.models.configuration.storage_settings import (
    StorageSettings,
)


class AppSettings(
    BaseModel,
):
    """
    Representa as configurações gerais da aplicação.
    """

    application_name: str

    version: str

    log_level: str

    #
    # Caminhos
    #

    base_path: Path

    installer_path: Path

    publish_path: Path

    #
    # Armazenamento
    #

    storage: StorageSettings

    #
    # Ferramentas
    #

    build_tools: BuildToolsSettings

    #
    # Diretórios derivados
    #

    @property
    def config_path(
        self,
    ) -> Path:
        return self.base_path / "config"

    @property
    def data_path(
        self,
    ) -> Path:
        return self.base_path / "data"

    @property
    def logs_path(
        self,
    ) -> Path:
        return self.data_path / "logs"

    @property
    def executions_path(
        self,
    ) -> Path:
        return self.logs_path / "executions"

    @property
    def reports_path(
        self,
    ) -> Path:
        return self.data_path / "reports"

    @property
    def cache_path(
        self,
    ) -> Path:
        return self.data_path / "cache"

    @property
    def metadata_path(
        self,
    ) -> Path:
        return self.data_path / "metadata"

    @property
    def backups_path(
        self,
    ) -> Path:
        return self.data_path / "backups"

    @property
    def temp_path(
        self,
    ) -> Path:
        return self.data_path / "temp"