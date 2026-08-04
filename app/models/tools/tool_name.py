"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : tool_name.py
Descrição : Ferramentas suportadas pelo OuroBuild.
--------------------------------------------------------------------
"""

from enum import Enum


class ToolName(
    str,
    Enum,
):
    """
    Ferramentas conhecidas pela aplicação.
    """

    MSBUILD = "msbuild"

    DOTNET = "dotnet"

    ADVANCED_INSTALLER = "advanced_installer"

    VSWHERE = "vswhere"

    NUGET = "nuget"

    SIGNTOOL = "signtool"