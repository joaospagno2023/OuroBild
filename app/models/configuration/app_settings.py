"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : app_settings.py
Descrição : Modelo das configurações gerais da aplicação.
--------------------------------------------------------------------
"""

from pathlib import Path

from pydantic import BaseModel

from app.models.configuration.build_tools_settings import (
    BuildToolsSettings,
)


class AppSettings(BaseModel):
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
    # Ferramentas
    #

    build_tools: BuildToolsSettings