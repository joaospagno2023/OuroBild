"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : storage_settings.py
Descrição : Configurações de armazenamento da aplicação.
--------------------------------------------------------------------
"""

from pathlib import Path

from pydantic import BaseModel
from pydantic import Field


class StorageSettings(
    BaseModel,
):
    """
    Configurações de armazenamento.
    """

    workspace_path: Path = Field(
        default=Path.cwd(),
    )

    @property
    def config_path(
        self,
    ) -> Path:
        return self.workspace_path / "config"

    @property
    def data_path(
        self,
    ) -> Path:
        return self.workspace_path / "data"

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
    def reports_path(
        self,
    ) -> Path:
        return self.data_path / "reports"

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