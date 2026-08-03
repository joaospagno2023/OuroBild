"""
--------------------------------------------------------------------
Projeto : OuroBuild
Arquivo : build_error.py
Descrição : Representa um erro encontrado durante uma Build.
--------------------------------------------------------------------
"""

from dataclasses import dataclass

from app.models.build.build_message import BuildMessage


@dataclass
class BuildError(BuildMessage):
    """
    Representa um erro de compilação.
    """