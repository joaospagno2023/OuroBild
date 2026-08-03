"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_warning.py
Descrição : Representa um warning encontrado durante uma Build.
--------------------------------------------------------------------
"""

from dataclasses import dataclass

from app.models.build.build_message import BuildMessage


@dataclass
class BuildWarning(BuildMessage):
    """
    Representa um warning de compilação.
    """