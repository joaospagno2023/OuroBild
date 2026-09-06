"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : configuration_response.py
Descrição : Representa a configuração editável da aplicação.
--------------------------------------------------------------------
"""

from pydantic import BaseModel

from app.models.configuration.build_tools_settings import (
    BuildToolsSettings,
)
from app.models.configuration.logging_settings import (
    LoggingSettings,
)
from app.models.configuration.setup_settings import (
    SetupSettings,
)
from app.models.configuration.storage_settings import (
    StorageSettings,
)


class ConfigurationResponse(
    BaseModel,
):
    """
    Configuração operacional disponibilizada pela API.
    """

    application_name: str

    version: str

    log_level: str

    base_path: str

    installer_path: str

    publish_path: str

    storage: StorageSettings

    build_tools: BuildToolsSettings

    setup: SetupSettings

    logging: LoggingSettings