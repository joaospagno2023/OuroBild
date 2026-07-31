"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : app_settings.py
Descrição : Modelo das configurações gerais da aplicação.
--------------------------------------------------------------------
"""

# Bibliotecas de terceiros
from pydantic import BaseModel


class AppSettings(BaseModel):
    """
    Representa as configurações gerais da aplicação.
    """

    application_name: str
    version: str
    log_level: str
    build_tools: BuildToolsSettings