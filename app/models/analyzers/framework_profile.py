"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : framework_profile.py
Descrição : Representa as informações do framework do projeto.
--------------------------------------------------------------------
"""

from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class FrameworkProfile:
    """
    Representa as informações do framework
    encontradas durante a análise.
    """

    target_framework: str = ""

    target_framework_version: str = ""

    sdk_style: bool = False

    tools_version: str = ""