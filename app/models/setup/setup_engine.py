"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : setup_engine.py
Descrição : Define os mecanismos disponíveis para geração de Setup.
--------------------------------------------------------------------
"""

from enum import Enum


class SetupEngine(
    str,
    Enum,
):
    """
    Define os mecanismos disponíveis
    para geração de Setup.
    """

    VISUAL_STUDIO = "visual_studio"

    ADVANCED_INSTALLER = "advanced_installer"