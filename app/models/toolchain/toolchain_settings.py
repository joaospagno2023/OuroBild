"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : toolchain_settings.py
Descrição : Configurações das ferramentas utilizadas pelo OuroBuild.
--------------------------------------------------------------------
"""

from pydantic import BaseModel

from app.models.toolchain.tool_settings import (
    ToolSettings,
)


class ToolchainSettings(BaseModel):
    """
    Configuração das ferramentas do sistema.
    """

    vswhere: ToolSettings

    msbuild: ToolSettings

    dotnet: ToolSettings

    advanced_installer: ToolSettings