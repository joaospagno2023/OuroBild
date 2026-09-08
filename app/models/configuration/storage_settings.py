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

    executions_path: Path | None = Field(
        default=None,
    )

    def model_post_init(
        self,
        __context,
    ) -> None:
        """
        Define o caminho padrão das execuções quando
        ele não estiver configurado explicitamente.
        """
        if self.executions_path is None:
            self.executions_path = (
                self.workspace_path
                / "data"
                / "logs"
                / "executions"
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