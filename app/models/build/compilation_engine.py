"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : compilation_engine.py
Descrição : Engines suportadas para compilação.
--------------------------------------------------------------------
"""

from enum import Enum


class CompilationEngine(
    str,
    Enum,
):
    """
    Engines suportadas para compilação.
    """

    DOTNET = "dotnet"

    MSBUILD = "msbuild"