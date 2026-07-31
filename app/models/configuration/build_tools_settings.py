"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_tools_settings.py
Descrição : Configurações das ferramentas utilizadas pela Engine.
--------------------------------------------------------------------
"""

from pathlib import Path

from pydantic import BaseModel


class BuildToolsSettings(BaseModel):
    """
    Configurações das ferramentas utilizadas pela Engine de Build.
    """

    msbuild_path: Path

    advanced_installer_path: Path

    robocopy_path: Path